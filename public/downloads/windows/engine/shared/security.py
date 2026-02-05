import hmac
import hashlib
from typing import Optional

def sign_payload(secret: str, body_bytes: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256)
    return mac.hexdigest()

def verify_signature(secret: str, body_bytes: bytes, provided: Optional[str]) -> bool:
    if not provided:
        return False
    expected = sign_payload(secret, body_bytes)
    return hmac.compare_digest(expected, provided)

def sign_callback(secret: str, body_bytes: bytes, *, timestamp: str, nonce: str) -> str:
    """v6.12+: bind signature to timestamp + nonce to prevent replay."""
    msg = (str(timestamp) + "." + str(nonce) + ".").encode("utf-8") + body_bytes
    mac = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256)
    return mac.hexdigest()

def verify_callback_signature(
    secret: str,
    body_bytes: bytes,
    provided: Optional[str],
    *,
    timestamp: Optional[str],
    nonce: Optional[str],
    allow_legacy_body_only: bool = True,
) -> bool:
    if not provided:
        return False
    ts = (timestamp or "").strip()
    nn = (nonce or "").strip()
    if ts and nn:
        expected = sign_callback(secret, body_bytes, timestamp=ts, nonce=nn)
        if hmac.compare_digest(expected, provided):
            return True
    if allow_legacy_body_only:
        return verify_signature(secret, body_bytes, provided)
    return False


from dataclasses import dataclass
import json as _json

@dataclass
class CallbackSecret:
    key_id: str
    secret: str
    active: bool = True

def parse_callback_secrets_json(raw: str) -> list[CallbackSecret]:
    out: list[CallbackSecret] = []
    if not raw:
        return out
    try:
        d = _json.loads(raw)
        if isinstance(d, dict):
            d = d.get("secrets") or d.get("keys") or []
        if not isinstance(d, list):
            return out
        for it in d:
            if not isinstance(it, dict):
                continue
            kid = str(it.get("id") or it.get("key_id") or "").strip()
            sec = str(it.get("secret") or it.get("key") or "").strip()
            if not sec:
                continue
            out.append(CallbackSecret(key_id=kid or "key", secret=sec, active=bool(it.get("active", True))))
    except Exception:
        return []
    return out

def verify_callback_signature_multi(
    *,
    secrets: list[CallbackSecret],
    body_bytes: bytes,
    provided: Optional[str],
    timestamp: Optional[str],
    nonce: Optional[str],
    key_id: Optional[str] = None,
    allow_legacy_body_only: bool = True,
) -> tuple[bool, str]:
    """Verify callback signature against one or more secrets.

    If key_id is provided, verify only that secret (if present & active).
    Otherwise verify all active secrets in order.

    Returns (ok, matched_key_id). matched_key_id is empty if not matched.
    """
    if not provided:
        return False, ""
    kid = (key_id or "").strip()
    cands: list[CallbackSecret] = []
    if kid:
        for s in secrets:
            if s.key_id == kid and s.active:
                cands = [s]
                break
        if not cands:
            return False, ""
    else:
        cands = [s for s in secrets if s.active]

    for s in cands:
        if verify_callback_signature(s.secret, body_bytes, provided, timestamp=timestamp, nonce=nonce, allow_legacy_body_only=allow_legacy_body_only):
            return True, s.key_id
    return False, ""
