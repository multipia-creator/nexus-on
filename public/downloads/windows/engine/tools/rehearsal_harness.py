#!/usr/bin/env python3
"""NEXUS Operations Rehearsal Harness (v6.10)

This script executes a small set of "known-good" exercises to validate:
- LLM connectivity & logging (audit + cost ledger)
- Dedupe behavior
- Report generation
- Anomaly watcher dry-run / alert wiring

Notes
- Some scenarios (429 burst / breaker open) depend on real provider behavior or intentional misconfig.
  This harness supports "manual" modes for those, and records guidance.

Usage examples
- Baseline smoke (recommended first):
  python tools/rehearsal_harness.py smoke --prompt "hello"

- Dedupe test:
  python tools/rehearsal_harness.py dedupe --prompt "same prompt" --n 5

- Tagging test:
  python tools/rehearsal_harness.py tagging --prompt "tag test" --team ops --project finops

- Report test (today):
  python tools/rehearsal_harness.py report --from 2026-01-01 --to 2026-01-31

- Alert wiring (dry-run):
  python tools/rehearsal_harness.py anomaly --dry-run

"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from shared.logging_utils import get_logger
from shared.llm_client import LLMClient
from shared.settings import settings

logger = get_logger(__name__)


def _exists(path: str) -> bool:
    try:
        return os.path.exists(path)
    except Exception:
        return False


def _check_paths() -> dict:
    audit = str(getattr(settings, "llm_audit_log_path", "logs/llm_audit.jsonl") or "logs/llm_audit.jsonl")
    ledger = str(getattr(settings, "llm_cost_ledger_path", "logs/llm_cost_ledger.jsonl") or "logs/llm_cost_ledger.jsonl")
    return {"audit": audit, "ledger": ledger, "audit_exists": _exists(audit), "ledger_exists": _exists(ledger)}


def cmd_smoke(args) -> int:
    c = LLMClient()
    ctx = {"team": args.team, "project": args.project} if args.team or args.project else None
    res = c.generate(args.prompt, purpose=args.purpose, max_output_tokens=args.max_output_tokens, context=ctx)
    paths = _check_paths()
    out = {
        "ok": True,
        "provider": res.provider,
        "model": res.model,
        "text_preview": (res.text or "")[:120],
        "paths": paths,
    }
    print(out)
    return 0


def cmd_dedupe(args) -> int:
    c = LLMClient()
    ctx = {"team": args.team, "project": args.project} if args.team or args.project else None
    providers = []
    for i in range(args.n):
        res = c.generate(args.prompt, purpose=args.purpose, max_output_tokens=args.max_output_tokens, context=ctx)
        providers.append(res.provider)
    print({"ok": True, "n": args.n, "providers": providers, "note": "Check audit logs for llm_dedupe_hit entries and metrics dedupe hits."})
    return 0


def cmd_tagging(args) -> int:
    c = LLMClient()
    ctx = {"team": args.team, "project": args.project}
    res = c.generate(args.prompt, purpose=args.purpose, max_output_tokens=args.max_output_tokens, context=ctx)
    print({"ok": True, "team": args.team, "project": args.project, "provider": res.provider, "model": res.model})
    print("Verify: logs/llm_cost_ledger.jsonl includes team/project fields; Prometheus cost metric has the same labels.")
    return 0


def cmd_report(args) -> int:
    # shell out to finops_report tool
    import subprocess
    cmd = [sys.executable, "tools/finops_report.py", "--from", args.date_from, "--to", args.date_to, "--out", args.out]
    if args.ledger:
        cmd += ["--ledger", args.ledger]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print({"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "out": args.out})
    return r.returncode


def cmd_anomaly(args) -> int:
    import subprocess
    cmd = [sys.executable, "tools/anomaly_watch.py"]
    if args.dry_run:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, capture_output=True, text=True)
    print({"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()})
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("smoke")
    p.add_argument("--prompt", required=True)
    p.add_argument("--purpose", default="ops")
    p.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=128)
    p.add_argument("--team", default="")
    p.add_argument("--project", default="")
    p.set_defaults(fn=cmd_smoke)

    p = sub.add_parser("dedupe")
    p.add_argument("--prompt", required=True)
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--purpose", default="ops")
    p.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=128)
    p.add_argument("--team", default="")
    p.add_argument("--project", default="")
    p.set_defaults(fn=cmd_dedupe)

    p = sub.add_parser("tagging")
    p.add_argument("--prompt", required=True)
    p.add_argument("--purpose", default="ops")
    p.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=128)
    p.add_argument("--team", required=True)
    p.add_argument("--project", required=True)
    p.set_defaults(fn=cmd_tagging)

    p = sub.add_parser("report")
    p.add_argument("--from", dest="date_from", required=True)
    p.add_argument("--to", dest="date_to", required=True)
    p.add_argument("--ledger", default="")
    p.add_argument("--out", default="logs/finops_rehearsal.md")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("anomaly")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_anomaly)

    args = ap.parse_args()
    return int(args.fn(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
