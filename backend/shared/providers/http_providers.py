from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List

import requests

from shared.errors import classify_http_status, ClassifiedError


@dataclass
class ProviderResponse:
    ok: bool
    text: str
    model: str
    provider: str
    latency_ms: int
    error: Optional[ClassifiedError] = None
    raw: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, int]] = None


def _now_ms() -> int:
    return int(time.time() * 1000)

def _parse_retry_after(headers: Dict[str, Any]) -> Optional[float]:
    ra = None
    try:
        ra = (headers or {}).get("Retry-After") or (headers or {}).get("retry-after")
    except Exception:
        ra = None
    if not ra:
        return None
    try:
        return float(ra)
    except Exception:
        return None

def _extract_openai_output_text(data: Dict[str, Any]) -> str:
    # Responses API: output is a list of items, commonly "message" with content blocks.
    # We extract all blocks where type is output_text or text.
    out: List[str] = []
    for item in data.get("output", []) or []:
        content = item.get("content") or []
        for block in content:
            t = block.get("text")
            if isinstance(t, str) and t.strip():
                out.append(t)
    if out:
        return "\n".join(out)
    # fallback (some SDKs expose output_text, but HTTP raw usually doesn't)
    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        return data["output_text"]
    return json.dumps(data, ensure_ascii=False)


def _extract_anthropic_text(data: Dict[str, Any]) -> str:
    # content: [{"type":"text","text":"..."}, ...]
    out: List[str] = []
    for block in data.get("content", []) or []:
        t = block.get("text")
        if isinstance(t, str) and t.strip():
            out.append(t)
    return "\n".join(out) if out else json.dumps(data, ensure_ascii=False)


def _extract_gemini_text(data: Dict[str, Any]) -> str:
    # candidates[0].content.parts[].text
    try:
        cand = (data.get("candidates") or [])[0]
        parts = (cand.get("content") or {}).get("parts") or []
        out: List[str] = []
        for p in parts:
            t = p.get("text")
            if isinstance(t, str) and t.strip():
                out.append(t)
        if out:
            return "\n".join(out)
    except Exception:
        pass
    return json.dumps(data, ensure_ascii=False)


def _extract_glm_text(data: Dict[str, Any]) -> str:
    # OpenAI-compatible: choices[0].message.content
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps(data, ensure_ascii=False)


def call_openai_responses(
    *,
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
    temperature: float = 0.2,
    timeout_s: int = 30,
) -> ProviderResponse:
    t0 = _now_ms()
    url = api_base.rstrip("/") + "/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "model": model,
        "input": prompt,
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
        "store": False,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
        status = r.status_code
        if status >= 400:
            ra = _parse_retry_after(r.headers.get("retry-after"))
            err = classify_http_status(status, r.text[:500], ra)
            return ProviderResponse(False, "", model, "openai", _now_ms() - t0, err, None)
        data = r.json()
        text = _extract_openai_output_text(data)
        return ProviderResponse(True, text, model, "openai", _now_ms() - t0, None, data, usage=_extract_usage_tokens(data))
    except requests.Timeout as e:
        err = classify_http_status(408, str(e))
        return ProviderResponse(False, "", model, "openai", _now_ms() - t0, err, None)
    except Exception as e:
        err = classify_http_status(None, str(e))
        return ProviderResponse(False, "", model, "openai", _now_ms() - t0, err, None)


def call_anthropic_messages(
    *,
    api_base: str,
    api_key: str,
    anthropic_version: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
    temperature: float = 0.2,
    timeout_s: int = 30,
) -> ProviderResponse:
    t0 = _now_ms()
    url = api_base.rstrip("/") + "/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": anthropic_version,
        "content-type": "application/json",
    }
    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": max_output_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
        status = r.status_code
        if status >= 400:
            ra = _parse_retry_after(r.headers.get("retry-after"))
            err = classify_http_status(status, r.text[:500], ra)
            return ProviderResponse(False, "", model, "anthropic", _now_ms() - t0, err, None)
        data = r.json()
        text = _extract_anthropic_text(data)
        return ProviderResponse(True, text, model, "anthropic", _now_ms() - t0, None, data, usage=_extract_usage_tokens(data))
    except requests.Timeout as e:
        err = classify_http_status(408, str(e))
        return ProviderResponse(False, "", model, "anthropic", _now_ms() - t0, err, None)
    except Exception as e:
        err = classify_http_status(None, str(e))
        return ProviderResponse(False, "", model, "anthropic", _now_ms() - t0, err, None)


