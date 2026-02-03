# FinOps (v6.6)

Goals
- Prevent cost runaway (budget gates).
- Measure usage and settle estimates to actual (best-effort).
- Reduce duplicate calls (dedupe).
- Standardize transient retry behavior (backoff).

What’s included
1) Cost settlement
- On successful LLM calls, NEXUS extracts token usage (best-effort) and writes a ledger:
  - logs/llm_cost_ledger.jsonl
- Budget is reserved by estimate at call time, and then settled by (actual - estimate) delta.

2) Dedupe cache
- Fingerprint-based dedupe for short window to prevent repeated identical expensive calls.
- Redis-first, file fallback (logs/dedupe_cache.json).

3) Standard backoff
- shared/backoff.py defines a single retry curve.
- Providers respect Retry-After if present, otherwise use backoff curve.

Config
- LLM_COST_LEDGER_PATH=logs/llm_cost_ledger.jsonl
- LLM_DEDUPE_ENABLED=true
- LLM_DEDUPE_TTL_S=30


## v6.7 additions
- Model-specific pricing via LLM_PRICING_JSON (provider default + model override)
- Usage-missing fallback token estimation (approx_tokens=true)
- Purpose-based dedupe TTL via LLM_DEDUPE_TTL_MAP
