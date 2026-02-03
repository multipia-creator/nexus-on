from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import redis


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class YouTubeQueueStore:
    """Tenant+session scoped YouTube queue backed by Redis."""

    def __init__(self, redis_url: str):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    def _k(self, tenant_id: str, session_id: str) -> str:
        return f"nexus:ytq:{tenant_id}:{session_id}"

    def _k_meta(self, tenant_id: str, session_id: str) -> str:
        return f"nexus:ytqmeta:{tenant_id}:{session_id}"

    def list(self, *, tenant_id: str, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        raw = self.r.lrange(self._k(tenant_id, session_id), 0, max(0, limit - 1))
        out: List[Dict[str, Any]] = []
        for s in raw:
            try:
                out.append(json.loads(s))
            except Exception:
                continue
        return out

    def add(self, *, tenant_id: str, session_id: str, item: Dict[str, Any], ttl_seconds: int = 86400) -> int:
        if "added_at" not in item:
            item["added_at"] = _utc_iso()
        k = self._k(tenant_id, session_id)
        self.r.rpush(k, json.dumps(item, ensure_ascii=False))
        self.r.expire(k, ttl_seconds)
        self.r.hset(self._k_meta(tenant_id, session_id), mapping={"updated_at": _utc_iso()})
        self.r.expire(self._k_meta(tenant_id, session_id), ttl_seconds)
        return int(self.r.llen(k))

    def pop_next(self, *, tenant_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        k = self._k(tenant_id, session_id)
        s = self.r.lpop(k)
        if not s:
            return None
        try:
            item = json.loads(s)
        except Exception:
            item = {"raw": s}
        self.r.hset(self._k_meta(tenant_id, session_id), mapping={"updated_at": _utc_iso()})
        return item

    def clear(self, *, tenant_id: str, session_id: str) -> None:
        self.r.delete(self._k(tenant_id, session_id))
        self.r.delete(self._k_meta(tenant_id, session_id))
