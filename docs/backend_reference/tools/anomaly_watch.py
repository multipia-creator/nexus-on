#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from shared.settings import settings
from shared.notify import notify

LEDGER_DEFAULT = "logs/llm_cost_ledger.jsonl"
AUDIT_DEFAULT = "logs/llm_audit.jsonl"


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=LEDGER_DEFAULT)
    ap.add_argument("--audit", default=AUDIT_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    window_min = int(getattr(settings, "anomaly_window_min", 15) or 15)
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=window_min)

    ledger = [r for r in load_jsonl(args.ledger) if r.get("ts_utc")]
    recent_cost = [r for r in ledger if since <= parse_ts(r["ts_utc"]) <= now]

    total_cost = sum(float(r.get("actual_cost_usd") or 0.0) for r in recent_cost)
    rate_threshold = float(getattr(settings, "anomaly_cost_usd_rate_threshold", 2.0) or 2.0)
    cost_spike = total_cost >= rate_threshold

    # 429 burst from audit (llm_fail with reason PROVIDER_RATE_LIMIT)
    audit = [r for r in load_jsonl(args.audit) if r.get("ts_utc")]
    recent_audit = [r for r in audit if since <= parse_ts(r["ts_utc"]) <= now]
    rate_limit_fails = sum(1 for r in recent_audit if r.get("type") in ("llm_fail", "llm_provider_error") and r.get("reason") == "PROVIDER_RATE_LIMIT")
    burst_threshold = int(getattr(settings, "anomaly_429_burst_threshold", 20) or 20)
    burst_429 = rate_limit_fails >= burst_threshold

    # breaker open minutes: infer by provider_health state file if present
    breaker_open_min = int(getattr(settings, "anomaly_breaker_open_min", 5) or 5)
    breaker_alerts = []
    # check file fallback state
    state_paths = [
        "logs/provider_breaker_state.json",
        "logs/provider_health_state.json",
    ]
    state = {}
    for p in state_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    state = json.load(f) or {}
                break
            except Exception:
                state = {}
    # state format: provider -> {open_until, ...}
    now_ts = time.time()
    for prov, st in (state or {}).items():
        try:
            open_until = float((st or {}).get("open_until") or 0.0)
            if open_until > now_ts and (open_until - now_ts) >= breaker_open_min * 60:
                breaker_alerts.append((prov, int((open_until - now_ts) // 60)))
        except Exception:
            continue

    if not (cost_spike or burst_429 or breaker_alerts):
        return

    lines = []
    lines.append(f"Window: last {window_min}m (UTC)")
    if cost_spike:
        lines.append(f"- COST spike: ${total_cost:.4f} >= threshold ${rate_threshold:.2f}")
    if burst_429:
        lines.append(f"- 429 burst: {rate_limit_fails} >= threshold {burst_threshold}")
    if breaker_alerts:
        for prov, mins in breaker_alerts:
            lines.append(f"- Breaker open: {prov} (remaining ~{mins}m)")

    msg = "\n".join(lines)
    if args.dry_run:
        print(msg)
        return

    prefer = str(getattr(settings, "notify_prefer", "slack") or "slack")
    notify(msg, title="NEXUS anomaly", prefer=prefer)


if __name__ == "__main__":
    main()
