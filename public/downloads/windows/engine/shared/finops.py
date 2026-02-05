from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from shared.settings import settings
from shared.append_only import append_jsonl_with_chain


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def _pricing_table() -> Dict[str, Dict[str, float]]:
    # Optional override: LLM_PRICING_JSON can specify provider/model specific pricing.
    # Example:
    # {
    #  "gemini": {"default": {"prompt":0.001,"completion":0.002}, "gemini-2.0-flash": {"prompt":0.0008,"completion":0.0016}},
    #  "openai": {"gpt-4.1-mini": {"prompt":0.003,"completion":0.006}}
    # }
    try:
        raw = str(getattr(settings, 'llm_pricing_json', '') or '').strip()
        if raw:
            d = json.loads(raw)
            # normalize: allow provider -> {model-> {prompt,completion}} or provider -> {prompt,completion}
            out: Dict[str, Dict[str, float]] = {}
            # keep base pricing for default fallback
            base = {
                "gemini": {"prompt": 0.001, "completion": 0.002},
                "openai": {"prompt": 0.005, "completion": 0.010},
                "anthropic": {"prompt": 0.006, "completion": 0.012},
                "glm": {"prompt": 0.003, "completion": 0.006},
            }
            for prov, v in (d or {}).items():
                p = str(prov).lower()
                if isinstance(v, dict) and ("prompt" in v or "completion" in v):
                    out[p] = {"prompt": float(v.get("prompt", base.get(p, {}).get("prompt", 0.005))),
                              "completion": float(v.get("completion", base.get(p, {}).get("completion", 0.010)))}
                else:
                    # store model-specific dict in a side channel by flattening with key p|model
                    for model, vv in (v or {}).items():
                        if not isinstance(vv, dict):
                            continue
                        key = f"{p}|{str(model)}"
                        out[key] = {"prompt": float(vv.get("prompt", base.get(p, {}).get("prompt", 0.005))),
                                    "completion": float(vv.get("completion", base.get(p, {}).get("completion", 0.010)))}
                    # also ensure provider default exists
                    if p not in out:
                        out[p] = base.get(p, {"prompt": 0.005, "completion": 0.010})
            return {**base, **out}
    except Exception:
        pass

    
    """USD per 1k tokens (prompt/complete) coarse table.
    Override via env if you want (future: model-specific).
    """
    # These are intentionally conservative defaults. Tune with real billing.
    return {
        "gemini": {"prompt": 0.001, "completion": 0.002},
        "openai": {"prompt": 0.005, "completion": 0.010},
        "anthropic": {"prompt": 0.006, "completion": 0.012},
        "glm": {"prompt": 0.003, "completion": 0.006},
    }


def estimate_cost_usd(provider: str, usage: Usage, model: Optional[str] = None) -> float:
    pt = _pricing_table()
    p = provider.lower()
    key = f"{p}|{model}" if model else None
    t = pt.get(key, pt.get(p, {"prompt": 0.005, "completion": 0.010}))
    return (usage.prompt_tokens / 1000.0) * float(t["prompt"]) + (usage.completion_tokens / 1000.0) * float(t["completion"])


def _budget_state_path() -> str:
    return "logs/budget_state.json"


def _today_utc_key() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def _load_budget() -> Dict[str, Any]:
    try:
        if not os.path.exists(_budget_state_path()):
            return {"day_key": _today_utc_key(), "spent_usd": 0.0}
        with open(_budget_state_path(), "r", encoding="utf-8") as f:
            d = json.load(f) or {}
        if d.get("day_key") != _today_utc_key():
            return {"day_key": _today_utc_key(), "spent_usd": 0.0}
        return {"day_key": d.get("day_key"), "spent_usd": float(d.get("spent_usd") or 0.0)}
    except Exception:
        return {"day_key": _today_utc_key(), "spent_usd": 0.0}


def _save_budget(d: Dict[str, Any]) -> None:
    os.makedirs("logs", exist_ok=True)
    with open(_budget_state_path(), "w", encoding="utf-8") as f:
        json.dump(d, f)


def budget_adjust(delta_usd: float) -> None:
    """Best-effort settlement adjust after actual usage is known.
    delta can be negative or positive.
    """
    st = _load_budget()
    st["spent_usd"] = max(0.0, float(st.get("spent_usd") or 0.0) + float(delta_usd))
    _save_budget(st)


def write_cost_ledger(event: Dict[str, Any]) -> None:
    path = str(getattr(settings, "llm_cost_ledger_path", "logs/llm_cost_ledger.jsonl") or "logs/llm_cost_ledger.jsonl")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    ev = dict(event)
    ev.setdefault("ts_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    append_jsonl_with_chain(path, ev)
