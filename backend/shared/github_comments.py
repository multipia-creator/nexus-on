from __future__ import annotations

import os
import difflib
import re
import time
import random
import datetime

def _parse_fields_from_body(body: str) -> dict:
    # Extract a small set of stable fields from the Status table.
    fields = {}
    for line in (body or "").splitlines():
        line = line.strip()
        if line.startswith("| conclusion |"):
            fields["conclusion"] = line.split("|")[2].strip()
        elif line.startswith("| gate |"):
            fields["gate"] = line.split("|")[2].strip()
        elif line.startswith("| checks |"):
            fields["checks"] = line.split("|")[2].strip()
        elif line.startswith("| missing_contexts |"):
            fields["missing_contexts"] = line.split("|")[2].strip()
        elif line.startswith("| required_contexts |"):
            fields["required_contexts"] = line.split("|")[2].strip()
    # Next actions summary (order-insensitive)
    actions = _parse_next_actions(body)
    if actions:
        fields["next_actions"] = "|".join(sorted(actions))
    return fields


def _build_changelog(prev: dict, cur: dict) -> str:
    if not prev:
        return "- first report"
    changes = []
    keys = ["conclusion", "gate", "checks", "missing_contexts", "required_contexts", "next_actions"]
    for k in keys:
        pv = (prev or {}).get(k, "")
        cv = (cur or {}).get(k, "")
        if pv != cv:
            changes.append(f"- {k}: `{pv}` -> `{cv}`")
    if not changes:
        return "- no field-level changes"
    return "\n".join(changes)

def _parse_next_actions(body: str) -> list:
    lines = (body or "").splitlines()
    actions = []
    in_actions = False
    for ln in lines:
        s = (ln or "").strip()
        if s.lower().startswith("### next actions"):
            in_actions = True
            continue
        if in_actions and s.startswith("### "):
            break
        if in_actions and s.startswith("- "):
            actions.append(s[2:].strip())
    # normalize
    actions = [a for a in actions if a]
    return actions

def _parse_runbooks(body: str) -> list:
    lines = (body or "").splitlines()
    urls = []
    in_rb = False
    for ln in lines:
        s = (ln or "").strip()
        if s.lower().startswith("### runbooks"):
            in_rb = True
            continue
        if in_rb and s.startswith("### "):
            break
        if in_rb and s.startswith("- "):
            urls.append(s[2:].strip())
    return [u for u in urls if u]


def _match_runbook(body: str, keyword: str) -> str:
    kw = (keyword or "").strip().lower()
    if not kw:
        return ""
    for u in _parse_runbooks(body):
        if kw in u.lower():
            return u
    return ""

def _get_top_failing_check(pr_number: int) -> tuple[str, str]:
    """Best-effort: return (check_name, check_url).
    Strategy:
    - Use list_check_runs_for_ref on PR head SHA when available (preferred).
    - Fallback to empty if not retrievable.
    """
    try:
        # Fetch PR to get head sha
        pr_url = f"{_base()}/repos/{_repo()}/pulls/{int(pr_number)}"
        pr = requests.get(pr_url, headers=_headers(), timeout=20)
        if not (200 <= pr.status_code < 300):
            return ("", "")
        sha = ((pr.json() or {}).get("head") or {}).get("sha") or ""
        if not sha:
            return ("", "")
        runs_url = f"{_base()}/repos/{_repo()}/commits/{sha}/check-runs"
        r = requests.get(runs_url, headers={**_headers(), "Accept":"application/vnd.github+json"}, timeout=20)
        if not (200 <= r.status_code < 300):
            return ("", "")
        runs = (r.json() or {}).get("check_runs") or []
        # find first failing in order of started_at desc
        failing = []
        for cr in runs:
            concl = (cr.get("conclusion") or "").lower()
            status = (cr.get("status") or "").lower()
            name = cr.get("name") or ""
            html = cr.get("html_url") or ""
            if concl in ("failure", "timed_out", "action_required", "cancelled") or (status == "completed" and concl and concl != "success"):
                failing.append((cr.get("started_at") or "", name, html, concl))
        failing.sort(reverse=True, key=lambda x: x[0] or "")
        if failing:
            _, name, html, concl = failing[0]
            return (f"{name} ({concl})", html)
        return ("", "")
    except Exception:
        return ("", "")






