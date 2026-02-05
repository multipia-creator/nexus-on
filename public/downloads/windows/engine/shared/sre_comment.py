from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SREComment:
    title: str
    body: str


def build_sre_comment(
    failure_code: str,
    run_url: Optional[str],
    status: Optional[str],
    conclusion: Optional[str],
    merge_note: str,
    missing_checks: List[str],
    next_actions: List[str],
) -> SREComment:
    # compact but structured
    lines = []
    header_line = f"AutoFix: {conclusion or status or 'unknown'} | gate: {merge_note or 'n/a'}"
    lines.append(header_line)
    # Hidden marker used to dedupe/update reliably
    lines.append(getattr(__import__("shared.settings", fromlist=["settings"]).settings, "autofix_comment_marker", "<!-- NEXUS_AUTOFIX_MARKER:v1 -->"))
    lines.append("")
    lines.append("NEXUS AutoFix CI Summary")
    lines.append("")
    lines.append(f"- failure_code: `{failure_code}`")
    if run_url:
        lines.append(f"- workflow_run: {run_url}")
    lines.append(f"- status: `{status}`")
    lines.append(f"- conclusion: `{conclusion}`")
    if merge_note:
        lines.append(f"- merge_gate: {merge_note}")
    if missing_checks:
        lines.append(f"- missing_required_checks: {', '.join(missing_checks)}")
    if next_actions:
        lines.append("")
        lines.append("Next actions")
        for a in next_actions[:6]:
            lines.append(f"- {a}")
    return SREComment(title="NEXUS AutoFix", body="\n".join(lines))
