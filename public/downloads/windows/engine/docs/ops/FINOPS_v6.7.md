# FinOps (v6.7) — Model pricing + usage fallback + cache policies

1) Model-specific pricing
- Use LLM_PRICING_JSON to override USD/1k token rates.
- Supports provider defaults and model overrides.

2) Usage missing fallback
- If provider response has no usage, NEXUS estimates token counts using a conservative heuristic.
- Ledger records approx_tokens=true for transparency.

3) Cache policies
- Dedupe TTL can be configured per purpose:
  - LLM_DEDUPE_TTL_MAP=default:30,ops:15,autofix:10