def _parse_checks_failing(checks_field: str) -> int:
    # expects: "X/Y ok (Z failing)" but be defensive
    m = re.search(r"\((\d+)\s+failing\)", checks_field or "")
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return 0
    return 0


def _transition_summary(prev: dict, cur: dict) -> str:
    if not prev:
        return "FIRST: first report"
    pv = (prev.get("conclusion") or "").lower()
    cv = (cur.get("conclusion") or "").lower()

    def norm(x: str) -> str:
        if "success" in x:
            return "success"
        if "failure" in x:
            return "failure"
        if "neutral" in x:
            return "neutral"
        if "cancel" in x:
            return "cancelled"
        return x or "unknown"

    # conclusion transition
    if pv != cv and pv and cv:
        return f"CONCLUSION: {norm(pv)} -> {norm(cv)}"

    # checks failing delta
    pf = _parse_checks_failing(prev.get("checks",""))
    cf = _parse_checks_failing(cur.get("checks",""))
    if pf != cf:
        if cf < pf:
            return f"CHECKS: improved ({pf} -> {cf} failing)"
        return f"CHECKS: worsened ({pf} -> {cf} failing)"

    # missing contexts delta (count)
    pm = (prev.get("missing_contexts","") or "").strip()
    cm = (cur.get("missing_contexts","") or "").strip()
    if pm != cm and (pm not in ("-","") or cm not in ("-","")):
        return "CONTEXT: missing contexts changed"

    # gate delta
    if (prev.get("gate") or "") != (cur.get("gate") or ""):
        return "GATE: merge gate changed"

    return "NONE: no significant transition"


def _split_actions_field(v: str) -> set:
    if not v:
        return set()
    parts = [p.strip() for p in (v or "").split("|")]
    return set([p for p in parts if p])


def _action_delta(prev_fields: dict, cur_fields: dict) -> str:
    prev = _split_actions_field((prev_fields or {}).get("next_actions", ""))
    cur = _split_actions_field((cur_fields or {}).get("next_actions", ""))
    added = sorted(list(cur - prev))
    removed = sorted(list(prev - cur))
    if not prev and cur:
        return "- actions: initialized"
    if not added and not removed:
        return "- actions: no change"
    lines = []
    if added:
        lines.append("- actions added: " + ", ".join([f"`{a}`" for a in added[:6]]) + ("" if len(added) <= 6 else f" (+{len(added)-6} more)"))
    if removed:
        lines.append("- actions removed: " + ", ".join([f"`{a}`" for a in removed[:6]]) + ("" if len(removed) <= 6 else f" (+{len(removed)-6} more)"))
    return "\n".join(lines)


def _top_blocker(cur_fields: dict, body: str, pr_number: int, allow_link: bool = True, include_top_check: bool = True) -> str:
    # choose one top blocker line for operator focus
    conc = (cur_fields or {}).get("conclusion","").lower()
    missing = (cur_fields or {}).get("missing_contexts","")

    if missing and missing.strip() not in ("-", "none"):
        first = missing.split(",")[0].strip()
        if allow_link:
            rb = _match_runbook(body, first)
            if rb:
                return f"missing_contexts: `{first}` (runbook: {rb})"
        return f"missing_contexts: `{first}`"

    failing = _parse_checks_failing((cur_fields or {}).get("checks",""))
    if failing > 0:
        if include_top_check:
            name, url = _get_top_failing_check(pr_number)
            if name and url:
                return f"checks failing: `{failing}` (top: `{name}` {url})"
            if name:
                return f"checks failing: `{failing}` (top: `{name}`)"
        return f"checks failing: `{failing}`"

    gate = (cur_fields or {}).get("gate","")
    if gate and gate.strip() not in ("n/a","-"):
        return f"merge gate: `{gate}`"

    if "success" in conc:
        return "green: ready (no blocker detected)"
    if conc:
        return f"conclusion: `{cur_fields.get('conclusion')}`"
    return "unknown"






from dataclasses import dataclass
from typing import Dict, Optional

import requests
from shared.github_api import request_json, GitHubAPIError

