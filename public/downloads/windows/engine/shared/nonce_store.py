from __future__ import annotations

import json
import os
import time
from typing import Optional

import redis

class NonceStore:
    """Replay protection store: NX set with TTL (Redis), with file fallback."""

    def __init__(self, redis_url: str, ttl_seconds: int, file_path: str = "/tmp/nexus_nonce_store.json"):
        self.ttl = int(ttl_seconds)
        self.file_path = file_path
        self.r: Optional[redis.Redis] = None
        try:
            self.r = redis.Redis.from_url(redis_url, decode_responses=True)
        except Exception:
            self.r = None

    def _file_load(self) -> dict:
        try:
            if not os.path.exists(self.file_path):
                return {}
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def _file_save(self, d: dict) -> None:
        os.makedirs(os.path.dirname(self.file_path) or ".", exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(d, f)

    def seen_or_mark(self, nonce: str) -> bool:
        """Returns True if nonce already seen (replay). Marks nonce otherwise."""
        nonce = (nonce or "").strip()
        if not nonce:
            return True

        # Redis path
        if self.r is not None:
            try:
                key = f"nonce:{nonce}"
                # SET key value NX EX ttl
                ok = self.r.set(key, "1", nx=True, ex=self.ttl)
                return (ok is None)  # None => already existed
            except Exception:
                # fall back
                pass

        # file fallback
        now = int(time.time())
        d = self._file_load()
        # purge
        cutoff = now - self.ttl
        d = {k: v for k, v in d.items() if isinstance(v, int) and v >= cutoff}
        if nonce in d:
            return True
        d[nonce] = now
        self._file_save(d)
        return False
