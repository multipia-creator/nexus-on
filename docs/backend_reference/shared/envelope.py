from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class FailureEnvelope:
    failure_code: str
    error: Dict[str, Any]
    failed_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {"failure_code": self.failure_code, "error": self.error, "failed_at": self.failed_at}


def attach_failure(task: Dict[str, Any], failure_code: str, error: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of task with standardized failure envelope attached."""
    out = dict(task)
    out["failure"] = FailureEnvelope(failure_code=failure_code, error=error, failed_at=utc_now()).to_dict()
    # Keep backwards compatibility fields (optional)
    out["failure_code"] = failure_code
    out["last_error"] = error
    out["failed_at"] = out["failure"]["failed_at"]
    return out


def extract_failure_code(headers: Optional[Dict[str, Any]], msg: Dict[str, Any]) -> Optional[str]:
    if headers and headers.get("failure_code"):
        return str(headers.get("failure_code"))
    # body fields
    if msg.get("failure_code"):
        return str(msg.get("failure_code"))
    failure = msg.get("failure") or {}
    if isinstance(failure, dict) and failure.get("failure_code"):
        return str(failure.get("failure_code"))
    return None


def extract_task_type(msg: Dict[str, Any]) -> str:
    return str(msg.get("task_type") or msg.get("type") or "unknown")
