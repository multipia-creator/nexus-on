from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import redis

from shared.settings import settings

@dataclass
class LockState:
    locked: bool
    ttl_seconds: int

class TaskLock:
    """Redis-backed lock to prevent infinite retry loops (per task_id)."""

    def __init__(self):
        self.r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = int(getattr(settings, "task_lock_ttl_seconds", 900))  # default 15m

    def _key(self, task_id: str) -> str:
        return f"nexus:tasklock:{task_id}"

    def is_locked(self, task_id: str) -> LockState:
        key = self._key(task_id)
        ttl = self.r.ttl(key)
        if ttl is None or ttl < 0:
            return LockState(False, 0)
        return LockState(True, int(ttl))

    def lock(self, task_id: str) -> None:
        self.r.set(self._key(task_id), str(int(time.time())), ex=self.ttl, nx=True)
