#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from shared.append_only import verify_jsonl_chain

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="jsonl path to verify")
    args = ap.parse_args()
    res = verify_jsonl_chain(args.path)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if not res.get("ok"):
        raise SystemExit(2)

if __name__ == "__main__":
    main()
