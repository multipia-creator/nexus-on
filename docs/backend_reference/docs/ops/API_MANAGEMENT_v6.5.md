# API Management (v6.5) — Governance 100

This release closes the operational loop for multi-LLM environments (Gemini-first + optional OpenAI/Anthropic/GLM).

## What’s new (vs v6.4)
1) Per-provider RPM + global RPM
- Global token bucket: LLM_RATE_LIMIT_RPM_GLOBAL
- Provider token buckets: LLM_RATE_LIMIT_RPM_MAP="gemini:60,anthropic:30,openai:30,glm:30"

2) Retry-After aware breaker
- When a provider returns HTTP 429 with Retry-After, the circuit breaker opens for that duration (best-effort).
- Prevents immediate re-hammering and reduces noisy alerts.

3) Soft budget degrade (policy-backed)
- If daily budget crosses soft threshold, NEXUS automatically reduces max_output_tokens.
- Optionally reorders provider chain by cheapest-first.

4) Breaker persistence without Redis
- ProviderHealth uses Redis when available.
- If Redis is unavailable, it falls back to logs/provider_breaker_state.json (restart-safe in single-node mode).

5) Audit logs enriched
- Records est_cost_usd / max_output_tokens / retry_after_s, plus prompt fingerprint (not raw prompt).

## Configuration
Required
- GEMINI_API_KEY (and optional: OPENAI_API_KEY, ANTHROPIC_API_KEY, GLM_API_KEY)

Governance
- LLM_RATE_LIMIT_RPM_GLOBAL=60
- LLM_RATE_LIMIT_RPM_MAP=gemini:60,anthropic:30,openai:30,glm:30
- LLM_BUDGET_DAILY_USD=20
- LLM_BUDGET_SOFT_PCT=0.8
- LLM_BUDGET_HARD_PCT=1.0
- LLM_SOFT_DEGRADE_MAX_OUTPUT_TOKENS=256
- LLM_SOFT_DEGRADE_PREFER_CHEAPEST=true
- LLM_AUDIT_ENABLED=true
- LLM_AUDIT_LOG_PATH=logs/llm_audit.jsonl

## Operational checklist
- Rotate keys monthly (or immediately upon suspected exposure).
- Watch audit logs for repeated 429/5xx to spot quota issues.
- Use budget soft threshold to force degraded mode before hitting hard-stop.


## v6.6 additions
- LLM_COST_LEDGER_PATH, LLM_DEDUPE_ENABLED, LLM_DEDUPE_TTL_S
- logs/llm_cost_ledger.jsonl for cost tracking.
