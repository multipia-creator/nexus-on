from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Any, Dict, List

from shared.settings import settings
from shared.provider_health import ProviderHealth
from shared.provider_keys import select_key
from shared.dedupe import DedupeStore
from shared.finops import estimate_cost_usd, write_cost_ledger, budget_adjust
from shared.api_management import budget_check_and_reserve, rate_limit_allow, audit_log, audit_prompt_fingerprint
from shared.metrics import (
    inc_llm_call,
    observe_llm_latency_ms,
    observe_llm_tokens,
    observe_llm_cost_usd,
)
from shared.providers.http_providers import (
    call_gemini_generate_content,
    call_openai_responses,
    call_anthropic_messages,
    call_glm_chat_completions,
    ProviderResponse,
)


@dataclass
class LLMResult:
    """Back-compat response object used across supervisor/tools."""

    ok: bool
    disabled: bool
    output_text: str
    provider: str
    model: str
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    failure_code: Optional[str] = None
    status_code: Optional[int] = None
    retry_after_s: Optional[int] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    cost_usd: Optional[float] = None

    # compatibility aliases
    @property
    def text(self) -> str:  # used by tools
        return self.output_text


def _default_chain() -> List[str]:
    primary = (getattr(settings, "llm_primary_provider", "gemini") or "gemini").strip().lower()
    fallbacks = (getattr(settings, "llm_fallback_providers", "") or "").strip()
    chain = [primary]
    if fallbacks:
        for p in fallbacks.split(","):
            p = p.strip().lower()
            if p and p not in chain:
                chain.append(p)
    # sanity
    return [p for p in chain if p in {"gemini", "openai", "anthropic", "glm"}] or ["gemini"]


def _model_for(provider: str, model_override: Optional[str]) -> str:
    if model_override:
        return model_override
    if provider == "gemini":
        return str(getattr(settings, "gemini_model", "gemini-1.5-pro") or "gemini-1.5-pro")
    if provider == "openai":
        return str(getattr(settings, "openai_model", "gpt-4.1-mini") or "gpt-4.1-mini")
    if provider == "anthropic":
        return str(getattr(settings, "anthropic_model", "claude-3-5-sonnet") or "claude-3-5-sonnet")
    if provider == "glm":
        return str(getattr(settings, "glm_model", "glm-4.7") or "glm-4.7")
    return str(model_override or "")


def _estimate_tokens(text: str) -> int:
    # crude char->token approximation; safe upper bound for budgeting
    return max(1, int(len(text) / 4))


def _call_provider(
    provider: str,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    timeout_s: float,
    temperature: float,
) -> ProviderResponse:
    if provider == "gemini":
        return call_gemini_generate_content(
            api_key=api_key,
            model=model,
            prompt=prompt,
            max_output_tokens=max_tokens,
            timeout_s=timeout_s,
            temperature=temperature,
        )
    if provider == "openai":
        return call_openai_responses(
            api_key=api_key,
            model=model,
            prompt=prompt,
            max_output_tokens=max_tokens,
            timeout_s=timeout_s,
            temperature=temperature,
        )
    if provider == "anthropic":
        return call_anthropic_messages(
            api_key=api_key,
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            timeout_s=timeout_s,
            temperature=temperature,
        )
    if provider == "glm":
        return call_glm_chat(
            api_key=api_key,
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            timeout_s=timeout_s,
            temperature=temperature,
        )
    return ProviderResponse(
        ok=False,
        provider=provider,
        model=model,
        text="",
        error=f"unsupported_provider:{provider}",
        status_code=400,
        failure_code="UNSUPPORTED_PROVIDER",
    )


def _should_retry(resp: ProviderResponse) -> bool:
    if resp.ok:
        return False
    code = (resp.failure_code or "").upper()
    # transient / retriable
    return code in {
        "RATE_LIMITED",
        "TIMEOUT",
        "NETWORK_ERROR",
        "UPSTREAM_5XX",
        "BAD_REQUEST",  # sometimes transient schema issues; allow one retry
        "UNKNOWN_ERROR",
    }


