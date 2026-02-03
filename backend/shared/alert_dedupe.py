from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import redis

from shared.settings import settings


@dataclass
class DedupeResult:
    allowed: bool
    ttl_seconds: int


class AlertDedupe:
    """Redis-backed dedupe to suppress repeated alerts within a cooldown window."""

    def __init__(self):
        self.r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = int(getattr(settings, "alert_dedupe_ttl_seconds", 900))  # default 15m

    def _key(self, dedupe_key: str) -> str:
        return f"nexus:alertdedupe:{dedupe_key}"

    def allow(self, dedupe_key: str) -> DedupeResult:
        key = self._key(dedupe_key)
        # set if not exists
        ok = self.r.set(key, str(int(time.time())), ex=self.ttl, nx=True)
        if ok:
            return DedupeResult(True, self.ttl)
        ttl = self.r.ttl(key)
        return DedupeResult(False, int(ttl) if ttl and ttl > 0 else 0)
