from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from shared.settings import settings

@dataclass
class TriageDecision:
    action: str  # requeue|hold|alarm|ignore
    reason: str

def _csv(s: str) -> List[str]:
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]

def triage_failure_code(failure_code: Optional[str]) -> TriageDecision:
    fc = (failure_code or "").strip() or "unknown"

    auto_requeue = set(_csv(getattr(settings, "auto_requeue_failure_codes", "")))
    auto_hold = set(_csv(getattr(settings, "auto_hold_failure_codes", "")))
    auto_alarm = set(_csv(getattr(settings, "auto_alarm_failure_codes", "")))

    if fc in auto_hold:
        return TriageDecision("hold", "configured hold code")
    if fc in auto_alarm:
        return TriageDecision("alarm", "configured alarm code")
    if fc in auto_requeue:
        return TriageDecision("requeue", "configured auto requeue code")

    # default heuristics (safe)
    if fc in ("PROVIDER_TIMEOUT", "PROVIDER_UPSTREAM_ERROR", "PROVIDER_RATE_LIMIT"):
        return TriageDecision("requeue", "default transient provider error")
    if fc in ("PROVIDER_AUTH_ERROR", "PROVIDER_DISABLED"):
        return TriageDecision("alarm", "non-transient provider config/auth")
    if fc.startswith("SCHEMA_"):
        return TriageDecision("hold", "schema issue needs prompt/schema fix")

    return TriageDecision("ignore", "no rule matched")