class LLMClient:
    def __init__(self, vault: Any = None) -> None:
        self.vault = vault
        self.health = ProviderHealth()
        self.dedupe = DedupeStore()

    def generate(
        self,
        input_text: str,
        purpose: str = "default",
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        max_output_tokens: Optional[int] = None,
        timeout_s: Optional[float] = None,
        cache_ttl_s: Optional[int] = None,
        tenant: Optional[dict] = None,
        **_: Any,
    ) -> LLMResult:
        provider_override = (provider_override or "").strip().lower() or None
        chain = [provider_override] if provider_override else _default_chain()

        mt = int(max_tokens if max_tokens is not None else (max_output_tokens if max_output_tokens is not None else 512))
        mt = max(1, min(mt, 8192))

        tmo = float(timeout_s if timeout_s is not None else (getattr(settings, "llm_request_timeout_s", 30.0) or 30.0))
        temperature = float(temperature if temperature is not None else 0.2)

        # rate limit (global)
        if not rate_limit_allow():
            return LLMResult(
                ok=False,
                disabled=True,
                output_text="",
                provider=chain[0],
                model=_model_for(chain[0], model_override),
                error="rate_limited_global",
                failure_code="RATE_LIMITED",
                status_code=429,
            )

        # dedupe key
        fp = audit_prompt_fingerprint(f"{tenant or {}}|{purpose}|{provider_override or ''}|{model_override or ''}|{input_text}")
        hit = self.dedupe.get(fp, purpose=purpose)
        if hit is not None:
            return LLMResult(
                ok=True,
                disabled=False,
                output_text=hit.cached_text,
                provider=hit.cached_provider or (chain[0] if chain else ""),
                model=hit.cached_model or _model_for(chain[0], model_override),
                latency_ms=0,
            )

        # pre-budget reservation (rough)
        est_in = _estimate_tokens(input_text)
        est_out = mt
        # estimate with primary provider model; for chain this is a rough upper bound
        est_provider = chain[0]
        est_model = _model_for(est_provider, model_override)
        est_cost = float(estimate_cost_usd(est_provider, est_model, est_in, est_out) or 0.0)
        allowed, budget_reason = budget_check_and_reserve(est_cost)
        if not allowed:
            audit_log(
                {
                    "event": "llm_budget_reject",
                    "purpose": purpose,
                    "provider": est_provider,
                    "model": est_model,
                    "estimated_cost_usd": est_cost,
                    "reason": budget_reason,
                    "tenant": tenant or {},
                    "fp": fp,
                }
            )
            return LLMResult(
                ok=False,
                disabled=True,
                output_text="",
                provider=est_provider,
                model=est_model,
                error=budget_reason,
                failure_code="BUDGET_EXCEEDED",
                status_code=402,
            )

        retries = int(getattr(settings, "llm_max_retries", 2) or 2)
        backoff_s = float(getattr(settings, "llm_retry_backoff_s", 0.8) or 0.8)

        last: Optional[ProviderResponse] = None
        started_global = time.monotonic()

        for provider in chain:
            provider = provider.strip().lower()
            if not provider:
                continue

            if not self.health.allow(provider):
                last = ProviderResponse(
                    ok=False,
                    provider=provider,
                    model=_model_for(provider, model_override),
                    text="",
                    error="circuit_open",
                    status_code=503,
                    failure_code="CIRCUIT_OPEN",
                )
                continue

            sel = select_key(provider, tenant=tenant, vault=self.vault)
            if sel.missing or not sel.api_key:
                last = ProviderResponse(
                    ok=False,
                    provider=provider,
                    model=_model_for(provider, model_override),
                    text="",
                    error=f"missing_api_key:{sel.missing}",
                    status_code=401,
                    failure_code="PROVIDER_DISABLED",
                )
                self.health.record_failure(provider, last.failure_code, retry_after_s=60)
                continue

            model = _model_for(provider, model_override)

            attempt = 0
            while True:
                attempt += 1
                resp = _call_provider(provider, sel.api_key, model, input_text, mt, tmo, temperature)
                last = resp

                try:
                    inc_llm_call(provider, purpose, status="ok" if resp.ok else "error")
                except Exception:
                    pass

                if resp.latency_ms is not None:
                    try:
                        observe_llm_latency_ms(provider, purpose, int(resp.latency_ms))
                    except Exception:
                        pass

                if resp.ok:
                    self.health.record_success(provider)

                    # usage / cost
                    tokens_in = None
                    tokens_out = None
                    if resp.usage:
                        tokens_in = int(resp.usage.get("input_tokens") or resp.usage.get("prompt_tokens") or 0) or None
                        tokens_out = int(resp.usage.get("output_tokens") or resp.usage.get("completion_tokens") or 0) or None

                    actual_cost = None
                    if tokens_in is not None and tokens_out is not None:
                        try:
                            actual_cost = float(estimate_cost_usd(provider, model, tokens_in, tokens_out) or 0.0)
                        except Exception:
                            actual_cost = None

                    # settle budget delta
                    if actual_cost is not None:
                        try:
                            budget_adjust(actual_cost - est_cost)
                        except Exception:
                            pass

                    # cost ledger (best-effort)
                    try:
                        write_cost_ledger(
                            {
                                "ts": time.time(),
                                "purpose": purpose,
                                "provider": provider,
                                "model": model,
                                "fp": fp,
                                "tenant": tenant or {},
                                "estimated_cost_usd": est_cost,
                                "actual_cost_usd": actual_cost,
                                "tokens_in": tokens_in,
                                "tokens_out": tokens_out,
                                "latency_ms": resp.latency_ms,
                                "budget_reason": budget_reason,
                                "key_id": sel.key_id,
                            }
                        )
                    except Exception:
                        pass

                    if tokens_in is not None and tokens_out is not None:
                        try:
                            observe_llm_tokens(provider, purpose, tokens_in, tokens_out)
                        except Exception:
                            pass
                    if actual_cost is not None:
                        try:
                            observe_llm_cost_usd(provider, purpose, actual_cost)
                        except Exception:
                            pass

                    # audit
                    audit_log(
                        {
                            "event": "llm_generate",
                            "purpose": purpose,
                            "provider": provider,
                            "model": model,
                            "latency_ms": resp.latency_ms,
                            "fp": fp,
                            "tenant": tenant or {},
                            "key_id": sel.key_id,
                            "status": "ok",
                            "budget_reason": budget_reason,
                        }
                    )

                    # set dedupe
                    try:
                        self.dedupe.set(fp, provider=provider, model=model, text=resp.text, purpose=purpose)
                    except Exception:
                        pass

                    return LLMResult(
                        ok=True,
                        disabled=False,
                        output_text=resp.text,
                        provider=provider,
                        model=model,
                        latency_ms=resp.latency_ms,
                        tokens_in=tokens_in,
                        tokens_out=tokens_out,
                        cost_usd=actual_cost,
                    )

                # failure
                self.health.record_failure(provider, resp.failure_code, resp.retry_after_s)

                audit_log(
                    {
                        "event": "llm_generate",
                        "purpose": purpose,
                        "provider": provider,
                        "model": model,
                        "latency_ms": resp.latency_ms,
                        "fp": fp,
                        "tenant": tenant or {},
                        "key_id": sel.key_id,
                        "status": "error",
                        "failure_code": resp.failure_code,
                        "status_code": resp.status_code,
                        "error": resp.error,
                    }
                )

                if attempt <= retries and _should_retry(resp):
                    sleep_s = backoff_s * (2 ** (attempt - 1))
                    if resp.retry_after_s is not None:
                        sleep_s = max(sleep_s, float(resp.retry_after_s))
                    time.sleep(min(sleep_s, 5.0))
                    continue

                break

        # no provider succeeded
        provider = last.provider if last is not None else (chain[0] if chain else "gemini")
        model = last.model if last is not None else _model_for(provider, model_override)

        # settle reservation: when all fail, we should refund reservation (best-effort)
        try:
            budget_adjust(-est_cost)
        except Exception:
            pass

        audit_log(
            {
                "event": "llm_generate_final_fail",
                "purpose": purpose,
                "provider": provider,
                "model": model,
                "latency_ms": int((time.monotonic() - started_global) * 1000),
                "fp": fp,
                "tenant": tenant or {},
                "failure_code": getattr(last, "failure_code", None),
                "status_code": getattr(last, "status_code", None),
                "error": getattr(last, "error", None),
            }
        )

        return LLMResult(
            ok=False,
            disabled=True,
            output_text="",
            provider=provider,
            model=model,
            latency_ms=int((time.monotonic() - started_global) * 1000),
            error=getattr(last, "error", "llm_failed") if last is not None else "llm_failed",
            failure_code=getattr(last, "failure_code", "LLM_FAILED") if last is not None else "LLM_FAILED",
            status_code=getattr(last, "status_code", 503) if last is not None else 503,
            retry_after_s=getattr(last, "retry_after_s", None) if last is not None else None,
        )
