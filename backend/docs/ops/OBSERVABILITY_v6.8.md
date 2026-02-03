# Observability (v6.8)

Metrics (Prometheus)
- nexus_llm_cost_usd_total{provider,model,purpose,team,project,approx}
- nexus_llm_dedupe_hits_total{purpose}
- nexus_llm_dedupe_sets_total{purpose}
- nexus_llm_breaker_open{provider}
- Existing: llm_call_total / llm_call_fail_total / llm_call_latency

Suggested alerts
1) Breaker open too long
- nexus_llm_breaker_open == 1 for > 5m

2) Cost spike
- rate(nexus_llm_cost_usd_total[15m]) > X

3) 429 burst
- increase(llm_call_fail_total{reason="PROVIDER_RATE_LIMIT"}[10m]) > N

4) Dedupe hit ratio low (optional)
- nexus_llm_dedupe_hits_total / nexus_llm_dedupe_sets_total < threshold
