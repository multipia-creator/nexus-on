#!/usr/bin/env python3
"""Simple load generator for rehearsal (v6.10).

This intentionally avoids heavy dependencies. Use at low concurrency first.

Example:
  python tools/rehearsal_load_test.py --prompt "ping" --n 50 --concurrency 5 --purpose ops --team ops --project rehearsal
"""

from __future__ import annotations

import argparse
import queue
import threading
import time
from typing import Dict, List

from shared.llm_client import LLMClient


def worker(q: "queue.Queue[int]", results: List[Dict], client: LLMClient, prompt: str, purpose: str, max_out: int, ctx: Dict):
    while True:
        try:
            _ = q.get_nowait()
        except queue.Empty:
            return
        t0 = time.time()
        ok = True
        err = ""
        try:
            r = client.generate(prompt, purpose=purpose, max_output_tokens=max_out, context=ctx)
            provider = r.provider
            model = r.model
        except Exception as e:
            ok = False
            provider = "unknown"
            model = "unknown"
            err = f"{type(e).__name__}:{e}"
        dt = (time.time() - t0) * 1000.0
        results.append({"ok": ok, "latency_ms": dt, "provider": provider, "model": model, "error": err})
        q.task_done()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--purpose", default="ops")
    ap.add_argument("--max-output-tokens", dest="max_out", type=int, default=64)
    ap.add_argument("--team", default="ops")
    ap.add_argument("--project", default="rehearsal")
    args = ap.parse_args()

    q: "queue.Queue[int]" = queue.Queue()
    for i in range(args.n):
        q.put(i)

    client = LLMClient()
    results: List[Dict] = []
    ctx = {"team": args.team, "project": args.project}

    threads = []
    for _ in range(max(1, args.concurrency)):
        t = threading.Thread(target=worker, args=(q, results, client, args.prompt, args.purpose, args.max_out, ctx), daemon=True)
        t.start()
        threads.append(t)

    q.join()
    # summarize
    ok_n = sum(1 for r in results if r["ok"])
    fail_n = len(results) - ok_n
    lat = sorted([r["latency_ms"] for r in results if r["ok"]])
    p50 = lat[int(0.5 * (len(lat)-1))] if lat else 0.0
    p95 = lat[int(0.95 * (len(lat)-1))] if lat else 0.0
    print({"n": len(results), "ok": ok_n, "fail": fail_n, "p50_ms": p50, "p95_ms": p95})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
