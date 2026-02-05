from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from shared.github_client import create_issue, GitHubResult
from shared.fix_suggester import suggest_fix
from shared.envelope import extract_task_type


@dataclass
class FixIssueResult:
    ok: bool
    issue: Optional[GitHubResult]
    suggestion: Optional[Dict[str, Any]]
    error: Optional[str] = None


def create_fix_issue_from_hold(msg: Dict[str, Any], failure_code: str, provider_override: Optional[str] = None) -> FixIssueResult:
    sug = suggest_fix(msg, failure_code, provider_override=provider_override)
    if not sug.ok or not sug.data:
        return FixIssueResult(False, None, None, error=sug.error or "suggest_fix failed")

    task_type = extract_task_type(msg)
    title = f"[FIX] {task_type}: {failure_code}"
    body = f"""## Auto-generated fix suggestion (schema-enforced)
- provider: {sug.provider}
- model: {sug.model}
- repaired: {sug.repaired}
- attempts: {sug.attempts}

## Issue summary
{sug.data.get("issue_summary","")}

## Probable root cause
{sug.data.get("probable_root_cause","")}

## Proposed changes
### prompt_patch
{sug.data.get("proposed_changes",{}).get("prompt_patch","")}

### schema_patch
{sug.data.get("proposed_changes",{}).get("schema_patch","")}

### code_patch
{sug.data.get("proposed_changes",{}).get("code_patch","")}

## Risk
{sug.data.get("risk","")}

## Verification
- tests:
{chr(10).join([f"- {t}" for t in (sug.data.get("verification",{}).get("tests") or [])])}
- dry_run_steps:
{chr(10).join([f"- {t}" for t in (sug.data.get("verification",{}).get("dry_run_steps") or [])])}
"""
    issue = create_issue(title, body, labels=["fix", "hold", "llm"])
    if not issue.ok:
        return FixIssueResult(False, issue, sug.data, error=issue.error or "github issue create failed")
    return FixIssueResult(True, issue, sug.data, error=None)
