from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests

from shared.settings import settings
from shared.logging_utils import get_logger

logger = get_logger("github_actions")


@dataclass
class GitHubWorkflowRun:
    ok: bool
    run_id: Optional[int] = None
    run_url: Optional[str] = None
    status: Optional[str] = None
    conclusion: Optional[str] = None
    error: Optional[str] = None


def _headers() -> Dict[str, str]:
    token = getattr(settings, "github_token", "") or ""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "nexus-supervisor",
    }


def _base() -> str:
    return (getattr(settings, "github_api_base", "") or "https://api.github.com").rstrip("/")


def _repo() -> str:
    return getattr(settings, "github_repo", "") or ""


def _require() -> Optional[str]:
    if not _repo():
        return "GITHUB_REPO not set"
    if not getattr(settings, "github_token", ""):
        return "GITHUB_TOKEN not set"
    wf = getattr(settings, "github_workflow", "") or ""
    if not wf:
        return "GITHUB_WORKFLOW not set"
    return None


def dispatch_workflow(workflow: str, ref: str, inputs: Optional[Dict[str, Any]] = None) -> Optional[str]:
    url = f"{_base()}/repos/{_repo()}/actions/workflows/{workflow}/dispatches"
    payload: Dict[str, Any] = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs
    r = requests.post(url, headers=_headers(), json=payload, timeout=20)
    if 200 <= r.status_code < 300:
        return None
    logger.warning({"event":"GITHUB_DISPATCH_NON2XX","status":r.status_code,"text":r.text[:800]})
    return f"dispatch failed: {r.status_code}"


def find_latest_run_id(workflow: str, branch: str, created_after_epoch: float) -> Optional[int]:
    url = f"{_base()}/repos/{_repo()}/actions/workflows/{workflow}/runs"
    params = {"branch": branch, "event": "workflow_dispatch", "per_page": 10}
    r = requests.get(url, headers=_headers(), params=params, timeout=20)
    if not (200 <= r.status_code < 300):
        logger.warning({"event":"GITHUB_LIST_RUNS_NON2XX","status":r.status_code,"text":r.text[:800]})
        return None
    runs = (r.json() or {}).get("workflow_runs") or []
    # pick the newest that looks recent
    for run in runs:
        # created_at: ISO string; rough fallback by assuming list is sorted desc
        return int(run.get("id"))
    return None


def get_run(run_id: int) -> GitHubWorkflowRun:
    url = f"{_base()}/repos/{_repo()}/actions/runs/{run_id}"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        j = r.json() or {}
        return GitHubWorkflowRun(True, run_id, j.get("html_url"), j.get("status"), j.get("conclusion"), None)
    logger.warning({"event":"GITHUB_GET_RUN_NON2XX","status":r.status_code,"text":r.text[:800]})
    return GitHubWorkflowRun(False, run_id, None, None, None, f"get_run failed: {r.status_code}")


def dispatch_and_wait(branch: str, inputs: Optional[Dict[str, Any]] = None) -> GitHubWorkflowRun:
    err = _require()
    if err:
        return GitHubWorkflowRun(False, None, None, None, None, err)
    wf = getattr(settings, "github_workflow", "") or ""
    ref = branch
    # allow overriding ref (for repos that require default branch dispatch)
    ref_override = getattr(settings, "github_workflow_ref", "") or ""
    if ref_override:
        ref = ref_override

    t0 = time.time()
    derr = dispatch_workflow(wf, ref=ref, inputs=inputs)
    if derr:
        return GitHubWorkflowRun(False, None, None, None, None, derr)

    # try to find run id
    run_id = None
    for _ in range(10):
        run_id = find_latest_run_id(wf, branch=branch, created_after_epoch=t0 - 5)
        if run_id:
            break
        time.sleep(1.0)

    if not run_id:
        return GitHubWorkflowRun(False, None, None, None, None, "could not resolve workflow run id")

    wait_s = int(getattr(settings, "github_actions_wait_seconds", 60))
    poll_s = int(getattr(settings, "github_actions_poll_seconds", 3))
    deadline = time.time() + max(5, wait_s)

    last = None
    while time.time() < deadline:
        last = get_run(run_id)
        if not last.ok:
            return last
        if last.status in ("completed",):
            return last
        time.sleep(max(1, poll_s))

    # timeout
    if last and last.ok:
        last.error = "timeout waiting for workflow completion"
        return last
    return GitHubWorkflowRun(False, run_id, None, None, None, "timeout")
