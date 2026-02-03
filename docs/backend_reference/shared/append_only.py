from __future__ import annotations

import hashlib
import json
import os
import threading
from typing import Any, Dict, Optional

_LOCKS: Dict[str, threading.Lock] = {}

def _lock_for(path: str) -> threading.Lock:
    if path not in _LOCKS:
        _LOCKS[path] = threading.Lock()
    return _LOCKS[path]

def _sidecar_path(path: str) -> str:
    return path + ".chain"

def _canonical_json(ev: Dict[str, Any]) -> str:
    # stable encoding for hashing (do not use ensure_ascii to preserve unicode deterministically)
    return json.dumps(ev, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _read_last_hash(sidecar: str) -> str:
    try:
        if not os.path.exists(sidecar):
            return "0" * 64
        with open(sidecar, "r", encoding="utf-8") as f:
            h = (f.read() or "").strip()
        if len(h) == 64:
            return h
    except Exception:
        pass
    return "0" * 64

def _write_last_hash(sidecar: str, h: str) -> None:
    os.makedirs(os.path.dirname(sidecar) or ".", exist_ok=True)
    with open(sidecar, "w", encoding="utf-8") as f:
        f.write(h)

def append_jsonl_with_chain(path: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """Append event to JSONL file with an append-only hash chain.

    Adds:
      - chain_ver: 1
      - prev_hash: sha256 of previous record
      - hash: sha256(prev_hash + "\n" + canonical_json)
    Sidecar: <path>.chain holds the last hash for efficient append.

    NOTE:
      - Not a full WORM guarantee, but provides tamper-evidence and lightweight verification.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    sidecar = _sidecar_path(path)
    lk = _lock_for(path)
    with lk:
        prev = _read_last_hash(sidecar)
        ev = dict(event)
        ev.setdefault("chain_ver", 1)
        ev["prev_hash"] = prev
        payload = _canonical_json({k: v for k, v in ev.items() if k != "hash"})
        h = _sha256_hex(prev + "\n" + payload)
        ev["hash"] = h
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        _write_last_hash(sidecar, h)
        return ev

def verify_jsonl_chain(path: str) -> Dict[str, Any]:
    """Verify chain of <path>. Returns summary."""
    ok = True
    errors = []
    count = 0
    last = "0" * 64
    if not os.path.exists(path):
        return {"ok": False, "count": 0, "errors": [{"line": 0, "error": "missing_file"}]}
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception as e:
                ok = False
                errors.append({"line": idx, "error": f"json_parse:{e}"})
                continue
            prev_hash = str(ev.get("prev_hash") or "")
            h = str(ev.get("hash") or "")
            if len(prev_hash) != 64 or len(h) != 64:
                ok = False
                errors.append({"line": idx, "error": "missing_hash_fields"})
                continue
            if prev_hash != last:
                ok = False
                errors.append({"line": idx, "error": "prev_hash_mismatch"})
            payload = _canonical_json({k: v for k, v in ev.items() if k != "hash"})
            expected = _sha256_hex(prev_hash + "\n" + payload)
            if not hashlib.compare_digest(expected, h):
                ok = False
                errors.append({"line": idx, "error": "hash_mismatch"})
            last = h
            count += 1
    return {"ok": ok, "count": count, "errors": errors[:20], "last_hash": last}
