from prometheus_client import Counter, Histogram

# Existing metrics in supervisor may import these.
# LLM provider metrics
llm_call_total = Counter("nexus_llm_call_total", "LLM calls", ["provider", "model"])
llm_call_fail_total = Counter("nexus_llm_call_fail_total", "LLM call failures", ["provider", "model", "reason"])
llm_call_latency_seconds = Histogram("nexus_llm_call_latency_seconds", "LLM call latency", ["provider", "model"])


# v6.8 FinOps dashboard metrics
try:
    from prometheus_client import Counter, Gauge
    llm_cost_usd_total = Counter(
        "nexus_llm_cost_usd_total",
        "Total LLM cost in USD (actual or estimated)",
        ["provider", "model", "purpose", "team", "project", "approx"],
    )
    llm_dedupe_hits_total = Counter(
        "nexus_llm_dedupe_hits_total",
        "Total dedupe hits (request-level cache)",
        ["purpose"],
    )
    llm_dedupe_sets_total = Counter(
        "nexus_llm_dedupe_sets_total",
        "Total dedupe sets (request-level cache)",
        ["purpose"],
    )
    llm_breaker_open = Gauge(
        "nexus_llm_breaker_open",
        "Circuit breaker open state (1=open, 0=closed)",
        ["provider"],
    )
except Exception:  # pragma: no cover
    llm_cost_usd_total = None
    llm_dedupe_hits_total = None
    llm_dedupe_sets_total = None
    llm_breaker_open = None

# ---- Helper functions (v7.x compatibility) ----

def inc_llm_call(provider: str, model: str) -> None:
    try:
        llm_call_total.labels(provider=provider, model=model).inc()
    except Exception:
        pass


def inc_llm_call_fail(provider: str, model: str, reason: str) -> None:
    try:
        llm_call_fail_total.labels(provider=provider, model=model, reason=reason).inc()
    except Exception:
        pass


def observe_llm_latency_ms(provider: str, model: str, latency_ms: int) -> None:
    try:
        llm_call_latency_seconds.labels(provider=provider, model=model).observe(max(0.0, float(latency_ms)) / 1000.0)
    except Exception:
        pass


def observe_llm_tokens(provider: str, model: str, tokens_in: int | None, tokens_out: int | None) -> None:
    # Token histograms are not yet standardized in supervisor metrics.
    # Keep as a no-op for now.
    return


def observe_llm_cost_usd(provider: str, model: str, purpose: str, team: str | None, project: str | None, cost_usd: float, approx: bool) -> None:
    if llm_cost_usd_total is None:
        return
    try:
        llm_cost_usd_total.labels(
            provider=provider,
            model=model,
            purpose=purpose,
            team=team or "",
            project=project or "",
            approx="1" if approx else "0",
        ).inc(max(0.0, float(cost_usd)))
    except Exception:
        pass


def inc_llm_dedupe_hit(purpose: str) -> None:
    if llm_dedupe_hits_total is None:
        return
    try:
        llm_dedupe_hits_total.labels(purpose=purpose).inc()
    except Exception:
        pass


def inc_llm_dedupe_set(purpose: str) -> None:
    if llm_dedupe_sets_total is None:
        return
    try:
        llm_dedupe_sets_total.labels(purpose=purpose).inc()
    except Exception:
        pass


def set_llm_breaker_open(provider: str, is_open: bool) -> None:
    if llm_breaker_open is None:
        return
    try:
        llm_breaker_open.labels(provider=provider).set(1.0 if is_open else 0.0)
    except Exception:
        pass