from shared.settings import settings
from shared.comment_dedupe import compute_hash, get_last_hash_wf, get_last_url_wf, set_last_hash_url_wf, get_last_body_wf, get_last_fields_wf, set_last_state_wf, get_last_hash, get_last_url, set_last_hash_url
from shared.logging_utils import get_logger

logger = get_logger("github_comments")


@dataclass
class GitHubCommentResult:
    ok: bool
    url: Optional[str] = None
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


def _inject_diff(body: str, prev: str, max_lines: int, changelog: str) -> str:
    """Insert a compact unified diff under 'Change since last report'.

    The comment body includes the placeholder '_diff will appear here when enabled_'.
    """
    placeholder = "_diff will appear here when enabled_"
    if placeholder not in body:
        return body

    if not prev:
        payload = (changelog or "- first report") + "\n\n_no previous report found_"
        return body.replace(placeholder, payload)

    a = prev.splitlines()
    b = body.splitlines()
    diff = list(difflib.unified_diff(a, b, lineterm="", n=1))

    # Drop the first two header lines if present to reduce noise
    if len(diff) >= 2 and diff[0].startswith("---") and diff[1].startswith("+++"):
        diff = diff[2:]

    if not diff:
        payload = (changelog or "- no changes") + "\n\n_no changes_"
        return body.replace(placeholder, payload)

    max_lines = max(4, int(max_lines or 24))
    diff = diff[:max_lines]
    block = "```diff\n" + "\n".join(diff) + "\n```"
    payload = (changelog or "-") + "\n\n" + block
    return body.replace(placeholder, payload)
def _find_existing_issue(title: str) -> str:
    # Returns issue URL if found (best-effort, search open issues by title)
    try:
        url = f"{_base()}/search/issues"
        q = f"repo:{_repo()} is:issue is:open in:title \"{title}\""
        r = requests.get(url, headers=_headers(), params={"q": q}, timeout=20)
        if not (200 <= r.status_code < 300):
            return ""
        items = (r.json() or {}).get("items") or []
        if items:
            return (items[0] or {}).get("html_url") or ""
        return ""
    except Exception:
        return ""


def _create_issue(title: str, body: str) -> tuple[bool, str]:
    try:
        url = f"{_base()}/repos/{_repo()}/issues"
        r = requests.post(url, headers=_headers(), json={"title": title, "body": body, "labels": ["nexus-autofix"]}, timeout=20)
        if 200 <= r.status_code < 300:
            return (True, (r.json() or {}).get("html_url") or "")
        return (False, "")
    except Exception:
        return (False, "")


def create_or_update_issue_fallback(pr_number: int, body: str) -> str:
    # We do not update existing issue body via API to keep scope minimal; create if none found.
    title = f"NEXUS AutoFix report for PR #{int(pr_number)}"
    existing = _find_existing_issue(title)
    if existing:
        return existing
    ok, url = _create_issue(title, body)
    return url or ""


def _find_existing_issue_v2(title: str) -> tuple[int, str]:
    # Returns (issue_number, issue_url) if found.
    try:
        url = f"{_base()}/search/issues"
        q = f"repo:{_repo()} is:issue is:open in:title \"{title}\""
        try:
            _, js, _ = request_json("GET", url, params={"q": q}, retries=2)
        except GitHubAPIError:
            return (0, "")
        items = (js or {}).get("items") or []
        if items:
            it = items[0] or {}
            return (int(it.get("number") or 0), it.get("html_url") or "")
        return (0, "")
    except Exception:
        return (0, "")


def _create_issue_v2(title: str, body: str) -> tuple[bool, int, str]:
    try:
        url = f"{_base()}/repos/{_repo()}/issues"
        try:
            _, js, _ = request_json("POST", url, json_payload={"title": title, "body": body, "labels": ["nexus-autofix"]})
            return (True, int((js or {}).get("number") or 0), (js or {}).get("html_url") or "")
        except GitHubAPIError:
            return (False, 0, "")
    except Exception:
        return (False, 0, "")


def _append_issue_comment(issue_number: int, body: str) -> bool:
    try:
        url = f"{_base()}/repos/{_repo()}/issues/{int(issue_number)}/comments"
        try:
            request_json("POST", url, json_payload={"body": body})
            return True
        except GitHubAPIError:
            return False
    except Exception:
        return False

