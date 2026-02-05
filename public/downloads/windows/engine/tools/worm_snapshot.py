#!/usr/bin/env python3
"""Create WORM snapshots + signed manifest (v6.21).

This is intended for cron usage when WORM_ARCHIVE_MODE=cron.

Env:
  WORM_ARCHIVE_DIR=/mnt/worm
  WORM_MANIFEST_HMAC_KEY=... (optional but recommended)
  WORM_SNAPSHOT_GZIP=true|false

Usage:
  python tools/worm_snapshot.py logs/llm_audit.jsonl logs/llm_cost_ledger.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import time
import gzip
from datetime import datetime
from typing import List, Dict, Any

DEFAULT_INCLUDE = [
    # Core audit/ledger
    "logs/llm_audit.jsonl",
    "logs/llm_cost_ledger.jsonl",
    "logs/baseline_audit.jsonl",
    # Rehearsal evidence + scorecard
    "logs/character_rehearsal_evidence.jsonl",
    "logs/character_rehearsal_summary.json",
    "templates/REHEARSAL_SCORECARD_FILLED.md",
    # Baseline governance artifacts
    "tools/character_rehearsal_baseline.json",
    "logs/character_rehearsal_baseline_candidate.json",
    "tools/baseline_governance.json",
]

def _ts() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _hmac_hex(key: str, msg: bytes) -> str:
    return hmac.new(key.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def snapshot_file(src: str, dst_dir: str, gzip_on: bool) -> Dict[str, Any]:
    base = os.path.basename(src)
    suffix = _ts()
    if gzip_on:
        dst = os.path.join(dst_dir, f"{base}.{suffix}.jsonl.gz")
        with open(src, "rb") as f_in, gzip.open(dst, "wb") as f_out:
            f_out.write(f_in.read())
    else:
        dst = os.path.join(dst_dir, f"{base}.{suffix}.worm")
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            f_out.write(f_in.read())

    try:
        os.chmod(dst, 0o444)
    except Exception:
        pass

    return {"src": src, "dst": dst, "sha256": _sha256(dst)}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--default-set", action="store_true", help="Snapshot DEFAULT_INCLUDE when no paths provided")
    ap.add_argument("--archive-dir", default=os.getenv("WORM_ARCHIVE_DIR",""))
    ap.add_argument("--hmac-key", default=os.getenv("WORM_MANIFEST_HMAC_KEY",""))
    ap.add_argument("--gzip", default=os.getenv("WORM_SNAPSHOT_GZIP","true"))
    args = ap.parse_args()

    if not args.archive_dir:
        raise SystemExit("missing --archive-dir or WORM_ARCHIVE_DIR")

    gzip_on = str(args.gzip).lower() not in ("0","false","no")
    os.makedirs(args.archive_dir, exist_ok=True)

    # Determine snapshot targets
    targets = list(args.paths or [])
    if args.default_set or not targets:
        targets = list(DEFAULT_INCLUDE)

    items: List[Dict[str, Any]] = []
    for p in targets:
        if not os.path.exists(p):
            continue
        items.append(snapshot_file(p, args.archive_dir, gzip_on))

    manifest = {
        "ts": int(time.time()),
        "utc": _ts(),
        "gzip": gzip_on,
        "items": items,
    }
    raw = json.dumps(manifest, sort_keys=True).encode("utf-8")
    if args.hmac_key:
        manifest["hmac_sha256"] = _hmac_hex(args.hmac_key, raw)

    mpath = os.path.join(args.archive_dir, f"manifest.{_ts()}.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(mpath, 0o444)
    except Exception:
        pass

    print(mpath)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

# PR-07: baseline governance artifacts
