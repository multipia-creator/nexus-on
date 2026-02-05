from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

from shared.settings import settings
from shared.logging_utils import get_logger

logger = get_logger("github_pr_ops")


@dataclass
class GitHubOpsResult:
    ok: bool
    error: Optional[str] = None
    status_code: Optional[int] = None
    message: Optional[str] = None


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


def add_labels(issue_number: int, labels: List[str]) -> GitHubOpsResult:
    url = f"{_base()}/repos/{_repo()}/issues/{issue_number}/labels"
    r = requests.post(url, headers=_headers(), json={"labels": labels}, timeout=20)
    if 200 <= r.status_code < 300:
        return GitHubOpsResult(True, None)
    logger.warning({"event":"GITHUB_ADD_LABELS_NON2XX","status":r.status_code,"text":r.text[:800]})
    return GitHubOpsResult(False, f"add_labels failed: {r.status_code}")


def set_assignees(issue_number: int, assignees: List[str]) -> GitHubOpsResult:
    url = f"{_base()}/repos/{_repo()}/issues/{issue_number}/assignees"
    r = requests.post(url, headers=_headers(), json={"assignees": assignees}, timeout=20)
    if 200 <= r.status_code < 300:
        return GitHubOpsResult(True, None)
    logger.warning({"event":"GITHUB_SET_ASSIGNEES_NON2XX","status":r.status_code,"text":r.text[:800]})
    return GitHubOpsResult(False, f"set_assignees failed: {r.status_code}")


def merge_pr(pr_number: int, method: str = "squash") -> GitHubOpsResult:
    url = f"{_base()}/repos/{_repo()}/pulls/{pr_number}/merge"
    payload = {"merge_method": method}
    r = requests.put(url, headers=_headers(), json=payload, timeout=20)
    if 200 <= r.status_code < 300:
        return GitHubOpsResult(True, None, r.status_code, None)
    msg = ""
    try:
        j = r.json() or {}
        msg = j.get("message") or r.text
    except Exception:
        msg = r.text
    logger.warning({"event":"GITHUB_MERGE_PR_NON2XX","status":r.status_code,"text":(r.text or "")[:800]})
    return GitHubOpsResult(False, f"merge_pr failed: {r.status_code}", r.status_code, (msg or "")[:1200])


@dataclass
class PullInfo:
    ok: bool
    mergeable: Optional[bool] = None
    mergeable_state: Optional[str] = None
    head_sha: Optional[str] = None
    base_ref: Optional[str] = None
    error: Optional[str] = None


def get_pr_info(pr_number: int) -> PullInfo:
    url = f"{_base()}/repos/{_repo()}/pulls/{pr_number}"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        j = r.json() or {}
        return PullInfo(True, j.get("mergeable"), j.get("mergeable_state"), (j.get("head") or {}).get("sha"), (j.get("base") or {}).get("ref"), None)
    logger.warning({"event":"GITHUB_GET_PR_INFO_NON2XX","status":r.status_code,"text":r.text[:800]})
    return PullInfo(False, None, None, None, None, f"get_pr_info failed: {r.status_code}")


def get_combined_status(head_sha: str) -> Dict[str, str]:
    # combined status: state + contexts
    url = f"{_base()}/repos/{_repo()}/commits/{head_sha}/status"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        j = r.json() or {}
        state = j.get("state") or "unknown"
        contexts = [c.get("context") for c in (j.get("statuses") or []) if c.get("context")]
        details = []
        for c in (j.get("statuses") or []):
            nm = c.get("context")
            st = c.get("state")
            if nm:
                details.append(f"{nm}:{st}")
        return {"state": state, "contexts": ",".join(contexts), "contexts_detail": ", ".join(details)}
    logger.warning({"event":"GITHUB_GET_COMBINED_STATUS_NON2XX","status":r.status_code,"text":r.text[:800]})
    return {"state": "unknown", "contexts": ""}


def get_check_runs(head_sha: str) -> Dict[str, str]:
    url = f"{_base()}/repos/{_repo()}/commits/{head_sha}/check-runs"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        j = r.json() or {}
        runs = j.get("check_runs") or []
        # summarize: name=conclusion
        parts = []
        for cr in runs:
            name = cr.get("name") or "check"
            conc = cr.get("conclusion") or cr.get("status") or "unknown"
            parts.append(f"{name}:{conc}")
        return {"summary": ", ".join(parts)}
    logger.warning({"event":"GITHUB_GET_CHECK_RUNS_NON2XX","status":r.status_code,"text":r.text[:800]})
    return {"summary": ""}


@dataclass
class BranchProtectionInfo:
    ok: bool
    required_contexts: List[str] = None
    required_approvals: int = 0
    error: Optional[str] = None


