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
