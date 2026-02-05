from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from shared.security import CallbackSecret, parse_callback_secrets_json

# ---------------------------
# v6.13 compatibility (simple active flag)
# ---------------------------

def dump_secrets_json(secrets: List[CallbackSecret]) -> str:
    """Legacy helper: dumps list[CallbackSecret] to JSON array."""
    return json.dumps([{"id": s.key_id, "secret": s.secret, "active": s.active} for s in secrets], ensure_ascii=False)

def rotate_activate(secrets: List[CallbackSecret], new_active_id: str, grace_seconds: int = 3600, now: Optional[int] = None) -> Tuple[List[CallbackSecret], str]:
    """Legacy rotation: activate one key id, leave others unchanged (no deactivate_at)."""
    nid = (new_active_id or "").strip()
    if not nid:
        return secrets, "no-op: missing new_active_id"
    prev = [s.key_id for s in secrets if s.active]
    found = False
    for s in secrets:
        if s.key_id == nid:
            s.active = True
            found = True
    if not found:
        return secrets, f"no-op: secret id not found: {nid}"
    return secrets, f"activated: {nid}; previous_active={prev}"

def load_callback_secrets(source: str, secrets_json_env: str, secrets_path: str) -> List[CallbackSecret]:
    """Load secrets for verification path."""
    src = (source or "env").strip().lower()
    raw = ""
    if src == "file":
        if secrets_path:
            try:
                with open(secrets_path, "r", encoding="utf-8") as f:
                    raw = f.read()
            except Exception:
                raw = ""
    else:
        raw = secrets_json_env or ""
    return parse_callback_secrets_json(raw)

# ---------------------------
# v6.15 rotation automation (deactivate_at)
# ---------------------------

@dataclass
class RotatableSecret:
    id: str
    secret: str
    active: bool = True
    rotated_at: Optional[int] = None
    deactivate_at: Optional[int] = None

def _load_raw_from_file(path: str) -> str:
    if not path:
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def _write_raw_to_file(path: str, raw: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw)

def parse_rotatable_secrets(raw: str) -> List[RotatableSecret]:
    out: List[RotatableSecret] = []
    if not raw:
        return out
    try:
        d = json.loads(raw)
        if isinstance(d, dict):
            d = d.get("secrets") or d.get("keys") or []
        if not isinstance(d, list):
            return out
        for it in d:
            if not isinstance(it, dict):
                continue
            sid = str(it.get("id") or it.get("key_id") or "").strip()
            sec = str(it.get("secret") or it.get("key") or "").strip()
            if not sec:
                continue
            out.append(
                RotatableSecret(
                    id=sid or "key",
                    secret=sec,
                    active=bool(it.get("active", True)),
                    rotated_at=int(it["rotated_at"]) if isinstance(it.get("rotated_at"), (int, float)) else None,
                    deactivate_at=int(it["deactivate_at"]) if isinstance(it.get("deactivate_at"), (int, float)) else None,
                )
            )
    except Exception:
        return out
    return out

def dump_rotatable_secrets_json(secrets: List[RotatableSecret]) -> str:
    return json.dumps(
        [
            {
                "id": s.id,
                "secret": s.secret,
                "active": s.active,
                **({"rotated_at": s.rotated_at} if s.rotated_at is not None else {}),
                **({"deactivate_at": s.deactivate_at} if s.deactivate_at is not None else {}),
            }
            for s in secrets
        ],
        ensure_ascii=False,
    )

def load_rotatable_secrets(source: str, secrets_json_env: str, secrets_path: str) -> List[RotatableSecret]:
    src = (source or "env").strip().lower()
    raw = _load_raw_from_file(secrets_path) if src == "file" else (secrets_json_env or "")
    return parse_rotatable_secrets(raw)

def reconcile_expired(secrets: List[RotatableSecret], now: Optional[int] = None) -> Tuple[List[RotatableSecret], bool]:
    n = int(now or int(time.time()))
    changed = False
    for s in secrets:
        if s.active and s.deactivate_at is not None and s.deactivate_at <= n:
            s.active = False
            changed = True
    return secrets, changed

def rotate_activate_rotatable(
    secrets: List[RotatableSecret],
    new_active_id: str,
    grace_seconds: int = 3600,
    now: Optional[int] = None,
) -> Tuple[List[RotatableSecret], str]:
    n = int(now or int(time.time()))
    nid = (new_active_id or "").strip()
    if not nid:
        return secrets, "no-op: missing new_active_id"

    prev_active = [s.id for s in secrets if s.active]
    tgt = None
    for s in secrets:
        if s.id == nid:
            tgt = s
            break
    if tgt is None:
        return secrets, f"no-op: secret id not found: {nid}"

    tgt.active = True
    tgt.rotated_at = n
    tgt.deactivate_at = None

    for s in secrets:
        if s.id != nid and s.active:
            s.deactivate_at = n + int(grace_seconds or 0)

    return secrets, f"activated: {nid}; previous_active={prev_active}; grace_s={grace_seconds}"

def persist_if_file(source: str, secrets_path: str, secrets: List[RotatableSecret]) -> Optional[str]:
    if (source or "").strip().lower() != "file":
        return None
    if not secrets_path:
        return None
    raw = dump_rotatable_secrets_json(secrets)
    _write_raw_to_file(secrets_path, raw)
    return secrets_path
