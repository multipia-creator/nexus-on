from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from shared.settings import settings

# Lightweight, ops-friendly runbook pointers.
# You can replace these with internal docs URLs.
DEFAULT_RUNBOOKS: Dict[str, str] = {
    "PROVIDER_AUTH_ERROR": "Runbook: LLM provider auth/keys/permissions",
    "PROVIDER_DISABLED": "Runbook: Provider disabled / feature flags",
    "PROVIDER_RATE_LIMIT": "Runbook: Rate limit mitigation / backoff",
    "PROVIDER_TIMEOUT": "Runbook: Timeout tuning / network",
    "PROVIDER_UPSTREAM_ERROR": "Runbook: Upstream 5xx handling",
    "SCHEMA_PARSE_ERROR": "Runbook: Schema parse failures (JSON-only output)",
    "SCHEMA_VALIDATION_ERROR": "Runbook: Schema validation failures (fields/constraints)",
    "SCHEMA_REPAIR_FAILED": "Runbook: Repair failed (prompt + schema alignment)",
}

def get_runbook(failure_code: str) -> Optional[str]:
    url = runbook_url(failure_code)
    if url:
        return url
    return DEFAULT_RUNBOOKS.get(failure_code)


def runbook_url(failure_code: str) -> Optional[str]:
    base = getattr(settings, "runbook_base_url", "") or ""
    if not base:
        return None
    base = base.rstrip("/")
    # simple convention: {base}/{failure_code}
    return f"{base}/{failure_code}"
