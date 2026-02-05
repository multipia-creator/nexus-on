from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, Tuple

try:
    import fcntl  # type: ignore
except Exception:  # pragma: no cover
    fcntl = None


@dataclass
class CooldownState:
    until_ts: float
    reason: str


def _now() -> float:
    return time.time()


def _ensure_parent(path: str) -> None:
    d = os.path.dirname(path)
    if d and (not os.path.exists(d)):
        os.makedirs(d, exist_ok=True)


def _load_unlocked(path: str) -> Dict[str, Dict]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _save_unlocked(path: str, data: Dict) -> None:
    _ensure_parent(path)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)


def _with_lock(path: str, fn):
    _ensure_parent(path)
    # If fcntl missing (non-unix), best-effort no-lock.
    if fcntl is None:
        return fn()
    lock_path = f"{path}.lock"
    with open(lock_path, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            return fn()
        finally:
            try:
                fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass


def cleanup_expired(path: str) -> None:
    def _do():
        data = _load_unlocked(path)
        now = _now()
        changed = False
        for k in list(data.keys()):
            try:
                until = float((data.get(k) or {}).get("until_ts") or 0.0)
                if now >= until:
                    data.pop(k, None)
                    changed = True
            except Exception:
                data.pop(k, None)
                changed = True
        if changed:
            _save_unlocked(path, data)
    _with_lock(path, _do)


def is_in_cooldown(path: str, pr_number: int) -> Tuple[bool, str, float]:
    key = str(int(pr_number))
    def _do():
        data = _load_unlocked(path)
        st = data.get(key) or {}
        until = float(st.get("until_ts") or 0.0)
        reason = str(st.get("reason") or "")
        now = _now()
        if now >= until:
            if key in data:
                data.pop(key, None)
                _save_unlocked(path, data)
            return (False, "", 0.0)
        return (True, reason, until)
    return _with_lock(path, _do)


def set_cooldown(path: str, pr_number: int, minutes: int, reason: str) -> None:
    key = str(int(pr_number))
    mins = max(1, int(minutes or 1))
    until = _now() + mins * 60.0
    def _do():
        data = _load_unlocked(path)
        data[key] = {"until_ts": until, "reason": reason or "unknown", "updated_ts": _now()}
        _save_unlocked(path, data)
    _with_lock(path, _do)


def is_in_cooldown_key(path: str, key: str) -> Tuple[bool, str, float]:
    k = str(key)
    def _do():
        data = _load_unlocked(path)
        st = data.get(k) or {}
        until = float(st.get("until_ts") or 0.0)
        reason = str(st.get("reason") or "")
        now = _now()
        if now >= until:
            if k in data:
                data.pop(k, None)
                _save_unlocked(path, data)
            return (False, "", 0.0)
        return (True, reason, until)
    return _with_lock(path, _do)


def set_cooldown_key(path: str, key: str, minutes: int, reason: str) -> None:
    k = str(key)
    mins = max(1, int(minutes or 1))
    until = _now() + mins * 60.0
    def _do():
        data = _load_unlocked(path)
        data[k] = {"until_ts": until, "reason": reason or "unknown", "updated_ts": _now()}
        _save_unlocked(path, data)
    _with_lock(path, _do)