def _issue_summary_box(cur_fields: dict, transition: str, top_blocker: str, top_check: str) -> str:
    # Compact operator summary for issue body top.
    conc = (cur_fields or {}).get("conclusion", "")
    gate = (cur_fields or {}).get("gate", "")
    checks = (cur_fields or {}).get("checks", "")
    miss = (cur_fields or {}).get("missing_contexts", "")
    req = (cur_fields or {}).get("required_contexts", "")
    lines = []
    lines.append("## Summary")
    lines.append("")
    lines.append("| key | value |")
    lines.append("|---|---|")
    lines.append(f"| transition | {transition} |")
    lines.append(f"| top_blocker | {top_blocker} |")
    if top_check:
        lines.append(f"| top_failing_check | {top_check} |")
    lines.append(f"| conclusion | {conc} |")
    lines.append(f"| gate | {gate} |")
    lines.append(f"| checks | {checks} |")
    lines.append(f"| missing_contexts | {miss} |")
    lines.append(f"| required_contexts | {req} |")
    lines.append("")
    return "\n".join(lines)

NEXUS_HISTORY_START = "<!-- NEXUS_HISTORY_START -->"
NEXUS_HISTORY_END = "<!-- NEXUS_HISTORY_END -->"


def _get_issue_body(issue_number: int) -> str:
    try:
        url = f"{_base()}/repos/{_repo()}/issues/{int(issue_number)}"
        try:
            _, js, _ = request_json("GET", url, retries=2)
            return (js or {}).get("body") or ""
        except GitHubAPIError:
            return ""
    except Exception:
        return ""


def _update_body_with_history(existing_body: str, newest_entry: str, max_entries: int) -> str:
    # Store history inside body between markers. Each entry is separated by \n\n---\n\n
    max_entries = max(1, int(max_entries or 10))
    if NEXUS_HISTORY_START in existing_body and NEXUS_HISTORY_END in existing_body:
        pre, rest = existing_body.split(NEXUS_HISTORY_START, 1)
        hist, post = rest.split(NEXUS_HISTORY_END, 1)
        hist = hist.strip()
        entries = [e.strip() for e in hist.split("\n\n---\n\n") if e.strip()]
    else:
        pre = existing_body.strip() + "\n\n" if existing_body.strip() else ""
        post = ""
        entries = []

    entries = [newest_entry.strip()] + entries
    entries = entries[:max_entries]
    hist_block = "\n\n---\n\n".join(entries).strip()

    body = pre
    body += NEXUS_HISTORY_START + "\n" + (hist_block + "\n" if hist_block else "")
    body += NEXUS_HISTORY_END + "\n"
    body += post.lstrip()
    return body




def _update_issue_body(issue_number: int, body: str) -> bool:
    try:
        url = f"{_base()}/repos/{_repo()}/issues/{int(issue_number)}"
        try:
            request_json("PATCH", url, json_payload={"body": body})
            return True
        except GitHubAPIError:
            return False
    except Exception:
        return False




def create_or_update_issue_fallback_v2(pr_number: int, body: str, append: bool = True, update_body: bool = True, summary_box: str = "") -> str:
    # Create issue if none; if exists, update issue body to latest snapshot and append history as comment (optional).
    title = f"NEXUS AutoFix report for PR #{int(pr_number)}"
    num, url = _find_existing_issue_v2(title)
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    latest = (summary_box + "\n\n" if summary_box else "") + f"## Latest snapshot ({stamp})\n\n" + (body or "")
    if num and url:
        from shared.settings import settings
        in_body_hist = bool(getattr(settings, "autofix_issue_history_in_body", True))
        max_hist = int(getattr(settings, "autofix_issue_history_max", 10) or 10)
        if update_body:
            if in_body_hist:
                existing = _get_issue_body(num)
                # Ensure summary_box stays on top of body
                base = latest
                # store previous snapshots in history markers inside body
                body2 = _update_body_with_history(base, newest_entry=latest, max_entries=max_hist)
                _update_issue_body(num, body2)
            else:
                _update_issue_body(num, latest)
        # Optional: keep external history via issue comments
        if append:
            _append_issue_comment(num, latest)
        return url
    # initialize body with in-body history markers (first entry)
    from shared.settings import settings
    in_body_hist = bool(getattr(settings, "autofix_issue_history_in_body", True))
    max_hist = int(getattr(settings, "autofix_issue_history_max", 10) or 10)
    body_init = _update_body_with_history(latest, newest_entry=latest, max_entries=max_hist) if in_body_hist else latest
    ok, num2, url2 = _create_issue_v2(title, body_init)
    return url2 or ""


