from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import os
import time
import random
import requests


@dataclass
class GitHubAPIError(Exception):
    status_code: int
    message: str
    url: str

    def __str__(self) -> str:
        return f"GitHubAPIError(status={self.status_code}, url={self.url}, message={self.message})"


def _headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    tok = os.getenv("GITHUB_TOKEN") or ""
    if not tok:
        try:
            from shared.settings import settings as _st  # local import to avoid cycles
            tok = getattr(_st, "github_token", "") or ""
        except Exception:
            tok = ""
    hdr: Dict[str, str] = {
        "Authorization": f"Bearer {tok}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "nexus-autofix",
    }
    if extra:
        hdr.update(extra)
    return hdr


def _sleep_backoff(i: int, base_ms: int, cap_s: float = 8.0) -> None:
    sleep_s = (base_ms / 1000.0) * (2 ** i) + random.uniform(0, 0.2)
    time.sleep(min(cap_s, sleep_s))


def request_json(
    method: str,
    url: str,
    *,
    json_payload: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout_s: int = 20,
    retries: int = 3,
    base_ms: int = 600,
    respect_retry_after: bool = True,
) -> Tuple[int, Dict[str, Any], requests.Response]:
    """Best-effort GitHub REST request.
    Returns (status_code, json_dict, response).
    Retries on 429/5xx only.
    """
    last: Optional[requests.Response] = None
    tries = max(1, int(retries))
    for i in range(tries):
        r = requests.request(
            method,
            url,
            headers=_headers(),
            json=json_payload,
            params=params,
            timeout=timeout_s,
        )
        last = r
        if 200 <= r.status_code < 300:
            try:
                return r.status_code, (r.json() or {}), r
            except Exception:
                return r.status_code, {}, r

        if r.status_code in (401, 403):
            break

        if r.status_code == 429 or (500 <= r.status_code < 600):
            if respect_retry_after:
                ra = (r.headers or {}).get("Retry-After")
                if ra:
                    try:
                        time.sleep(min(20.0, float(ra)))
                        continue
                    except Exception:
                        pass
            _sleep_backoff(i, base_ms)
            continue

        break

    msg = ""
    try:
        msg = (last.json() or {}).get("message") or ""
    except Exception:
        msg = (last.text or "")[:200] if last is not None else ""
    raise GitHubAPIError(last.status_code if last else 0, msg, url)
