from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

from shared.settings import settings
from shared.metrics import llm_dedupe_hits_total, llm_dedupe_sets_total

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


@dataclass
class DedupeHit:
    key: str
    cached_text: str
    cached_provider: str
    cached_model: str
    age_s: float


class DedupeStore:
    """Request dedupe for LLM calls (fingerprint-based), with TTL.

    Redis-first; file fallback (single-node).
    """

    def __init__(self) -> None:
        self.ttl_s = int(getattr(settings, "llm_dedupe_ttl_s", 30) or 30)
        self.ttl_map = str(getattr(settings, "llm_dedupe_ttl_map", "") or "").strip()
        self.enabled = bool(getattr(settings, "llm_dedupe_enabled", True))
        self._redis = None
        if redis is not None:
            try:
                self._redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None
        self._file_path = "logs/dedupe_cache.json"

    def _rkey(self, k: str) -> str:
        return f"nexus:dedupe:{k}"

    def _file_load(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self._file_path):
                return {}
            with open(self._file_path, "r", encoding="utf-8") as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def _file_save(self, d: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self._file_path) or ".", exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(d, f)

    def _ttl_for_purpose(self, purpose: str) -> int:
        if not self.ttl_map:
            return self.ttl_s
        p = (purpose or "").strip().lower()
        m: Dict[str, int] = {}
        for part in self.ttl_map.split(","):
            part = part.strip()
            if not part or ":" not in part:
                continue
            k, v = part.split(":", 1)
            k = k.strip().lower()
            try:
                m[k] = int(v.strip())
            except Exception:
                continue
        return int(m.get(p, self.ttl_s))

    def get(self, key: str, purpose: str = "") -> Optional[DedupeHit]:
        if not self.enabled:
            return None
        now = time.time()
        ttl = self._ttl_for_purpose(purpose)
        raw: Optional[str] = None

        if self._redis is not None:
            try:
                raw = self._redis.get(self._rkey(key))
            except Exception:
                self._redis = None

        if raw is None:
            d = self._file_load()
            v = d.get(key)
            raw = json.dumps(v) if isinstance(v, dict) else None

        if not raw:
            return None

        try:
            v = json.loads(raw)
            ts = float(v.get("ts", 0.0))
            if now - ts > ttl:
                return None
            try:
                if llm_dedupe_hits_total is not None:
                    llm_dedupe_hits_total.labels(purpose=purpose or "default").inc()
            except Exception:
                pass

            return DedupeHit(
                key=key,
                cached_text=str(v.get("text") or ""),
                cached_provider=str(v.get("provider") or ""),
                cached_model=str(v.get("model") or ""),
                age_s=now - ts,
            )
        except Exception:
            return None

    def set(self, key: str, provider: str, model: str, text: str, purpose: str = "") -> None:
        if not self.enabled:
            return
        payload = {"ts": time.time(), "provider": provider, "model": model, "text": text}
        try:
            if llm_dedupe_sets_total is not None:
                llm_dedupe_sets_total.labels(purpose=purpose or "default").inc()
        except Exception:
            pass

        if self._redis is not None:
            try:
                self._redis.setex(self._rkey(key), self._ttl_for_purpose(purpose), json.dumps(payload))
                return
            except Exception:
                self._redis = None

        d = self._file_load()
        d[key] = payload
        self._file_save(d)