def _webhook_route_url(default_url: str) -> str:
    try:
        from shared.settings import settings
        mp = (getattr(settings, "autofix_alert_webhook_route_map", "") or "").strip()
        if not mp:
            return default_url
        repo = _repo()
        # Format: "repo:org/repo=url;repo:org/repo2=url;default=url"
        parts = [p.strip() for p in mp.split(";") if p.strip()]
        default = default_url
        for p in parts:
            if p.startswith("default="):
                default = p.split("=",1)[1].strip() or default
        for p in parts:
            if p.startswith("repo:") and "=" in p:
                k, v = p.split("=",1)
                k = k.replace("repo:","",1).strip()
                if k == repo:
                    return v.strip() or default
        return default
    except Exception:
        return default_url


def _send_webhook_alert(text: str, pr_url: str = "", checks_url: str = "", run_url: str = "", top_check_name: str = "", top_check_url: str = "") -> bool:
    """Send an optional webhook alert (Slack/Teams/etc). Best-effort only."""
    try:
        from shared.settings import settings

        if not bool(getattr(settings, "autofix_alert_webhook_enabled", False)):
            return False

        url = (getattr(settings, "autofix_alert_webhook_url", "") or "").strip()
        if not url:
            return False

        url = _webhook_route_url(url)
        fmt = (getattr(settings, "autofix_alert_webhook_format", "text") or "text").strip().lower()

        if fmt == "teams_adaptive":
            facts = []
            if pr_url:
                facts.append({"name": "PR", "value": pr_url})
            if checks_url:
                facts.append({"name": "Checks", "value": checks_url})
            if run_url:
                facts.append({"name": "Run", "value": run_url})
            if top_check_name and top_check_url:
                facts.append({"name": "Top failing check", "value": f"{top_check_name} {top_check_url}"})
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "summary": text[:240],
                "title": "NEXUS Alert",
                "text": text[:3500],
                "sections": [{"facts": facts}] if facts else [],
            }

        elif fmt == "slack_blocks":
            blocks = []
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text[:2900]}})
            if top_check_name and top_check_url:
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Top failing check:* <{top_check_url}|{top_check_name}>"},
                })

            btns = []
            if pr_url:
                btns.append({"type": "button", "text": {"type": "plain_text", "text": "PR"}, "url": pr_url})
            if checks_url:
                btns.append({"type": "button", "text": {"type": "plain_text", "text": "Checks"}, "url": checks_url})
            if run_url:
                btns.append({"type": "button", "text": {"type": "plain_text", "text": "Run"}, "url": run_url})
            if btns:
                blocks.append({"type": "actions", "elements": btns[:5]})

            payload = {"text": text[:3500], "blocks": blocks}

        else:
            extra = []
            if pr_url:
                extra.append(f"PR: {pr_url}")
            if checks_url:
                extra.append(f"Checks: {checks_url}")
            if run_url:
                extra.append(f"Run: {run_url}")
            if top_check_name and top_check_url:
                extra.append(f"Top failing check: {top_check_name} {top_check_url}")
            payload = {"text": (text + ("\n" + "\n".join(extra) if extra else ""))[:3500]}

        r = requests.post(url, json=payload, timeout=20)
        return 200 <= r.status_code < 300
    except Exception:
        return False


def _post_with_retry(url: str, json_payload: dict, max_tries: int, base_ms: int, respect_retry_after: bool = True) -> requests.Response:
    last = None
    for i in range(max_tries):
        try:
            _, _, r = request_json("POST", url, json_payload=json_payload, retries=1, base_ms=base_ms, respect_retry_after=respect_retry_after)
        except GitHubAPIError as e:
            class _R:
                status_code = e.status_code
                headers = {}
                text = str(e)
            r = _R()
        last = r
        if 200 <= getattr(r, "status_code", 0) < 300:
            return r
        # 403/401: no point retrying
        if r.status_code in (401, 403):
            return r
        # 429/5xx: retry with backoff+jitter; optionally respect Retry-After
        if r.status_code == 429 or (500 <= r.status_code < 600):
            if respect_retry_after:
                ra = (r.headers or {}).get("Retry-After")
                if ra:
                    try:
                        ra_s = float(ra)
                        time.sleep(min(20.0, ra_s))
                        continue
                    except Exception:
                        pass
            sleep_s = (base_ms / 1000.0) * (2 ** i) + random.uniform(0, 0.2)
            time.sleep(min(8.0, sleep_s))
            continue
        # other codes: don't retry
        return r
    return last


