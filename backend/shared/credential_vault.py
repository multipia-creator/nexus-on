from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from shared.pii_mask import mask_sensitive


try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore

    _CRYPTO_OK = True
except Exception:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore
    _CRYPTO_OK = False


@dataclass(frozen=True)
class ResolvedSecret:
    api_key: str
    key_id: str
    fingerprint: str
    last4: str


class CredentialVaultError(RuntimeError):
    pass


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _fingerprint(s: str) -> str:
    # stable, non-reversible
    return _sha256_hex(s)[:16]


def _normalize_fernet_key(raw: str) -> str:
    """Return urlsafe-base64 32-byte Fernet key.

    Accepts:
      - urlsafe-base64 key (44 chars)
      - any arbitrary string (derived via sha256)
    """
    raw = (raw or "").strip()
    if not raw:
        raise CredentialVaultError("missing_master_key")

    # If the user passed raw bytes (base64), try decode.
    try:
        b = base64.urlsafe_b64decode(raw.encode("utf-8"))
        if len(b) == 32:
            # already a valid fernet key
            return raw
    except Exception:
        pass

    # Derive from arbitrary string.
    d = hashlib.sha256(raw.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(d).decode("utf-8")


def _parse_master_keys() -> Tuple[str, Dict[str, str]]:
    """Return (active_key_id, {key_id: fernet_key_str}).

    Supported env:
      - CREDENTIALS_MASTER_KEYS_JSON: {"active": "k1", "keys": [{"id": "k1", "key": "..."}, ...]}
      - CREDENTIALS_MASTER_KEY: single key, implicit id="k1"
    """
    mk_json = os.getenv("CREDENTIALS_MASTER_KEYS_JSON", "").strip()
    if mk_json:
        try:
            obj = json.loads(mk_json)
            active = (obj.get("active") or "").strip() or "k1"
            keys = {}
            for item in (obj.get("keys") or []):
                kid = (item.get("id") or "").strip()
                kraw = (item.get("key") or "").strip()
                if not kid or not kraw:
                    continue
                keys[kid] = _normalize_fernet_key(kraw)
            if active not in keys and keys:
                # pick first deterministically
                active = sorted(keys.keys())[0]
            return active, keys
        except Exception as e:
            raise CredentialVaultError(f"bad_master_keys_json:{e}") from e

    mk = os.getenv("CREDENTIALS_MASTER_KEY", "").strip()
    if mk:
        return "k1", {"k1": _normalize_fernet_key(mk)}

    return "", {}


class _TTLCache:
    def __init__(self, ttl_s: int = 30):
        self.ttl_s = int(ttl_s)
        self._lock = threading.Lock()
        self._data: Dict[str, Tuple[float, ResolvedSecret]] = {}

    def get(self, key: str) -> Optional[ResolvedSecret]:
        now = time.time()
        with self._lock:
            v = self._data.get(key)
            if not v:
                return None
            exp, payload = v
            if exp < now:
                self._data.pop(key, None)
                return None
            return payload

    def set(self, key: str, val: ResolvedSecret) -> None:
        exp = time.time() + self.ttl_s
        with self._lock:
            self._data[key] = (exp, val)

    def delete_prefix(self, prefix: str) -> None:
        with self._lock:
            for k in list(self._data.keys()):
                if k.startswith(prefix):
                    self._data.pop(k, None)


class CredentialVault:
    """Encrypted per-tenant secret vault (LLM keys, supervisor keys, etc.).

    Storage: SQLite (default) for reference implementation.
    Production deployments should replace the persistence layer with Postgres/KMS.

    Secrets are encrypted at rest using Fernet (AES-128-CBC + HMAC). Master key
    rotation is supported via multiple key IDs.
    """

    def __init__(
        self,
        *,
        db_path: str = "data/credentials.db",
        cache_ttl_s: int = 30,
        active_key_id: str = "",
        keys: Optional[Dict[str, str]] = None,
    ):
        self.db_path = db_path
        self.cache = _TTLCache(cache_ttl_s)
        self.active_key_id = active_key_id
        self._keys = keys or {}

        self._enabled = bool(_CRYPTO_OK and self.active_key_id and self._keys)
        self._init_db()

    @classmethod
    def from_env(cls) -> "CredentialVault":
        """Create a vault using environment variables.

        If CREDENTIALS_ENABLED is falsey, returns a disabled vault (no keys).
        """

        enabled = (os.getenv("CREDENTIALS_ENABLED", "false") or "false").strip().lower() in ("1", "true", "yes", "on")
        db_path = (os.getenv("CREDENTIALS_DB_PATH", "data/credentials.db") or "data/credentials.db").strip()
        db_path = db_path or "data/credentials.db"
        cache_ttl = int((os.getenv("CREDENTIALS_CACHE_TTL_SECONDS", "30") or "30").strip() or "30")
        if not enabled:
            return cls(db_path=db_path, cache_ttl_s=cache_ttl, active_key_id="", keys={})
        active, keys = _parse_master_keys()
        return cls(db_path=db_path, cache_ttl_s=cache_ttl, active_key_id=active, keys=keys)

    @classmethod
    def from_settings(cls, stg: Any) -> "CredentialVault":
        """Create a vault using shared.settings.Settings (or compatible object).

        Falls back to from_env if a required attribute is absent.
        """
        try:
            enabled = bool(getattr(stg, "credentials_enabled"))
            db_path = getattr(stg, "credentials_db_path")
            cache_ttl = int(getattr(stg, "credentials_cache_ttl_seconds"))
        except Exception:
            return cls.from_env()
        # We still read master keys from env to avoid storing them in config files.
        if not enabled:
            return cls(db_path=db_path, cache_ttl_s=cache_ttl, active_key_id="", keys={})
        active, keys = _parse_master_keys()
        return cls(db_path=db_path, cache_ttl_s=cache_ttl, active_key_id=active, keys=keys)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS credentials (
                    org_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    ciphertext BLOB NOT NULL,
                    enc_key_id TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    last4 TEXT NOT NULL,
                    label TEXT DEFAULT '',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    PRIMARY KEY (org_id, project_id, kind)
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_credentials_tenant ON credentials(org_id, project_id);"
            )
            conn.commit()
        finally:
            conn.close()

    def _fernet(self, key_id: str) -> "Fernet":
        if not self.enabled:
            raise CredentialVaultError("vault_disabled")
        k = self._keys.get(key_id)
        if not k:
            raise CredentialVaultError(f"unknown_master_key_id:{key_id}")
        return Fernet(k.encode("utf-8"))

    def _encrypt(self, plaintext: str) -> Tuple[bytes, str]:
        f = self._fernet(self.active_key_id)
        ct = f.encrypt(plaintext.encode("utf-8"))
        return ct, self.active_key_id

    def _decrypt(self, ciphertext: bytes, key_id_hint: str) -> str:
        # Attempt hint key first, then all others.
        key_ids = [key_id_hint] + [k for k in self._keys.keys() if k != key_id_hint]
        for kid in key_ids:
            if kid not in self._keys:
                continue
            try:
                f = self._fernet(kid)
                pt = f.decrypt(ciphertext)
                return pt.decode("utf-8")
            except InvalidToken:
                continue
        raise CredentialVaultError("decrypt_failed")

    def upsert(
        self,
        *,
        org_id: str,
        project_id: str,
        kind: str,
        api_key: str,
        label: str = "",
    ) -> Dict[str, Any]:
        if not self.enabled:
            raise CredentialVaultError("vault_disabled")
        org_id = (org_id or "").strip()
        project_id = (project_id or "").strip()
        kind = (kind or "").strip()
        api_key = (api_key or "").strip()
        if not org_id or not project_id or not kind or not api_key:
            raise CredentialVaultError("missing_fields")

        ct, key_id = self._encrypt(api_key)
        now = int(time.time())
        last4 = api_key[-4:] if len(api_key) >= 4 else api_key
        fp = _fingerprint(api_key)

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO credentials(org_id, project_id, kind, ciphertext, enc_key_id, fingerprint, last4, label, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(org_id, project_id, kind)
                DO UPDATE SET ciphertext=excluded.ciphertext,
                              enc_key_id=excluded.enc_key_id,
                              fingerprint=excluded.fingerprint,
                              last4=excluded.last4,
                              label=excluded.label,
                              updated_at=excluded.updated_at;
                """,
                (org_id, project_id, kind, ct, key_id, fp, last4, label or "", now, now),
            )
            conn.commit()
        finally:
            conn.close()

        cache_key = f"{org_id}:{project_id}:{kind}"
        self.cache.set(cache_key, ResolvedSecret(api_key=api_key, key_id=key_id, fingerprint=fp, last4=last4))
        return {"org_id": org_id, "project_id": project_id, "kind": kind, "label": label or "", "last4": last4, "fingerprint": fp, "updated_at": now}

    def resolve(self, *, org_id: str, project_id: str, kind: str) -> Optional[ResolvedSecret]:
        org_id = (org_id or "").strip()
        project_id = (project_id or "").strip()
        kind = (kind or "").strip()
        if not org_id or not project_id or not kind:
            return None
        cache_key = f"{org_id}:{project_id}:{kind}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT ciphertext, enc_key_id, fingerprint, last4 FROM credentials WHERE org_id=? AND project_id=? AND kind=?",
                (org_id, project_id, kind),
            ).fetchone()
            if not row:
                return None
            ciphertext, key_id, fp, last4 = row
            pt = self._decrypt(ciphertext, str(key_id))
            res = ResolvedSecret(api_key=pt, key_id=str(key_id), fingerprint=str(fp), last4=str(last4))
            self.cache.set(cache_key, res)
            return res
        finally:
            conn.close()

    def list(self, *, org_id: str, project_id: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT kind, label, last4, fingerprint, updated_at FROM credentials WHERE org_id=? AND project_id=? ORDER BY updated_at DESC",
                (org_id, project_id),
            ).fetchall()
            return [
                {
                    "kind": str(kind),
                    "label": str(label or ""),
                    "last4": str(last4),
                    "fingerprint": str(fp),
                    "updated_at": int(updated_at),
                }
                for (kind, label, last4, fp, updated_at) in rows
            ]
        finally:
            conn.close()

    def delete(self, *, org_id: str, project_id: str, kind: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "DELETE FROM credentials WHERE org_id=? AND project_id=? AND kind=?",
                (org_id, project_id, kind),
            )
            conn.commit()
            self.cache.delete_prefix(f"{org_id}:{project_id}:")
            return cur.rowcount > 0
        finally:
            conn.close()

    def safe_error(self, err: Exception) -> str:
        # Redact common patterns.
        return mask_sensitive(str(err))
