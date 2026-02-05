import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from jsonschema import Draft7Validator

from shared.logging_utils import get_logger
from shared.errors import ErrorCode

logger = get_logger("json_guard")

_SCHEMA_CACHE: dict[str, Draft7Validator] = {}

@dataclass
class GuardResult:
    ok: bool
    data: Optional[dict]
    error: Optional[str]
    error_code: str
    repaired: bool = False
    provider: Optional[str] = None
    model: Optional[str] = None
    attempts: int = 0

def _load_schema(schema_name: str) -> Draft7Validator:
    if schema_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_name]
    base = Path(__file__).parent / "schemas"
    p = base / f"{schema_name}.schema.json"
    if not p.exists():
        raise FileNotFoundError(f"schema not found: {p}")
    schema = json.loads(p.read_text(encoding="utf-8"))
    v = Draft7Validator(schema)
    _SCHEMA_CACHE[schema_name] = v
    return v

def _strict_json_parse(text: str) -> Tuple[Optional[dict], Optional[str]]:
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj, None
        return None, "json root is not object"
    except Exception as e:
        return None, f"{e}"

def validate(text: str, schema_name: str) -> GuardResult:
    data, err = _strict_json_parse(text)
    if err:
        return GuardResult(False, None, f"json parse error: {err}", ErrorCode.SCHEMA_PARSE_ERROR)
    v = _load_schema(schema_name)
    errors = sorted(v.iter_errors(data), key=lambda e: e.path)
    if errors:
        msg = "; ".join([e.message for e in errors[:5]])
        return GuardResult(False, data, f"schema validation error: {msg}", ErrorCode.SCHEMA_VALIDATION_ERROR)
    return GuardResult(True, data, None, "OK")

def _repair_prompt(schema_name: str, content: str, mode: str) -> str:
    # mode: "parse" or "validate"
    if mode == "parse":
        # Focus on extracting a valid JSON object only.
        return f"""You MUST output only valid JSON object. No markdown. No code fences. No explanation.
Task: Convert the content into a single JSON object matching schema name: {schema_name}.
If content contains extra text, discard it. Output JSON only.

CONTENT:
{content}
"""
    # validate mode: fill missing fields strictly
    return f"""You MUST output only valid JSON object. No markdown. No code fences. No explanation.
Task: Produce JSON that matches schema name: {schema_name}. If fields are missing, add them with best defaults. Keep it minimal.

CONTENT:
{content}
"""

def repair(text: str, schema_name: str, llm_client, max_attempts: int = 2, tenant: dict | None = None) -> GuardResult:
    """Two-stage repair:
    - Attempt 1 focuses on parse errors (strip noise, output JSON only).
    - Attempt 2 focuses on validation errors (fill missing fields).
    """
    first = validate(text, schema_name)
    if first.ok:
        first.attempts = 0
        return first

    last = first
    for attempt in range(1, max_attempts + 1):
        mode = "parse" if last.error_code == ErrorCode.SCHEMA_PARSE_ERROR else "validate"
        prompt = _repair_prompt(schema_name, text, mode)
        res = llm_client.generate(prompt, purpose="schema_repair", tenant=tenant, cache_ttl_s=0)
        if res.disabled:
            return GuardResult(False, None, f"llm repair disabled: {res.output_text}", ErrorCode.PROVIDER_DISABLED, True, res.provider, res.model, attempt)
        vr = validate(res.output_text, schema_name)
        vr.repaired = True
        vr.provider = res.provider
        vr.model = res.model
        vr.attempts = attempt
        if vr.ok:
            return vr
        # next attempt switches to validate mode regardless
        last = vr
        last.error_code = ErrorCode.SCHEMA_REPAIR_FAILED

    logger.warning({"event":"JSON_REPAIR_EXHAUSTED","schema":schema_name,"err":last.error,"attempts":max_attempts,"provider":last.provider,"model":last.model})
    last.error_code = ErrorCode.SCHEMA_REPAIR_FAILED
    return last
