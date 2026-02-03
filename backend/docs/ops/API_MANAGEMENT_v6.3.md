# API Management (v6.3)

Why this matters
- LLM/3rd-party APIs are the primary operational risk: cost runaway, key leakage, rate limits, and silent degradation.
- NEXUS uses an explicit governance layer:
  - key custody (secrets)
  - routing (primary + fallbacks)
  - budgets (soft/hard)
  - rate limiting (token bucket)
  - audit logging (JSONL)

Config (env)
- LLM_PRIMARY_PROVIDER=gemini|openai|anthropic|glm
- LLM_FALLBACK_PROVIDERS=openai,anthropic,glm
- LLM_RATE_LIMIT_RPM=60
- LLM_BUDGET_DAILY_USD=20
- LLM_BUDGET_SOFT_PCT=0.8
- LLM_BUDGET_HARD_PCT=1.0
- LLM_AUDIT_ENABLED=true
- LLM_AUDIT_LOG_PATH=logs/llm_audit.jsonl

Secrets (never commit)
- GEMINI_API_KEY
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GLM_API_KEY

Operational policies
1) Key rotation
- Rotate keys on a fixed cadence (e.g., monthly) or immediately on suspected exposure.
- Keep "N+1" keys ready during rotation window.
- Verify: run scripts/smoke_test.py with LLM_AUDIT_ENABLED=true and ensure provider routing works.

2) Least privilege
- Use provider-scoped keys when available.
- For GitHub token: restrict to repo + issues + checks read as needed.

3) Budget governance
- Soft threshold: allow but degrade (optional). Hard threshold: block.
- You can wire 'soft exceeded' to post an ops warning comment or webhook.

4) Audit logging
- Only prompt fingerprints are stored (sha256 short) to reduce privacy exposure.
- Store provider, purpose, latency, and outcome for incident response and cost allocation.

Implementation notes
- shared/api_management.py: rate limit + budget store + audit log
- shared/llm_router.py: provider chain and structured call surface (currently stubbed; replace with SDK in deployment)

