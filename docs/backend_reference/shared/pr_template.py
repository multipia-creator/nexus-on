from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from shared.envelope import extract_task_type
from shared.runbooks import get_runbook

@dataclass
class PRTemplate:
    title: str
    body: str

def build_hold_pr(msg: Dict[str, Any], headers: Optional[Dict[str, Any]] = None) -> PRTemplate:
    failure = msg.get("failure") or {}
    failure_code = str(failure.get("failure_code") or msg.get("failure_code") or "unknown")
    task_type = extract_task_type(msg)
    schema = (msg.get("schema_name") or (msg.get("payload") or {}).get("schema_name") or "")

    err = failure.get("error") or msg.get("last_error") or {}
    err_msg = err.get("message") or err.get("error") or ""

    runbook = get_runbook(failure_code) or "Runbook: (add link)"
    task_id = msg.get("task_id") or (headers or {}).get("correlation_id") or "unknown"

    body = f"""## Summary
HOLD triage: `{failure_code}` for task `{task_id}` (task_type: `{task_type}`)

## What failed
- failure_code: `{failure_code}`
- schema_name: `{schema}`
- error: `{err_msg}`

## Expected JSON/schema
- schema file: `shared/schemas/{schema}.schema.json` (if applicable)
- If schema_name is empty, check caller passed `schema_name` and `allow_repair=true`.

## Suggested fix
1) Tighten prompt to force JSON-only output (no prose, no fences)
2) If fields missing, update schema defaults or caller logic
3) Add/adjust repair prompt in `shared/json_guard.py`

## Runbook
- {runbook}

## Evidence
```json
{json.dumps(msg, ensure_ascii=False, indent=2)[:4000]}
```
"""
    title = f"[HOLD] {task_type}: {failure_code}"
    return PRTemplate(title=title, body=body)
