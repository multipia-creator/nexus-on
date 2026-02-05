from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from shared.fix_pr import create_fix_pr_from_hold, FixPRResult
from shared.github_actions import dispatch_and_wait, GitHubWorkflowRun
from shared.github_comments import comment_on_pr
from shared.github_pr_ops import (
    add_labels,
    set_assignees,
    merge_pr,
    enable_auto_merge,
)
from shared.merge_error import classify_merge_failure
from shared.cooldown_store import cleanup_expired, set_cooldown_key
from shared.runbooks import get_runbook
from shared.settings import settings


@dataclass
class FixPRCIResult:
    ok: bool
    pr_url: Optional[str]
    run: Optional[GitHubWorkflowRun]
    comment_url: Optional[str]
    error: Optional[str] = None


def _parse_pr_number(pr_url: str) -> Optional[int]:
    try:
        parts = pr_url.rstrip("/").split("/")
        if "pull" in parts:
            idx = parts.index("pull")
            return int(parts[idx + 1])
        return int(parts[-1])
    except Exception:
        return None


def create_fix_pr_and_ci(
    msg: Dict[str, Any],
    failure_code: str,
    provider_override: Optional[str] = None,
    apply_patches: bool = False,
    allowlist: Optional[list[str]] = None,
    max_files: int = 5,
    max_lines: int = 400,
) -> FixPRCIResult:
    """Create an AutoFix PR, run CI, and optionally merge.

    This is the operational glue for the supervisor pipeline.
    """

    pr_res: FixPRResult = create_fix_pr_from_hold(
        msg,
        failure_code,
        provider_override=provider_override,
        apply_patches=apply_patches,
        allowlist=allowlist,
        max_files=max_files,
        max_lines=max_lines,
    )

    if not pr_res.ok or not pr_res.pr or not pr_res.pr.pr_url or not pr_res.pr.branch:
        return FixPRCIResult(False, pr_res.pr.pr_url if pr_res.pr else None, None, None, pr_res.error or "fix_pr failed")

    pr_url = pr_res.pr.pr_url
    pr_num = _parse_pr_number(pr_url)
    rb = get_runbook(failure_code) or ""

    # governance knobs
    assignees = [a.strip() for a in (getattr(settings, "autofix_assignees", "") or "").split(",") if a.strip()]
    label_ready = getattr(settings, "autofix_label_ready", "autofix-ready")
    label_failed = getattr(settings, "autofix_label_failed", "autofix-failed")
    label_queued = getattr(settings, "autofix_label_queued", "autofix-queued")

    retry_once = bool(getattr(settings, "autofix_ci_retry_once", True))
    auto_merge = bool(getattr(settings, "autofix_auto_merge", False))
    merge_method = getattr(settings, "autofix_merge_method", "squash") or "squash"
    merge_strategy = (getattr(settings, "autofix_merge_strategy", "direct") or "direct").strip().lower()
    auto_merge_fallback = bool(getattr(settings, "autofix_auto_merge_fallback", True))

    label_need_permission = getattr(settings, "autofix_label_need_permission", "autofix-need-permission")
    label_need_rebase = getattr(settings, "autofix_label_need_rebase", "autofix-need-rebase")
    label_need_checks = getattr(settings, "autofix_label_need_checks", "autofix-need-checks")
    label_need_merge_queue = getattr(settings, "autofix_label_need_merge_queue", "autofix-need-merge-queue")

    cooldown_minutes = int(getattr(settings, "autofix_failure_cooldown_minutes", 30) or 30)
    cooldown_store_path = getattr(settings, "autofix_cooldown_store_path", "/tmp/nexus_cooldown_store.json")
    cooldown_key_mode = (getattr(settings, "autofix_cooldown_key_mode", "repo_pr_class") or "repo_pr_class").strip().lower()

    try:
        cleanup_expired(cooldown_store_path)
    except Exception:
        pass

    repo_id = (os.getenv("AUTOFIX_GITHUB_REPO") or os.getenv("GITHUB_REPOSITORY") or "").strip() or "repo"
    workflow_id = (os.getenv("GITHUB_WORKFLOW") or os.getenv("GITHUB_WORKFLOW_REF") or "").strip() or "wf"

    if pr_num and assignees:
        set_assignees(pr_num, assignees)

    # --- CI dispatch
    run = dispatch_and_wait(branch=pr_res.pr.branch, inputs={"failure_code": failure_code})
    if (not run.ok or run.conclusion not in (None, "success")) and retry_once:
        run2 = dispatch_and_wait(branch=pr_res.pr.branch, inputs={"failure_code": failure_code, "retry": "1"})
        if run2.ok:
            run = run2

    ok = bool(run.ok and run.status == "completed" and (run.conclusion in (None, "success")))

    # --- PR comment
    comment_url = None
    if pr_num:
        apply_flag = bool(getattr(pr_res, "applied_patches", False))
        cf = int(getattr(pr_res, "changed_files", 0) or 0)
        cl = int(getattr(pr_res, "changed_lines", 0) or 0)

        body = f"""NEXUS AutoFix CI result

- failure_code: `{failure_code}`
- runbook: {rb}
- workflow_run: {run.run_url or "(unknown)"}
- status: `{run.status}`
- conclusion: `{run.conclusion}`
- note: {run.error or "ok"}
- patches_applied: `{apply_flag}`
- changed_files: `{cf}`
- changed_lines: `{cl}`
"""
        c = comment_on_pr(pr_num, body)
        comment_url = c.url if c.ok else None

    # --- labels
    if pr_num:
        add_labels(pr_num, [label_ready] if ok else [label_failed])

    # --- optional merge
    if pr_num and ok and auto_merge:
        mres = None
        if merge_strategy == "auto":
            mres = enable_auto_merge(pr_num, method=merge_method)
            if mres.ok:
                add_labels(pr_num, [label_queued])
            elif auto_merge_fallback:
                mres = merge_pr(pr_num, method=merge_method)
        else:
            mres = merge_pr(pr_num, method=merge_method)
            if (not mres.ok) and auto_merge_fallback:
                cls0 = classify_merge_failure(getattr(mres, "status_code", None), getattr(mres, "message", "") or "")
                if cls0.code == "merge_queue_required":
                    mres = enable_auto_merge(pr_num, method=merge_method)
                    if mres.ok:
                        add_labels(pr_num, [label_queued])

        if mres is not None and (not mres.ok):
            cls = classify_merge_failure(getattr(mres, "status_code", None), getattr(mres, "message", "") or "")

            # label routing
            if cls.code == "permission_denied":
                add_labels(pr_num, [label_need_permission])
            elif cls.code in ("merge_conflict",):
                add_labels(pr_num, [label_need_rebase])
            elif cls.code in ("required_checks_missing",):
                add_labels(pr_num, [label_need_checks])
            elif cls.code in ("merge_queue_required",):
                add_labels(pr_num, [label_need_merge_queue])

            # cooldown
            cd_key = str(pr_num)
            if cooldown_key_mode == "repo_pr":
                cd_key = f"{repo_id}:{workflow_id}:{pr_num}"
            elif cooldown_key_mode == "repo_pr_class":
                cd_key = f"{repo_id}:{workflow_id}:{pr_num}:{cls.code}"
            set_cooldown_key(cooldown_store_path, cd_key, cooldown_minutes, cls.code)

    return FixPRCIResult(ok, pr_url, run, comment_url, None if ok else (run.error or f"CI not successful: {run.conclusion}"))