def call_gemini_generate_content(
    *,
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
    temperature: float = 0.2,
    timeout_s: int = 30,
) -> ProviderResponse:
    t0 = _now_ms()
    # Google Gemini: key is usually passed as query param.
    url = api_base.rstrip("/") + f"/{model}:generateContent"
    params = {"key": api_key}
    headers = {"Content-Type": "application/json"}

    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_output_tokens, "temperature": temperature},
    }

    try:
        r = requests.post(url, headers=headers, params=params, json=payload, timeout=timeout_s)
        status = r.status_code
        if status >= 400:
            ra = _parse_retry_after(r.headers.get("retry-after"))
            err = classify_http_status(status, r.text[:500], ra)
            return ProviderResponse(False, "", model, "gemini", _now_ms() - t0, err, None)
        data = r.json()
        text = _extract_gemini_text(data)
        return ProviderResponse(True, text, model, "gemini", _now_ms() - t0, None, data, usage=_extract_usage_tokens(data))
    except requests.Timeout as e:
        err = classify_http_status(408, str(e))
        return ProviderResponse(False, "", model, "gemini", _now_ms() - t0, err, None)
    except Exception as e:
        err = classify_http_status(None, str(e))
        return ProviderResponse(False, "", model, "gemini", _now_ms() - t0, err, None)


def call_glm_chat_completions(
    *,
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
    temperature: float = 0.2,
    timeout_s: int = 30,
) -> ProviderResponse:
    t0 = _now_ms()
    # GLM OpenAI-compatible endpoint.
    url = api_base.rstrip("/") + "/chat/completions" if api_base.rstrip("/").endswith("/v4") else api_base
    # If user passes the full endpoint, keep it.
    if url.endswith("/v4"):
        url = url + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_output_tokens,
        "temperature": temperature,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
        status = r.status_code
        if status >= 400:
            ra = _parse_retry_after(r.headers.get("retry-after"))
            err = classify_http_status(status, r.text[:500], ra)
            return ProviderResponse(False, "", model, "glm", _now_ms() - t0, err, None)
        data = r.json()
        text = _extract_glm_text(data)
        return ProviderResponse(True, text, model, "glm", _now_ms() - t0, None, data, usage=_extract_usage_tokens(data))
    except requests.Timeout as e:
        err = classify_http_status(408, str(e))
        return ProviderResponse(False, "", model, "glm", _now_ms() - t0, err, None)
    except Exception as e:
        err = classify_http_status(None, str(e))
        return ProviderResponse(False, "", model, "glm", _now_ms() - t0, err, None)

def _extract_usage_tokens(provider: str, js: Dict[str, Any]) -> Dict[str, int]:
    """Best-effort usage extraction, provider-specific."""
    provider = provider.lower()
    try:
        if provider == "openai":
            u = (js or {}).get("usage") or {}
            pt = int(u.get("prompt_tokens") or 0)
            ct = int(u.get("completion_tokens") or 0)
            tt = int(u.get("total_tokens") or (pt + ct))
            return {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": tt}
        if provider == "anthropic":
            u = (js or {}).get("usage") or {}
            pt = int(u.get("input_tokens") or 0)
            ct = int(u.get("output_tokens") or 0)
            tt = int(u.get("total_tokens") or (pt + ct))
            return {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": tt}
        if provider == "gemini":
            # Gemini can expose usage in some responses; if absent, return zeros.
            u = (js or {}).get("usageMetadata") or (js or {}).get("usage") or {}
            pt = int(u.get("promptTokenCount") or u.get("prompt_tokens") or 0)
            ct = int(u.get("candidatesTokenCount") or u.get("completion_tokens") or 0)
            tt = int(u.get("totalTokenCount") or u.get("total_tokens") or (pt + ct))
            return {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": tt}
        if provider == "glm":
            u = (js or {}).get("usage") or {}
            pt = int(u.get("prompt_tokens") or 0)
            ct = int(u.get("completion_tokens") or 0)
            tt = int(u.get("total_tokens") or (pt + ct))
            return {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": tt}
    except Exception:
        pass
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
