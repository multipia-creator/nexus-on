#!/usr/bin/env python3
"""Verify WORM manifest signature (v6.15)."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json

def _hmac_hex(key: str, msg: bytes) -> str:
    return hmac.new(key.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--hmac-key", required=True)
    args = ap.parse_args()

    m = json.load(open(args.manifest, "r", encoding="utf-8"))
    sig = m.get("hmac_sha256")
    if not sig:
        print("missing hmac_sha256 in manifest")
        return 2
    m2 = dict(m)
    m2.pop("hmac_sha256", None)
    raw = json.dumps(m2, sort_keys=True).encode("utf-8")
    exp = _hmac_hex(args.hmac_key, raw)
    ok = (exp == sig)
    print("ok" if ok else "bad")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
