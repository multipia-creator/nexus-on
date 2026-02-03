import json
import os
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.settings import settings
from shared.logging_utils import get_logger
from shared.metrics import llm_breaker_open

logger = get_logger("provider_health")

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


@dataclass
class ProviderState:
    fail_count: int
    first_fail_ts: float
    open_until: float


class ProviderHealth:
    """Circuit breaker per provider.

    Primary store: Redis (persistent across restarts).
    Fallback: local file store under logs/provider_breaker_state.json when Redis is unavailable.
    """

    def __init__(self):
        self.window_seconds = int(getattr(settings, "breaker_window_seconds", 300) or 300)
        self.fail_threshold = int(getattr(settings, "breaker_fail_threshold", 5) or 5)
        self.cooldown_seconds = int(getattr(settings, "breaker_cooldown_seconds", 120) or 120)

        self._redis = None
        if redis is not None:
            try:
                self._redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
                # ping to verify connectivity
                self._redis.ping()
            except Exception:
                self._redis = None

        self._file_path = "logs/provider_breaker_state.json"

    def _key(self, provider: str) -> str:
        return f"nexus:breaker:{provider}"

    # ---------- file store ----------
    def _file_load_all(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self._file_path):
                return {}
            with open(self._file_path, "r", encoding="utf-8") as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def _file_save_all(self, d: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self._file_path) or ".", exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(d, f)

    def _file_get(self, provider: str) -> Optional[str]:
        d = self._file_load_all()
        v = d.get(provider)
        return json.dumps(v) if isinstance(v, dict) else None

    def _file_set(self, provider: str, payload: Dict[str, Any]) -> None:
        d = self._file_load_all()
        d[provider] = payload
        self._file_save_all(d)

    def _file_del(self, provider: str) -> None:
        d = self._file_load_all()
        if provider in d:
            del d[provider]
            self._file_save_all(d)

    # ---------- unified get/set ----------
    def _get_raw(self, provider: str) -> Optional[str]:
        if self._redis is not None:
            try:
                return self._redis.get(self._key(provider))
            except Exception:
                self._redis = None
        return self._file_get(provider)

    def _set_raw(self, provider: str, payload: Dict[str, Any]) -> None:
        if self._redis is not None:
            try:
                self._redis.set(self._key(provider), json.dumps(payload))
                return
            except Exception:
                self._redis = None
        self._file_set(provider, payload)

    def _del_raw(self, provider: str) -> None:
        if self._redis is not None:
            try:
                self._redis.delete(self._key(provider))
                return
            except Exception:
                self._redis = None
        self._file_del(provider)

    def get_state(self, provider: str) -> ProviderState:
        raw = self._get_raw(provider)
        if not raw:
            now = time.time()
            return ProviderState(0, now, 0.0)
        try:
            d = json.loads(raw)
        except Exception:
            now = time.time()
            return ProviderState(0, now, 0.0)
        return ProviderState(
            int(d.get("fail_count", 0)),
            float(d.get("first_fail_ts", time.time())),
            float(d.get("open_until", 0.0)),
        )

    def is_open(self, provider: str) -> bool:
        st = self.get_state(provider)
        opened = st.open_until > time.time()
        try:
            if llm_breaker_open is not None:
                llm_breaker_open.labels(provider=provider).set(1.0 if opened else 0.0)
        except Exception:
            pass
        return opened

    def record_success(self, provider: str) -> None:
        self._del_raw(provider)
        try:
            if llm_breaker_open is not None:
                llm_breaker_open.labels(provider=provider).set(0.0)
        except Exception:
            pass

    def record_failure(self, provider: str, *, open_seconds_override: Optional[float] = None) -> None:
        now = time.time()
        st = self.get_state(provider)

        # window reset
        if now - st.first_fail_ts > self.window_seconds:
            st = ProviderState(0, now, 0.0)

        st.fail_count += 1
        if st.fail_count >= self.fail_threshold:
            cd = float(open_seconds_override) if open_seconds_override is not None else float(self.cooldown_seconds)
            st.open_until = now + max(1.0, cd)
            try:
                if llm_breaker_open is not None:
                    llm_breaker_open.labels(provider=provider).set(1.0)
            except Exception:
                pass
            logger.warning(
                {
                    "event": "BREAKER_OPEN",
                    "provider": provider,
                    "fail_count": st.fail_count,
                    "open_until": st.open_until,
                    "cooldown_s": cd,
                }
            )

        payload = {"fail_count": st.fail_count, "first_fail_ts": st.first_fail_ts, "open_until": st.open_until}
        self._set_raw(provider, payload)
