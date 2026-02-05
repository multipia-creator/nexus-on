from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class CheckRunSummary:
    total: int
    success: int
    failed: int
    skipped: int
    neutral: int
    cancelled: int
    in_progress: int
    details: List[Tuple[str, str]]  # (name, conclusion/status)


def parse_check_runs_summary(summary: str) -> CheckRunSummary:
    # summary format: "name:conclusion, name2:status"
    items = []
    for part in (summary or "").split(","):
        p = part.strip()
        if not p:
            continue
        if ":" in p:
            n, c = p.split(":", 1)
        else:
            n, c = p, ""
        items.append((n.strip(), (c or "").strip()))

    succ = fail = skip = neut = canc = ip = 0
    for _, c in items:
        cl = c.lower()
        if "success" in cl:
            succ += 1
        elif "failure" in cl or "failed" in cl:
            fail += 1
        elif "skipped" in cl:
            skip += 1
        elif "neutral" in cl:
            neut += 1
        elif "cancel" in cl:
            canc += 1
        elif "in_progress" in cl or "queued" in cl or "requested" in cl or "running" in cl:
            ip += 1
        else:
            # unknown treated as in_progress-ish for safety
            ip += 1

    return CheckRunSummary(
        total=len(items),
        success=succ,
        failed=fail,
        skipped=skip,
        neutral=neut,
        cancelled=canc,
        in_progress=ip,
        details=items,
    )


def required_ok(details_summary: str, required: List[str], match_fn) -> Tuple[bool, List[str]]:
    # delegate to match_fn(summary, required, mode=...)
    return match_fn(details_summary, required)
