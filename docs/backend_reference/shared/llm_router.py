from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from shared.settings import settings
from shared.api_management import rate_limit_allow, budget_check_and_reserve, audit_log, audit_prompt_fingerprint


class LLMError(Exception):
    pass


def _providers_chain() -> List[str]:
    primary = (getattr(settings, "llm_primary_provider", "gemini") or "gemini").strip().lower()
    fall = (getattr(settings, "llm_fallback_providers", "") or "").strip().lower()
    chain = [primary] + [p.strip() for p in fall.split(",") if p.strip() and p.strip() != primary]
    # keep deterministic unique order
    seen = set()
    out: List[str] = []
    for p in chain:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _timeout() -> int:
    return int(getattr(settings, "llm_request_timeout_s", 60) or 60)


def _retries() -> int:
    return int(getattr(settings, "llm_max_retries", 2) or 2)


def _cost_rate(provider: str) -> float:
    # Conservative default (USD per 1k tokens). Override later if you want model-specific billing.
    # This is only used for budget enforcement heuristic.
    return {
        "gemini": 0.002,
        "openai": 0.010,
        "anthropic": 0.012,
        "glm": 0.006,
    }.get(provider, 0.010)


def _provider_key(provider: str) -> str:
    if provider == "gemini":
        return (getattr(settings, "gemini_api_key", "") or "").strip()
    if provider == "openai":
        return (getattr(settings, "openai_api_key", "") or "").strip()
    if provider == "anthropic":
        return (getattr(settings, "anthropic_api_key", "") or "").strip()
    if provider == "glm":
        return (getattr(settings, "glm_api_key", "") or "").strip()
    return ""


def llm_call(prompt: str, *, purpose: str, max_output_tokens: int = 512) -> Dict[str, Any]:
    """Minimal provider router (HTTP best-effort).
    This function is intentionally conservative: it enforces rate limit + budget and returns structured output.
    You can replace provider-specific calls with official SDKs later.
    """
    if not rate_limit_allow():
        audit_log({"type": "llm_reject", "reason": "rate_limited", "purpose": purpose})
        raise LLMError("rate_limited")

    # Rough budget reservation: assume prompt_tokens ~ len/4, completion ~ max_output_tokens
    prompt_tokens = max(1, int(len(prompt) / 4))
    est = ((prompt_tokens + max_output_tokens) / 1000.0) *  _cost_rate(_providers_chain()[0])
    ok, reason = budget_check_and_reserve(est)
    if not ok:
        audit_log({"type":"llm_reject", "reason": reason, "purpose": purpose})
        raise LLMError(reason)

    chain = _providers_chain()
    fp = audit_prompt_fingerprint(prompt)

    last_err: Optional[str] = None
    for provider in chain:
        key = _provider_key(provider)
        if not key:
            last_err = f"missing_api_key:{provider}"
            continue

        t0 = time.time()
        try:
            # Provider call placeholder: return echo-style stub to keep pipeline deterministic.
            # Replace with real API calls in your deployment layer.
            # We still log routing/audit to ensure governance.
            audit_log({
                "type":"llm_attempt",
                "provider": provider,
                "purpose": purpose,
                "prompt_fp": fp,
                "budget_note": reason,
            })
            # Stub "response"
            out = {
                "provider": provider,
                "ok": True,
                "text": f"[stub:{provider}] {prompt[:120]}",
                "meta": {"prompt_tokens_est": prompt_tokens, "max_output_tokens": max_output_tokens},
            }
            audit_log({
                "type":"llm_success",
                "provider": provider,
                "purpose": purpose,
                "prompt_fp": fp,
                "latency_ms": int((time.time()-t0)*1000),
            })
            return out
        except Exception as e:
            last_err = f"{provider}:{type(e).__name__}:{e}"
            audit_log({
                "type":"llm_fail",
                "provider": provider,
                "purpose": purpose,
                "prompt_fp": fp,
                "err": last_err,
                "latency_ms": int((time.time()-t0)*1000),
            })
            continue

    raise LLMError(last_err or "no_provider_succeeded")