def comment_on_pr(pr_number: int, body: str) -> GitHubCommentResult:
    if not _repo():
        return GitHubCommentResult(False, None, "GITHUB_REPO not set")
    if not getattr(settings, "github_token", ""):
        return GitHubCommentResult(False, None, "GITHUB_TOKEN not set")

    # v5.0: strict marker v2 (repo/workflow/pr) + table/diff ergonomics
    store_path = getattr(settings, "autofix_cooldown_store_path", "/tmp/nexus_cooldown_store.json")
    dedupe = bool(getattr(settings, "autofix_comment_dedupe", True))
    marker_prefix = getattr(settings, "autofix_comment_marker", "<!-- NEXUS_AUTOFIX_MARKER:v2 -->")
    bot_login = (getattr(settings, "autofix_github_bot_login", "") or "").strip().lower()
    workflow = (os.getenv("GITHUB_WORKFLOW") or os.getenv("GITHUB_WORKFLOW_REF") or "wf").strip() or "wf"
    repo_id = _repo()
    exact_marker = f"{marker_prefix} repo={repo_id} workflow={workflow} pr={int(pr_number)} -->"
    # diff support
    diff_max = int(getattr(settings, "autofix_comment_diff_max_lines", 24) or 24)
    store_body = bool(getattr(settings, "autofix_comment_store_body", True))

    # Deduplicate identical bodies per workflow
    h = compute_hash(body)
    if dedupe:
        last_h = get_last_hash_wf(store_path, repo_id, pr_number, workflow)
        last_url = get_last_url_wf(store_path, repo_id, pr_number, workflow)
        if last_h and last_h == h and last_url:
            return GitHubCommentResult(True, last_url, None)

    # Inject changelog + diff using previous stored body/fields
    changelog_enabled = bool(getattr(settings, "autofix_comment_changelog", True))
    transition_enabled = bool(getattr(settings, "autofix_comment_transition_summary", True))
    action_delta_enabled = bool(getattr(settings, "autofix_comment_action_delta", True))
    top_blocker_enabled = bool(getattr(settings, "autofix_comment_top_blocker", True))
    prev_body = get_last_body_wf(store_path, repo_id, pr_number, workflow) if store_body else ""
    prev_fields = get_last_fields_wf(store_path, repo_id, pr_number, workflow) if (store_body and changelog_enabled) else {}
    cur_fields = _parse_fields_from_body(body)
    base_changelog = _build_changelog(prev_fields, cur_fields) if changelog_enabled else "- changelog disabled"
    if transition_enabled:
        ts = _transition_summary(prev_fields, cur_fields)
        allow_link = bool(getattr(settings, "autofix_comment_top_blocker_link", True))
        include_top_check = bool(getattr(settings, "autofix_comment_top_check", True))
        # for issue summary: capture a clean top failing check label if available
        top_check_label = ""
        if include_top_check and _parse_checks_failing((cur_fields or {}).get("checks","")) > 0:
            nm, u = _get_top_failing_check(pr_number)
            if nm:
                top_check_label = nm
        tb = _top_blocker(cur_fields, body, pr_number, allow_link=allow_link, include_top_check=include_top_check) if top_blocker_enabled else "disabled"
        ad = _action_delta(prev_fields, cur_fields) if action_delta_enabled else "- actions delta disabled"
        changelog = f"**Transition:** {ts}\n\n**Top blocker:** {tb}\n\n" + ad + "\n" + base_changelog
    else:
        allow_link = bool(getattr(settings, "autofix_comment_top_blocker_link", True))
        include_top_check = bool(getattr(settings, "autofix_comment_top_check", True))
        # for issue summary: capture a clean top failing check label if available
        top_check_label = ""
        if include_top_check and _parse_checks_failing((cur_fields or {}).get("checks","")) > 0:
            nm, u = _get_top_failing_check(pr_number)
            if nm:
                top_check_label = nm
        tb = _top_blocker(cur_fields, body, pr_number, allow_link=allow_link, include_top_check=include_top_check) if top_blocker_enabled else "disabled"
        ad = _action_delta(prev_fields, cur_fields) if action_delta_enabled else "- actions delta disabled"
        changelog = f"**Top blocker:** {tb}\n\n" + ad + "\n" + base_changelog
    body2 = _inject_diff(body, prev_body, diff_max, changelog) if store_body else body

    # Update-in-place: find exact marker match
    comment_id = None
    comment_url = None
    try:
        comments = list_issue_comments(pr_number, per_page=100)
        for c in reversed(comments):
            b = (c.get("body") or "")
            if exact_marker in b:
                if bot_login:
                    author = (((c.get("user") or {}).get("login")) or "").strip().lower()
                    if author != bot_login:
                        continue
                comment_id = c.get("id")
                comment_url = c.get("html_url")
                break
    except Exception:
        comment_id = None

    if comment_id:
        u = update_issue_comment(int(comment_id), body2)
        if u.ok:
            set_last_state_wf(store_path, repo_id, pr_number, workflow, h, u.url or comment_url or "", body if store_body else "", fields=cur_fields)
            return u

    # Fallback create
    url = f"{_base()}/repos/{repo_id}/issues/{pr_number}/comments"
    retry_enabled = bool(getattr(settings, "autofix_comment_fail_retry", True))
    retry_max = int(getattr(settings, "autofix_comment_fail_retry_max", 3) or 3)
    retry_base = int(getattr(settings, "autofix_comment_fail_retry_base_ms", 600) or 600)
    if retry_enabled:
        respect_ra = bool(getattr(settings, "autofix_comment_respect_retry_after", True))
        r = _post_with_retry(url, {"body": body2}, max_tries=retry_max, base_ms=retry_base, respect_retry_after=respect_ra)
    else:
        r = requests.post(url, headers=_headers(), json={"body": body2}, timeout=20)
    if 200 <= r.status_code < 300:
        html = (r.json() or {}).get("html_url")
        set_last_state_wf(store_path, repo_id, pr_number, workflow, h, html or "", body if store_body else "", fields=cur_fields)
        return GitHubCommentResult(True, html, None)
    logger.warning({"event":"GITHUB_COMMENT_NON2XX","status":r.status_code,"text":r.text[:800]})
    if bool(getattr(settings, "autofix_comment_issue_fallback", True)):
        append = bool(getattr(settings, "autofix_comment_issue_append", True))
        update_body = bool(getattr(settings, "autofix_comment_issue_update_body", True))
        # Policy:
        # - 403/401: immediate issue fallback (no retry benefit)
        # - 429/5xx: after retry exhaustion, issue fallback
        # build summary box for issue body top
        summary_box = _issue_summary_box(cur_fields, ts if transition_enabled else "n/a", tb, top_check_label)
        isu = create_or_update_issue_fallback_v2(pr_number, body2, append=append, update_body=update_body, summary_box=summary_box)
        if isu:
            return GitHubCommentResult(False, isu, f"comment failed: {r.status_code} (issue fallback)")
        # if issue fallback also failed, try webhook alert
        server = (os.getenv("GITHUB_SERVER_URL") or "https://github.com").rstrip("/")
        pr_url = f"{server}/{repo_id}/pull/{int(pr_number)}"
        _send_webhook_alert(
            f"[NEXUS] comment+issue fallback failed (status {r.status_code})",
            pr_url=pr_url,
            checks_url=f"{server}/{repo_id}/pull/{int(pr_number)}/checks",
            run_url=(f"{server}/{repo_id}/actions/runs/{os.getenv('GITHUB_RUN_ID')}" if os.getenv('GITHUB_RUN_ID') else ""),
            top_check_name=top_check_label,
            top_check_url=(_get_top_failing_check(pr_number)[1] if top_check_label else "")
        )
    return GitHubCommentResult(False, None, f"comment failed: {r.status_code}")
