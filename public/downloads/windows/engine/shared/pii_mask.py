import re
from typing import Any

PHONE_RE = re.compile(r"(\+?\d{1,3})?\d{6,12}")
EMAIL_RE = re.compile(r"([\w\.-]+)@([\w\.-]+)\.(\w+)")

def mask_sensitive(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: mask_sensitive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [mask_sensitive(x) for x in obj]
    if isinstance(obj, str):
        s = obj
        s = EMAIL_RE.sub(lambda m: m.group(1)[:2] + "***@" + m.group(2) + "." + m.group(3), s)
        def _mask_phone(m):
            raw = m.group(0)
            if len(raw) <= 4:
                return "***"
            return "*" * (len(raw) - 3) + raw[-3:]
        s = PHONE_RE.sub(_mask_phone, s)
        return s
    return obj
