from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List

from shared.settings import settings
from shared.tenant_ctx import TenantCtx


@dataclass
class ProviderKey:
    key_id: str
    api_key: str
    created_at: str = ""
    active: bool = True


def _fingerprint(key: str) -> str:
    if not key:
        return ""
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return "sha256:" + h[:12]


def _parse_keys_json(raw: str) -> List[ProviderKey]:
    out: List[ProviderKey] = []
    if not raw:
        return out
    try:
        d = json.loads(raw)
        if isinstance(d, dict):
            d = d.get("keys") or []
        if not isinstance(d, list):
            return out
        for item in d:
            if not isinstance(item, dict):
                continue
            kid = str(item.get("id") or item.get("key_id") or "").strip()
            key = str(item.get("key") or item.get("api_key") or "").strip()
            if not key:
                continue
            out.append(
                ProviderKey(
                    key_id=kid or "key",
                    api_key=key,
                    created_at=str(item.get("created_at") or ""),
                    active=bool(item.get("active", True)),
                )
            )
    except Exception:
        return []
    return out


_KIND_BY_PROVIDER = {
    "gemini": "llm_gemini_api_key",
    "openai": "llm_openai_api_key",
    "anthropic": "llm_anthropic_api_key",
    "glm": "llm_glm_api_key",
}


def _provider_to_env(provider: str) -> Tuple[str, str, str]:
    p = (provider or "").lower().strip()
    if p == "gemini":
        keys_json = str(getattr(settings, "gemini_api_keys_json", "") or "").strip()
        active_id = str(getattr(settings, "gemini_active_key_id", "") or "").strip()
        single = str(getattr(settings, "gemini_api_key", "") or "").strip()
        return keys_json, active_id, single
    if p == "openai":
        keys_json = str(getattr(settings, "openai_api_keys_json", "") or "").strip()
        active_id = str(getattr(settings, "openai_active_key_id", "") or "").strip()
        single = str(getattr(settings, "openai_api_key", "") or "").strip()
        return keys_json, active_id, single
    if p == "anthropic":
        keys_json = str(getattr(settings, "anthropic_api_keys_json", "") or "").strip()
        active_id = str(getattr(settings, "anthropic_active_key_id", "") or "").strip()
        single = str(getattr(settings, "anthropic_api_key", "") or "").strip()
        return keys_json, active_id, single
    if p == "glm":
        keys_json = str(getattr(settings, "glm_api_keys_json", "") or "").strip()
        active_id = str(getattr(settings, "glm_active_key_id", "") or "").strip()
        single = str(getattr(settings, "glm_api_key", "") or "").strip()
        return keys_json, active_id, single
    return "", "", ""


def select_key(
    provider: str,
    *,
    tenant: Optional[TenantCtx] = None,
    vault: Optional[Any] = None,
    kind_override: Optional[str] = None,
) -> Tuple[str, str, str]:
    """Return (api_key, key_id, fingerprint).

    Precedence:
      1) tenant vault (if tenant+vault available and kind exists)
      2) env rotation (keys_json + active_id)
      3) env single key

    The returned fingerprint is a non-reversible short SHA-256 prefix for audit.
    """

    p = (provider or "").lower().strip()

    # 1) tenant vault
    kind = (kind_override or _KIND_BY_PROVIDER.get(p) or "").strip()
    if tenant and vault and kind:
        try:
            resolved = vault.resolve(org_id=tenant.org_id, project_id=tenant.project_id, kind=kind)
        except Exception:
            resolved = None
        if resolved and getattr(resolved, "api_key", ""):
            api_key = resolved.api_key
            key_id = f"vault:{kind}:{resolved.key_id}"
            fp = getattr(resolved, "fingerprint", "") or _fingerprint(api_key)
            return api_key, key_id, fp

    # 2-3) environment
    keys_json, active_id, single = _provider_to_env(p)

    keys = _parse_keys_json(keys_json)
    if keys:
        cand = None
        if active_id:
            for k in keys:
                if k.key_id == active_id and k.active:
                    cand = k
                    break
        if cand is None:
            for k in keys:
                if k.active:
                    cand = k
                    break
        if cand:
            return cand.api_key, cand.key_id, _fingerprint(cand.api_key)

    if single:
        return single, "", _fingerprint(single)

    return "", "", ""
