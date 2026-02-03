from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MergeErrorClass:
    code: str
    note: str


def classify_merge_failure(status_code: Optional[int], message: str) -> MergeErrorClass:
    msg = (message or "").lower()
    sc = int(status_code or 0)

    if sc in (401, 403):
        return MergeErrorClass("permission_denied", "Token lacks permission or branch protection blocks this action.")
    if sc == 404:
        return MergeErrorClass("not_found", "PR or repo not found (or token has no access).")
    if sc == 409:
        # typical: "Merge conflict" / "Head branch was modified"
        if "conflict" in msg or "merge conflict" in msg or "dirty" in msg:
            return MergeErrorClass("merge_conflict", "Merge conflicts detected; manual resolution required.")
        return MergeErrorClass("merge_blocked", "Merge blocked by branch state or protection; re-check mergeability.")
    if sc == 405:
        # often merge queue / auto-merge required
        if "merge queue" in msg or "queue" in msg:
            return MergeErrorClass("merge_queue_required", "Repository requires merge queue / auto-merge for protected branch.")
        return MergeErrorClass("method_not_allowed", "Merge endpoint not allowed; likely protected branch policy.")
    if sc == 422:
        return MergeErrorClass("unprocessable", "Merge request invalid (method, head behind, or policy).")
    if sc == 429:
        return MergeErrorClass("rate_limited", "Rate limited; retry after backoff.")
    if "merge queue" in msg or "queue" in msg:
        return MergeErrorClass("merge_queue_required", "Repository requires merge queue / auto-merge.")
    if "required status check" in msg or "required" in msg and "check" in msg:
        return MergeErrorClass("required_checks_missing", "Required checks not satisfied or not yet reported.")
    if "review" in msg and ("required" in msg or "approval" in msg):
        return MergeErrorClass("required_review_missing", "Required approvals missing.")
    return MergeErrorClass("unknown", "Merge failed; inspect GitHub response message and branch protection.")