def get_branch_protection(base_ref: str) -> BranchProtectionInfo:
    # Requires admin or appropriate permissions on some repos; best-effort
    url = f"{_base()}/repos/{_repo()}/branches/{base_ref}/protection"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        j = r.json() or {}
        req = j.get("required_status_checks") or {}
        contexts = req.get("contexts") or []
        # Some repos use checks instead of contexts; keep contexts only for now
        prr = j.get("required_pull_request_reviews") or {}
        approvals = int(prr.get("required_approving_review_count") or 0)
        return BranchProtectionInfo(True, contexts, approvals, None)
    # 404 is common if protections are disabled or token lacks scope
    logger.info({"event":"GITHUB_BRANCH_PROTECTION_NON2XX","status":r.status_code,"text":r.text[:500]})
    return BranchProtectionInfo(False, [], 0, f"branch_protection: {r.status_code}")


@dataclass
class PRReviewInfo:
    ok: bool
    approved: int = 0
    changes_requested: int = 0
    comment_only: int = 0
    error: Optional[str] = None


def get_pr_reviews(pr_number: int) -> PRReviewInfo:
    # Return latest state per reviewer. We'll approximate by counting latest submissions.
    url = f"{_base()}/repos/{_repo()}/pulls/{pr_number}/reviews?per_page=100"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        reviews = r.json() or []
        latest = {}
        for rv in reviews:
            user = ((rv.get("user") or {}).get("login")) or ""
            state = (rv.get("state") or "").upper()
            if not user:
                continue
            # GitHub reviews are ordered; later entries overwrite
            latest[user] = state
        approved = sum(1 for s in latest.values() if s == "APPROVED")
        changes = sum(1 for s in latest.values() if s == "CHANGES_REQUESTED")
        comment_only = sum(1 for s in latest.values() if s in ("COMMENTED","DISMISSED"))
        return PRReviewInfo(True, approved, changes, comment_only, None)
    logger.warning({"event":"GITHUB_GET_PR_REVIEWS_NON2XX","status":r.status_code,"text":r.text[:800]})
    return PRReviewInfo(False, 0, 0, 0, f"get_pr_reviews failed: {r.status_code}")


def get_pr_node_id(pr_number: int) -> Optional[str]:
    url = f"{_base()}/repos/{_repo()}/pulls/{pr_number}"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        j = r.json() or {}
        return j.get("node_id")
    logger.info({"event":"GITHUB_GET_PR_NODE_ID_NON2XX","status":r.status_code,"text":(r.text or "")[:500]})
    return None


def enable_auto_merge(pr_number: int, method: str = "squash") -> GitHubOpsResult:
    # GraphQL auto-merge (works with merge queue setups). Best-effort.
    node_id = get_pr_node_id(pr_number)
    if not node_id:
        return GitHubOpsResult(False, "enable_auto_merge: missing node_id", None, None)

    merge_method = {"merge": "MERGE", "squash": "SQUASH", "rebase": "REBASE"}.get((method or "squash").lower(), "SQUASH")
    query = """mutation($prId: ID!, $method: PullRequestMergeMethod!) {
      enablePullRequestAutoMerge(input:{pullRequestId:$prId, mergeMethod:$method}) {
        pullRequest { number }
      }
    }"""
    payload = {"query": query, "variables": {"prId": node_id, "method": merge_method}}
    url = f"{_base()}/graphql"
    r = requests.post(url, headers=_headers(), json=payload, timeout=20)
    if 200 <= r.status_code < 300:
        j = r.json() or {}
        if j.get("errors"):
            return GitHubOpsResult(False, "enable_auto_merge graphql errors", r.status_code, str(j.get("errors"))[:1200])
        return GitHubOpsResult(True, None, r.status_code, None)

    msg = ""
    try:
        j = r.json() or {}
        msg = j.get("message") or r.text
    except Exception:
        msg = r.text
    logger.warning({"event":"GITHUB_ENABLE_AUTO_MERGE_NON2XX","status":r.status_code,"text":(r.text or "")[:800]})
    return GitHubOpsResult(False, f"enable_auto_merge failed: {r.status_code}", r.status_code, (msg or "")[:1200])


def list_issue_comments(pr_number: int, per_page: int = 50) -> list:
    url = f"{_base()}/repos/{_repo()}/issues/{pr_number}/comments?per_page={per_page}"
    r = requests.get(url, headers=_headers(), timeout=20)
    if 200 <= r.status_code < 300:
        return r.json() or []
    logger.info({"event":"GITHUB_LIST_COMMENTS_NON2XX","status":r.status_code,"text":(r.text or "")[:500]})
    return []


def update_issue_comment(comment_id: int, body: str) -> GitHubOpsResult:
    url = f"{_base()}/repos/{_repo()}/issues/comments/{int(comment_id)}"
    payload = {"body": body}
    r = requests.patch(url, headers=_headers(), json=payload, timeout=20)
    if 200 <= r.status_code < 300:
        return GitHubOpsResult(True, None, r.status_code, None)
    msg = ""
    try:
        j = r.json() or {}
        msg = j.get("message") or r.text
    except Exception:
        msg = r.text
    logger.warning({"event":"GITHUB_UPDATE_COMMENT_NON2XX","status":r.status_code,"text":(r.text or "")[:800]})
    return GitHubOpsResult(False, f"update_comment failed: {r.status_code}", r.status_code, (msg or "")[:1200])
