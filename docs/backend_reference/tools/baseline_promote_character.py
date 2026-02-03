#!/usr/bin/env python3
"""Promote character rehearsal baseline candidate to approved baseline (v6.23 / PR-09).

Two-step baseline governance:
  1) Generate candidate:
       python tools/character_rehearsal_autoscore.py --write_baseline
     -> logs/character_rehearsal_baseline_candidate.json
  2) Promote (manual, controlled):
       BASELINE_APPROVER=admin python tools/baseline_promote_character.py --candidate logs/character_rehearsal_baseline_candidate.json

Guards:
  - Candidate must be hard_gate_ok
  - missing_required_prefixes must be empty
  - Requires BASELINE_APPROVER in allowlist (tools/baseline_governance.json)
  - Optional token check (BASELINE_APPROVER_TOKEN) if require_token=true
  - Archives previous baseline to WORM archive dir
  - Appends audit event to logs/baseline_audit.jsonl with hash chain
"""
from __future__ import annotations

import argparse
import hashlib
import json
import traceback
import os
from datetime import datetime
from typing import Any, Dict

# Ensure repository root is importable when executed as a script
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
import sys
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from shared.append_only import append_jsonl_with_chain
from shared.worm_archive import archive_file
from shared.notify import notify

DEFAULT_BASELINE = "tools/character_rehearsal_baseline.json"
DEFAULT_GOV = "tools/baseline_governance.json"
DEFAULT_AUDIT = "logs/baseline_audit.jsonl"
DEFAULT_ERROR = "logs/baseline_promote_error.json"

def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, help="Baseline candidate JSON path")
    ap.add_argument("--baseline", default=DEFAULT_BASELINE, help="Approved baseline output path")
    ap.add_argument("--governance", default=DEFAULT_GOV, help="Governance config JSON")
    ap.add_argument("--audit", default=DEFAULT_AUDIT, help="Audit log JSONL (append-only chain)")
    ap.add_argument("--error", default=DEFAULT_ERROR, help="Error envelope JSON path (written on failure)")
    ap.add_argument("--worm-archive-dir", default=os.getenv("WORM_ARCHIVE_DIR", "worm_archive"), help="Archive dir for old baseline")
    args = ap.parse_args()

    approver = os.getenv("BASELINE_APPROVER", "").strip()
    token = os.getenv("BASELINE_APPROVER_TOKEN", "").strip()
    approver2 = os.getenv("BASELINE_APPROVER2", "").strip()
    token2 = os.getenv("BASELINE_APPROVER2_TOKEN", "").strip()

    if not approver:
        raise SystemExit("missing BASELINE_APPROVER env var")

    gov = _load_json(args.governance) if os.path.exists(args.governance) else {}
    allow = set(gov.get("approvers") or [])
    if allow and approver not in allow:
        raise SystemExit(f"approver not allowed: {approver}")


    # Optional two-person rule
    if gov.get("require_two_person"):
        if not approver2:
            raise SystemExit("missing BASELINE_APPROVER2 env var (two-person rule enabled)")
        if approver2 == approver:
            raise SystemExit("BASELINE_APPROVER2 must differ from BASELINE_APPROVER")
        allow2 = set(gov.get("approvers2") or gov.get("approvers") or [])
        if allow2 and approver2 not in allow2:
            raise SystemExit(f"approver2 not allowed: {approver2}")

    if gov.get("require_token"):
        expected = (gov.get("token_sha256") or "").strip()
        if not expected:
            raise SystemExit("governance requires token but token_sha256 missing in config")
        if hashlib.sha256(token.encode("utf-8")).hexdigest() != expected:
            raise SystemExit("invalid BASELINE_APPROVER_TOKEN")

    if gov.get("require_two_tokens"):
        expected2 = (gov.get("token2_sha256") or "").strip()
        if not expected2:
            raise SystemExit("governance requires 2nd token but token2_sha256 missing in config")
        if hashlib.sha256(token2.encode("utf-8")).hexdigest() != expected2:
            raise SystemExit("invalid BASELINE_APPROVER2_TOKEN")

    cand = _load_json(args.candidate)
    if not cand.get("hard_gate_ok"):
        raise SystemExit("candidate hard_gate_ok=false")
    if cand.get("missing_required_prefixes"):
        raise SystemExit(f"candidate missing prefixes: {cand.get('missing_required_prefixes')}")

    os.makedirs(os.path.dirname(args.baseline) or ".", exist_ok=True)
    old_sha = _sha256_file(args.baseline) if os.path.exists(args.baseline) else ""

    # Archive old baseline (if exists)
    archived = None
    if os.path.exists(args.baseline):
        archived = archive_file(args.baseline, args.worm_archive_dir, chmod_readonly=True)

    # Write new approved baseline
    cand2 = dict(cand)
    cand2["approved_at_utc"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    cand2["approved_by"] = approver
    with open(args.baseline, "w", encoding="utf-8") as f:
        json.dump(cand2, f, ensure_ascii=False, indent=2)

    new_sha = _sha256_file(args.baseline)

    # Append audit event with chain
    ev = {
        "ts_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": "baseline_promote",
        "component": "character_rehearsal",
        "approver": approver,
        "approver2": approver2 if gov.get("require_two_person") else None,
        "candidate_path": args.candidate,
        "baseline_path": args.baseline,
        "old_baseline_sha256": old_sha,
        "new_baseline_sha256": new_sha,
        "archived_path": archived,
    }
    append_jsonl_with_chain(args.audit, ev)
    print(f"[ok] promoted baseline -> {args.baseline}")
    print(f"[ok] audit appended -> {args.audit}")
    if archived:
        print(f"[ok] archived old baseline -> {archived}")
    return 0

def _write_error(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as se:
        # Notify only on non-zero exit codes (policy/guard failures)
        code = getattr(se, "code", 0)
        if code not in (0, None, True):
            try:
                msg = f"SystemExit({code})"
                env = {
                    "ts_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "event": "baseline_promote_failed",
                    "error": msg,
                    "traceback": "",
                }
                _write_error(DEFAULT_ERROR, env)
            except Exception:
                pass
            try:
                notify(f"SystemExit({code})", title="Baseline Promote Failed", event="baseline_promote_failed", severity="error", dedupe_key="baseline_promote_failed")
            except Exception:
                pass
        raise
    except Exception as e:
        tb = traceback.format_exc(limit=8)
        msg = f"{type(e).__name__}: {e}"
        env = {
            "ts_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": "baseline_promote_failed",
            "error": msg,
            "traceback": tb,
        }
        # Best-effort: write error envelope and notify
        try:
            # argparse is in main(); default path is fine if main didn't parse
            _write_error(DEFAULT_ERROR, env)
        except Exception:
            pass
        try:
            notify(msg, title="Baseline Promote Failed")
        except Exception:
            pass
        raise
