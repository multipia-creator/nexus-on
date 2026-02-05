from __future__ import annotations

import json
import os
import time
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List

from shared.settings import settings
from shared.append_only import append_jsonl_with_chain


@dataclass
class BudgetState:
    day_key: str
    spent_usd: float


def _today_utc_key() -> str:
    # YYYY-MM-DD in UTC
    return time.strftime("%Y-%m-%d", time.gmtime())


def _budget_state_path() -> str:
    return "logs/budget_state.json"


def _load_budget_state() -> BudgetState:
    try:
        path = _budget_state_path()
        if not os.path.exists(path):
            return BudgetState(day_key=_today_utc_key(), spent_usd=0.0)
        with open(path, "r", encoding="utf-8") as f:
            js = json.load(f) or {}
        dk = js.get("day_key") or _today_utc_key()
        spent = float(js.get("spent_usd") or 0.0)
        if dk != _today_utc_key():
            return BudgetState(day_key=_today_utc_key(), spent_usd=0.0)
        return BudgetState(day_key=dk, spent_usd=spent)
    except Exception:
        return BudgetState(day_key=_today_utc_key(), spent_usd=0.0)


def _save_budget_state(st: BudgetState) -> None:
    os.makedirs("logs", exist_ok=True)
    with open(_budget_state_path(), "w", encoding="utf-8") as f:
        json.dump({"day_key": st.day_key, "spent_usd": st.spent_usd}, f)


def estimate_cost_usd(prompt_tokens: int, completion_tokens: int, *, per_1k_usd: float) -> float:
    # Simple estimator: (in+out)/1000 * rate
    return ((prompt_tokens + completion_tokens) / 1000.0) * float(per_1k_usd)


def budget_check_and_reserve(estimated_cost_usd: float) -> Tuple[bool, str]:
    """Returns (allowed, reason). Enforces soft/hard thresholds.
    - soft: allow but will annotate audit (caller should degrade behavior)
    - hard: reject
    """
    daily = float(getattr(settings, "llm_budget_daily_usd", 20.0) or 20.0)
    soft = float(getattr(settings, "llm_budget_soft_pct", 0.8) or 0.8)
    hard = float(getattr(settings, "llm_budget_hard_pct", 1.0) or 1.0)

    st = _load_budget_state()
    projected = st.spent_usd + max(0.0, float(estimated_cost_usd))
    if projected > daily * hard:
        return False, f"budget_hard_exceeded projected={projected:.2f} daily={daily:.2f}"
    # Reserve immediately to avoid thundering herd (best-effort, single-process)
    st.spent_usd = projected
    _save_budget_state(st)
    if projected > daily * soft:
        return True, f"budget_soft_exceeded projected={projected:.2f} daily={daily:.2f}"
    return True, "ok"


class TokenBucket:
    def __init__(self, rpm: int) -> None:
        self.capacity = max(1, int(rpm))
        self.tokens = float(self.capacity)
        self.fill_per_sec = float(self.capacity) / 60.0
        self.last = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = max(0.0, now - self.last)
        self.last = now
        self.tokens = min(float(self.capacity), self.tokens + elapsed * self.fill_per_sec)
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


_BUCKET: Optional[TokenBucket] = None


def rate_limit_allow() -> bool:
    global _BUCKET
    if _BUCKET is None:
        _BUCKET = TokenBucket(int(getattr(settings, "llm_rate_limit_rpm", 60) or 60))
    return _BUCKET.allow()


def _hash_payload(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def audit_log(event: Dict[str, Any]) -> None:
    if not bool(getattr(settings, "llm_audit_enabled", True)):
        return
    path = str(getattr(settings, "llm_audit_log_path", "logs/llm_audit.jsonl") or "logs/llm_audit.jsonl")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # redact obvious secrets in event
    ev = dict(event)
    for k in list(ev.keys()):
        if "key" in k.lower() or "token" in k.lower():
            ev[k] = "***redacted***"
    # stable envelope
    ev.setdefault("ts_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    append_jsonl_with_chain(path, ev)


def audit_prompt_fingerprint(prompt: str) -> str:
    # store only fingerprint to reduce privacy risk
    return _hash_payload(prompt[:4000])

class RateLimiter:
    """Global + per-provider RPM token buckets (in-memory).

    Env/config:
      - LLM_RATE_LIMIT_RPM: legacy fallback
      - LLM_RATE_LIMIT_RPM_GLOBAL: global bucket (default=LLM_RATE_LIMIT_RPM)
      - LLM_RATE_LIMIT_RPM_MAP: "gemini:60,anthropic:30,openai:30,glm:30"
    """

    def __init__(self) -> None:
        legacy = int(getattr(settings, "llm_rate_limit_rpm", 60) or 60)
        self.global_rpm = int(getattr(settings, "llm_rate_limit_rpm_global", legacy) or legacy)
        self.map_str = str(getattr(settings, "llm_rate_limit_rpm_map", "") or "").strip()
        self.buckets: Dict[str, TokenBucket] = {}
        self.global_bucket = TokenBucket(self.global_rpm)

    def _rpm_for(self, provider: str) -> int:
        legacy = int(getattr(settings, "llm_rate_limit_rpm", 60) or 60)
        if not self.map_str:
            return legacy
        m: Dict[str, int] = {}
        for part in self.map_str.split(","):
            part = part.strip()
            if not part or ":" not in part:
                continue
            k, v = part.split(":", 1)
            k = k.strip().lower()
            try:
                m[k] = int(v.strip())
            except Exception:
                continue
        return int(m.get(provider.lower(), legacy))

    def allow(self, provider: Optional[str] = None) -> bool:
        if not self.global_bucket.allow():
            return False
        if not provider:
            return True
        p = provider.lower()
        if p not in self.buckets:
            self.buckets[p] = TokenBucket(self._rpm_for(p))
        return self.buckets[p].allow()


_RATE_LIMITER: Optional[RateLimiter] = None


def rate_limit_allow(provider: Optional[str] = None) -> bool:
    """Compatibility: previously global only. Now supports per-provider as well."""
    global _RATE_LIMITER
    if _RATE_LIMITER is None:
        _RATE_LIMITER = RateLimiter()
    return _RATE_LIMITER.allow(provider)


def budget_soft_exceeded(reason: str) -> bool:
    return isinstance(reason, str) and reason.startswith("budget_soft_exceeded")

