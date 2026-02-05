from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List


from shared.settings import settings
from shared.logging_utils import get_logger
from shared.github_api import request_json, GitHubAPIError
from shared.github_comments import _update_body_with_history

logger = get_logger("github_client")


@dataclass
class GitHubResult:
    ok: bool
    status_code: Optional[int] = None
    url: Optional[str] = None
    error: Optional[str] = None


def _repo() -> str:
    return getattr(settings, "github_repo", "") or ""


def _base() -> str:
    return getattr(settings, "github_api_base", "https://api.github.com") or "https://api.github.com"


def _headers() -> Dict[str, str]:
    token = getattr(settings, "github_token", "") or ""
    if not token:
        return {}
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "nexus-supervisor",
    }


def create_issue(title: str, body: str, labels: Optional[list[str]] = None) -> GitHubResult:
    repo = _repo()
    base = _base()
    if not repo:
        return GitHubResult(False, None, None, "GITHUB_REPO not set")
    if not getattr(settings, "github_token", "") and not (os.getenv("GITHUB_TOKEN") or ""):
        return GitHubResult(False, None, None, "GITHUB_TOKEN not set")

    url = f"{base}/repos/{repo}/issues"
    payload: Dict[str, Any] = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels

    try:
        code, js, _ = request_json("POST", url, json_payload=payload, retries=2, base_ms=300)
        return GitHubResult(True, code, (js or {}).get("html_url"), None)
    except GitHubAPIError as e:
        logger.warning({"event": "GITHUB_ISSUE_API_ERROR", "status": e.status_code, "url": e.url, "msg": e.message})
        return GitHubResult(False, e.status_code, None, str(e))
    except Exception as e:
        logger.warning({"event": "GITHUB_ISSUE_ERROR", "err": str(e)})
        return GitHubResult(False, None, None, str(e))


# -----------------------------
# Alert issue upsert (dedupe)
# -----------------------------

_DEDUPE_PREFIX = "NEXUS_DEDUPE:"
_DEFAULT_MAX_HISTORY = 12


def _dedupe_marker(dedupe_key: str) -> str:
    dk = (dedupe_key or "").strip()
    return f"<!-- {_DEDUPE_PREFIX}{dk} -->" if dk else ""


def _search_open_issue_by_dedupe(dedupe_key: str) -> Tuple[int, str]:
    repo = _repo()
    if not repo or not getattr(settings, "github_token", ""):
        return 0, ""
    dk = (dedupe_key or "").strip()
    if not dk:
        return 0, ""

    q = f'repo:{repo} is:issue is:open "{_DEDUPE_PREFIX}{dk}" in:body'
    url = f"{_base()}/search/issues"
    try:
        _, js, _ = request_json("GET", url, params={"q": q, "sort": "updated", "order": "desc"}, retries=2, base_ms=300)
        items = (js or {}).get("items") or []
        if not items:
            return 0, ""
        it = items[0] or {}
        return int(it.get("number") or 0), str(it.get("html_url") or "")
    except Exception:
        return 0, ""


def _get_issue_body(issue_number: int) -> str:
    repo = _repo()
    if not repo or not getattr(settings, "github_token", ""):
        return ""
    url = f"{_base()}/repos/{repo}/issues/{int(issue_number)}"
    try:
        _, js, _ = request_json("GET", url, retries=2, base_ms=300)
        return str((js or {}).get("body") or "")
    except Exception:
        return ""


def _update_issue_body(issue_number: int, body: str) -> GitHubResult:
    repo = _repo()
    if not repo:
        return GitHubResult(False, None, None, "GITHUB_REPO not set")
    if not getattr(settings, "github_token", ""):
        return GitHubResult(False, None, None, "GITHUB_TOKEN not set")

    url = f"{_base()}/repos/{repo}/issues/{int(issue_number)}"
    try:
        code, _, _ = request_json("PATCH", url, json_payload={"body": body}, retries=2, base_ms=300)
        return GitHubResult(True, code, None, None)
    except GitHubAPIError as e:
        return GitHubResult(False, e.status_code, None, str(e))
    except Exception as e:
        return GitHubResult(False, None, None, str(e))


def upsert_alert_issue(
    *,
    title: str,
    header: str,
    entry: str,
    dedupe_key: str,
    labels: Optional[List[str]] = None,
    max_history: int = _DEFAULT_MAX_HISTORY,
) -> GitHubResult:
    """Create or update an alert issue by dedupe_key.

    - Search open issues by body marker: <!-- NEXUS_DEDUPE:<key> -->
    - Store snapshots inside in-body history markers (NEXUS_HISTORY_START/END)
      via shared.github_comments._update_body_with_history
    """
    repo = _repo()
    if not repo:
        return GitHubResult(False, None, None, "GITHUB_REPO not set")
    if not getattr(settings, "github_token", ""):
        return GitHubResult(False, None, None, "GITHUB_TOKEN not set")

    dk = (dedupe_key or "").strip()
    marker = _dedupe_marker(dk)

    base_header = (header or "").strip()
    if marker and marker not in base_header:
        base_header = (base_header + "\n\n" + marker).strip()

    newest = (entry or "").strip()
    if marker and marker not in newest:
        newest = (newest + "\n\n" + marker).strip()

    issue_no, html = _search_open_issue_by_dedupe(dk) if dk else (0, "")
    if issue_no:
        existing = _get_issue_body(issue_no)
        if marker and marker not in (existing or ""):
            existing = (existing.strip() + "\n\n" + marker).strip() + "\n"
        body2 = _update_body_with_history(existing or base_header, newest_entry=newest, max_entries=max_history)
        r = _update_issue_body(issue_no, body2)
        r.url = html or r.url
        return r

    body_init = _update_body_with_history(base_header or newest, newest_entry=newest, max_entries=max_history)
    if marker and marker not in body_init:
        body_init = (body_init.strip() + "\n\n" + marker).strip() + "\n"
    return create_issue(title[:240], body_init, labels=labels or [])
