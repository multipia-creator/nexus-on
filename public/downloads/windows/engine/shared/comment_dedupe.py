from __future__ import annotations

import hashlib
from typing import Tuple

from shared.cooldown_store import _with_lock, _load_unlocked, _save_unlocked, _ensure_parent


def _key(repo: str, pr_number: int, workflow: str = "") -> str:
    wf = (workflow or "wf").strip() or "wf"
    return f"comment_hash:{repo}:{wf}:{int(pr_number)}"


def compute_hash(body: str) -> str:
    b = (body or "").encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def get_last_hash(store_path: str, repo: str, pr_number: int) -> str:
    k = _key(repo, pr_number, workflow="")
    def _do():
        data = _load_unlocked(store_path)
        v = data.get(k) or {}
        return str(v.get("hash") or "")
    return _with_lock(store_path, _do)


def set_last_hash(store_path: str, repo: str, pr_number: int, h: str) -> None:
    k = _key(repo, pr_number, workflow="")
    def _do():
        data = _load_unlocked(store_path)
        data[k] = {"hash": h}
        _save_unlocked(store_path, data)
    return _with_lock(store_path, _do)


def get_last_url(store_path: str, repo: str, pr_number: int) -> str:
    k = _key(repo, pr_number, workflow="")
    def _do():
        data = _load_unlocked(store_path)
        v = data.get(k) or {}
        return str(v.get("url") or "")
    return _with_lock(store_path, _do)


def set_last_hash_url(store_path: str, repo: str, pr_number: int, h: str, url: str) -> None:
    k = _key(repo, pr_number, workflow="")
    def _do():
        data = _load_unlocked(store_path)
        data[k] = {"hash": h, "url": url or ""}
        _save_unlocked(store_path, data)
    return _with_lock(store_path, _do)


def get_last_hash_wf(store_path: str, repo: str, pr_number: int, workflow: str) -> str:
    k = _key(repo, pr_number, workflow=workflow)
    def _do():
        data = _load_unlocked(store_path)
        v = data.get(k) or {}
        return str(v.get("hash") or "")
    return _with_lock(store_path, _do)


def get_last_url_wf(store_path: str, repo: str, pr_number: int, workflow: str) -> str:
    k = _key(repo, pr_number, workflow=workflow)
    def _do():
        data = _load_unlocked(store_path)
        v = data.get(k) or {}
        return str(v.get("url") or "")
    return _with_lock(store_path, _do)


def set_last_hash_url_wf(store_path: str, repo: str, pr_number: int, workflow: str, h: str, url: str) -> None:
    k = _key(repo, pr_number, workflow=workflow)
    def _do():
        data = _load_unlocked(store_path)
        data[k] = {"hash": h, "url": url or ""}
        _save_unlocked(store_path, data)
    return _with_lock(store_path, _do)


def get_last_body_wf(store_path: str, repo: str, pr_number: int, workflow: str) -> str:
    k = _key(repo, pr_number, workflow=workflow)
    def _do():
        data = _load_unlocked(store_path)
        v = data.get(k) or {}
        return str(v.get("body") or "")
    return _with_lock(store_path, _do)


def set_last_state_wf(store_path: str, repo: str, pr_number: int, workflow: str, h: str, url: str, body: str = "") -> None:
    k = _key(repo, pr_number, workflow=workflow)
    def _do():
        data = _load_unlocked(store_path)
        data[k] = {"hash": h, "url": url or "", "body": (body or "")[:12000]}
        _save_unlocked(store_path, data)
    return _with_lock(store_path, _do)


def get_last_fields_wf(store_path: str, repo: str, pr_number: int, workflow: str) -> dict:
    k = _key(repo, pr_number, workflow=workflow)
    def _do():
        data = _load_unlocked(store_path)
        v = data.get(k) or {}
        try:
            return dict(v.get("fields") or {})
        except Exception:
            return {}
    return _with_lock(store_path, _do)


def set_last_state_wf(store_path: str, repo: str, pr_number: int, workflow: str, h: str, url: str, body: str = "", fields: dict | None = None) -> None:
    k = _key(repo, pr_number, workflow=workflow)
    def _do():
        data = _load_unlocked(store_path)
        data[k] = {
            "hash": h,
            "url": url or "",
            "body": (body or "")[:12000],
            "fields": (fields or {}),
        }
        _save_unlocked(store_path, data)
    return _with_lock(store_path, _do)
