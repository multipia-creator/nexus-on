#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from collections import defaultdict
from typing import Any, Dict, Tuple

def parse_ts(ts: str) -> datetime:
    # expected: 2026-01-31T12:34:56Z
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def load_jsonl(path: str):
    if not os.path.exists(path):
        return []
    out = []
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="date_from", default=None, help="YYYY-MM-DD (UTC)")
    ap.add_argument("--to", dest="date_to", default=None, help="YYYY-MM-DD (UTC, inclusive)")
    ap.add_argument("--ledger", default="logs/llm_cost_ledger.jsonl")
    ap.add_argument("--out", default="logs/finops_report.md")
    args = ap.parse_args()

    rows = load_jsonl(args.ledger)
    if not rows:
        print("No ledger rows found.")
        return

    dfrom = datetime.min.replace(tzinfo=timezone.utc)
    dto = datetime.max.replace(tzinfo=timezone.utc)
    if args.date_from:
        dfrom = datetime.strptime(args.date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if args.date_to:
        # inclusive end day
        dto = datetime.strptime(args.date_to, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        dto = dto.replace(hour=23, minute=59, second=59)

    filt = []
    for r in rows:
        ts = r.get("ts_utc")
        if not ts:
            continue
        try:
            t = parse_ts(ts)
        except Exception:
            continue
        if dfrom <= t <= dto:
            filt.append(r)

    totals = defaultdict(float)
    by_provider = defaultdict(float)
    by_model = defaultdict(float)
    by_purpose = defaultdict(float)
    by_team = defaultdict(float)
    approx_count = 0
    n = 0

    for r in filt:
        n += 1
        cost = float(r.get("actual_cost_usd") or 0.0)
        totals["total"] += cost
        by_provider[str(r.get("provider") or "unknown")] += cost
        by_model[str(r.get("model") or "unknown")] += cost
        by_purpose[str(r.get("purpose") or "default")] += cost
        by_team[f"{r.get('team','default')}/{r.get('project','nexus')}"] += cost
        if r.get("approx_tokens"):
            approx_count += 1

    def topk(d, k=10):
        return sorted(d.items(), key=lambda x: x[1], reverse=True)[:k]

    lines = []
    lines.append("# FinOps Report")
    lines.append(f"Window (UTC): {dfrom.date()} to {dto.date()}")
    lines.append(f"Rows: {n}")
    lines.append(f"Total cost (USD): {totals['total']:.4f}")
    lines.append(f"Approx token rows: {approx_count} ({(approx_count/max(1,n))*100:.1f}%)")
    lines.append("")
    lines.append("## Top providers")
    for k,v in topk(by_provider, 10):
        lines.append(f"- {k}: ${v:.4f}")
    lines.append("")
    lines.append("## Top models")
    for k,v in topk(by_model, 10):
        lines.append(f"- {k}: ${v:.4f}")
    lines.append("")
    lines.append("## Top purposes")
    for k,v in topk(by_purpose, 10):
        lines.append(f"- {k}: ${v:.4f}")
    lines.append("")
    lines.append("## Team/Project")
    for k,v in topk(by_team, 20):
        lines.append(f"- {k}: ${v:.4f}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
