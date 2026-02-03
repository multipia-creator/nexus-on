from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from shared.settings import settings
from shared.logging_utils import get_logger

logger = get_logger("github_pr")

@dataclass
class GitHubPRResult:
    ok: bool
    pr_url: Optional[str] = None
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
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
    return None


def get_repo_default_branch() -> Optional[str]:
    err = _require()
    if err:
        return None
    url = f"{_base()}/repos/{_repo()}"
    r = requests.get(url, headers=_headers(), timeout=15)
    if 200 <= r.status_code < 300:
        return (r.json() or {}).get("default_branch")
    return None


def get_branch_sha(branch: str) -> Optional[str]:
    url = f"{_base()}/repos/{_repo()}/git/ref/heads/{branch}"
    r = requests.get(url, headers=_headers(), timeout=15)
    if 200 <= r.status_code < 300:
        return ((r.json() or {}).get("object") or {}).get("sha")
    return None


def create_branch(new_branch: str, from_sha: str) -> bool:
    url = f"{_base()}/repos/{_repo()}/git/refs"
    payload = {"ref": f"refs/heads/{new_branch}", "sha": from_sha}
    r = requests.post(url, headers=_headers(), json=payload, timeout=15)
    if 200 <= r.status_code < 300:
        return True
    # If branch exists, allow idempotent behavior
    if r.status_code == 422:
        return True
    logger.warning({"event":"GITHUB_CREATE_BRANCH_NON2XX","status":r.status_code,"text":r.text[:800]})
    return False


def get_file_text(path: str, branch: str) -> tuple[Optional[str], Optional[str]]:
    """Return (text, sha) or (None,None) if missing."""
    url = f"{_base()}/repos/{_repo()}/contents/{path.lstrip('/')}"
    r = requests.get(url, headers=_headers(), params={"ref": branch}, timeout=15)
    if r.status_code == 404:
        return None, None
    if 200 <= r.status_code < 300:
        data = r.json() or {}
        content = data.get("content") or ""
        sha = data.get("sha")
        try:
            import base64
            txt = base64.b64decode(content).decode("utf-8") if content else ""
        except Exception:
            txt = ""
        return txt, sha
    logger.warning({"event":"GITHUB_GET_FILE_TEXT_NON2XX","status":r.status_code,"text":r.text[:800]})
    return None, None


def upsert_file(path: str, content_text: str, branch: str, message: str) -> Optional[str]:
    """Create or update a file via Contents API. Returns commit sha."""
    url = f"{_base()}/repos/{_repo()}/contents/{path.lstrip('/')}"
    # check existing
    r0 = requests.get(url, headers=_headers(), params={"ref": branch}, timeout=15)
    sha = None
    if 200 <= r0.status_code < 300:
        sha = (r0.json() or {}).get("sha")
    elif r0.status_code not in (404,):
        logger.warning({"event":"GITHUB_GET_CONTENT_NON2XX","status":r0.status_code,"text":r0.text[:800]})

    b64 = base64.b64encode(content_text.encode("utf-8")).decode("ascii")
    payload: Dict[str, Any] = {"message": message, "content": b64, "branch": branch}
    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=_headers(), json=payload, timeout=20)
    if 200 <= r.status_code < 300:
        return (((r.json() or {}).get("commit") or {}).get("sha"))

    logger.warning({"event":"GITHUB_UPSERT_FILE_NON2XX","status":r.status_code,"text":r.text[:800]})
    return None


def create_pull_request(title: str, body: str, head: str, base: str) -> Optional[str]:
    url = f"{_base()}/repos/{_repo()}/pulls"
    payload = {"title": title, "body": body, "head": head, "base": base}
    r = requests.post(url, headers=_headers(), json=payload, timeout=20)
    if 200 <= r.status_code < 300:
        return (r.json() or {}).get("html_url")
    # If PR exists, GitHub returns 422; attempt to find existing? (skip for simplicity)
    logger.warning({"event":"GITHUB_CREATE_PR_NON2XX","status":r.status_code,"text":r.text[:800]})
    return None


def create_autofix_pr(
    branch_suffix: str,
    base_branch: Optional[str],
    title: str,
    md_path: str,
    md_content: str,
    pr_body: str,
) -> GitHubPRResult:
    err = _require()
    if err:
        return GitHubPRResult(False, None, None, None, err)

    base = base_branch or getattr(settings, "github_default_branch", "") or get_repo_default_branch() or "main"
    base_sha = get_branch_sha(base)
    if not base_sha:
        return GitHubPRResult(False, None, None, None, f"failed to resolve base branch sha: {base}")

    branch = f"nexus/autofix/{branch_suffix}".replace(" ", "-").replace("/", "-")
    if not create_branch(branch, base_sha):
        return GitHubPRResult(False, None, None, None, "failed to create branch")

    commit_sha = upsert_file(md_path, md_content, branch, message=f"nexus: add autofix suggestion {branch_suffix}")
    if not commit_sha:
        return GitHubPRResult(False, None, branch, None, "failed to create/update autofix file")

    pr_url = create_pull_request(title=title, body=pr_body, head=branch, base=base)
    if not pr_url:
        return GitHubPRResult(False, None, branch, commit_sha, "failed to create PR")

    return GitHubPRResult(True, pr_url, branch, commit_sha, None)
