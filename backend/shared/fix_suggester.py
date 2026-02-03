from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from shared.envelope import extract_task_type
from shared.json_guard import repair
from shared.llm_client import LLMClient
from shared.runbooks import get_runbook


@dataclass
class FixSuggestionResult:
    ok: bool
    data: Optional[Dict[str, Any]]
    provider: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None
    repaired: bool = False
    attempts: int = 0


def _build_prompt(msg: Dict[str, Any], failure_code: str) -> str:
    task_type = extract_task_type(msg)
    schema_name = str(msg.get("schema_name") or (msg.get("payload") or {}).get("schema_name") or "")
    failure = msg.get("failure") or {}
    err = (failure.get("error") or msg.get("last_error") or {}) if isinstance(failure, dict) else (msg.get("last_error") or {})
    err_msg = str(err.get("message") or err.get("error") or "")
    runbook = get_runbook(failure_code) or "(add runbook)"

    return f"""You are a senior production engineer and LLM prompt/schema specialist.
You MUST output only JSON matching schema name: fix_suggestion (strict JSON object, no markdown, no fences).

Context:
- task_type: {task_type}
- failure_code: {failure_code}
- schema_name: {schema_name}
- error: {err_msg}
- runbook_hint: {runbook}

Goal:
Return a minimal, actionable fix plan. Prefer the smallest change that prevents recurrence.
If you propose patches, express them as unified diff snippets inside strings (or explicit before/after blocks).

Rules:
- No prose outside JSON.
- proposed_changes.prompt_patch/schema_patch/code_patch can be empty strings if not applicable, but MUST be present.
- verification.tests and verification.dry_run_steps must each include at least 1 item.

Evidence (truncated):
{str(msg)[:6000]}
"""


def suggest_fix(msg: Dict[str, Any], failure_code: str, provider_override: Optional[str] = None) -> FixSuggestionResult:
    llm = LLMClient()
    prompt = _build_prompt(msg, failure_code)
    res = llm.generate(prompt, provider_override=provider_override)
    # validate+repair against fix_suggestion schema
    guard = repair(res.output_text, "fix_suggestion", llm_client=llm, max_attempts=2)
    if not guard.ok:
        return FixSuggestionResult(False, None, res.provider, res.model, guard.error, guard.repaired, guard.attempts)
    return FixSuggestionResult(True, guard.data, res.provider, res.model, None, guard.repaired, guard.attempts)
