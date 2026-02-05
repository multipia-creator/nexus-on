#!/usr/bin/env python3
"""Generate callback headers for /agent/callback (v6.13)."""
from __future__ import annotations

import argparse
import json
import os
import secrets as _secrets
import time
import hmac
import hashlib

def sign(secret: str, timestamp: str, nonce: str, body: bytes) -> str:
    msg = (f"{timestamp}.{nonce}.").encode("utf-8") + body
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--secret", default=os.getenv("CALLBACK_SIGNATURE_SECRET",""))
    ap.add_argument("--key-id", default=os.getenv("CALLBACK_KEY_ID",""))
    ap.add_argument("--timestamp", default="")
    ap.add_argument("--nonce", default="")
    ap.add_argument("--body-json", required=True, help="Path to json file")
    args = ap.parse_args()

    if not args.secret:
        raise SystemExit("missing --secret or CALLBACK_SIGNATURE_SECRET")

    ts = args.timestamp or str(int(time.time()))
    nonce = args.nonce or _secrets.token_urlsafe(16)
    body_obj = json.load(open(args.body_json, "r", encoding="utf-8"))
    body = json.dumps(body_obj, ensure_ascii=False).encode("utf-8")
    sig = sign(args.secret, ts, nonce, body)

    print(f"X-Timestamp: {ts}")
    print(f"X-Nonce: {nonce}")
    print(f"X-Signature: {sig}")
    if args.key_id:
        print(f"X-Key-Id: {args.key_id}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
