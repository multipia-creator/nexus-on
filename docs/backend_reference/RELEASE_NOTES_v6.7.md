# RELEASE NOTES v6.4 — HTTP LLM adapters + unified settings + governance wired into LLMClient

## What changed

1. **Settings.py hard-fix (syntax + indentation)**
   - `shared/settings.py` was previously malformed (indentation broke `BaseSettings`).
   - Rewritten as a single, consistent `Settings` class.
   - Backward compatibility preserved (legacy env aliases like `LLM_PROVIDER`, `LLM_FALLBACKS`, `ZAI_MODEL`, `ZAI_BASE_URL`).

2. **Real provider calls (no SDK dependency)**
   - Added `shared/providers/http_providers.py` implementing raw-HTTP calls for:
     - Gemini `generateContent`
     - OpenAI Responses API `/responses`
     - Anthropic Messages API `/messages`
     - GLM OpenAI-compatible `/chat/completions`
   - Robust response extraction (`output_text`/content blocks/choices) + status-based error classification.

3. **Governance actually enforced where it matters (LLMClient)**
   - `shared/llm_client.py` now enforces:
     - global RPM rate limit
     - daily USD budget reservation
     - audit logging (attempt/success/fail)
     - circuit breaker (existing ProviderHealth)
   - Routing uses **new** vars first:
     - `LLM_PRIMARY_PROVIDER`, `LLM_FALLBACK_PROVIDERS`
     - falls back to `LLM_PROVIDER`, `LLM_FALLBACKS` if unset.

## New / updated environment variables

- Keys
  - `GEMINI_API_KEY`
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `GLM_API_KEY` (fallback: `ZAI_API_KEY`)

- Provider endpoints (optional)
  - `GEMINI_API_BASE` (default: `https://generativelanguage.googleapis.com/v1beta`)
  - `OPENAI_API_BASE` (default: `https://api.openai.com/v1`)
  - `ANTHROPIC_API_BASE` (default: `https://api.anthropic.com/v1`)
  - `GLM_API_BASE` (default: `https://open.bigmodel.cn/api/paas/v4`)
  - Legacy override: `ZAI_BASE_URL` can be the **full** chat completions URL.

- Governance
  - `LLM_RATE_LIMIT_RPM`
  - `LLM_BUDGET_DAILY_USD`
  - `LLM_AUDIT_LOG_PATH`

## Notes

- This patch intentionally avoids provider SDKs. If you prefer SDKs in production, keep the HTTP adapters as a deterministic fallback path.
- If you run behind a corporate proxy / gateway, set the `*_API_BASE` env vars accordingly.


---

## v6.5.0 API governance 100
- Adds per-provider + global rate limiting (LLM_RATE_LIMIT_RPM_GLOBAL, LLM_RATE_LIMIT_RPM_MAP).
- Retry-After aware cooldown: breaker opens for provider-specified duration on HTTP 429.
- Soft budget degrade policy: auto-reduce max_output_tokens and optional cheapest-first routing.
- ProviderHealth persistence: Redis-first, file fallback for restart-safe breaker state in single-node mode.
- Audit log enriched: est_cost_usd, max_output_tokens, retry_after_s (prompt stored as fingerprint only).


---

## v6.6.0 FinOps
- Adds cost ledger (logs/llm_cost_ledger.jsonl) and estimate settlement to budget_state.
- Adds fingerprint-based request dedupe (Redis-first, file fallback).
- Adds standardized backoff policy with Retry-After preference in provider HTTP calls.


---

## v6.7.0 FinOps++
- Model-specific pricing overrides via LLM_PRICING_JSON.
- Usage missing fallback token estimation (ledger marks approx_tokens=true).
- Purpose-based dedupe TTL policies via LLM_DEDUPE_TTL_MAP.
