from __future__ import annotations

import re
from typing import List, Tuple


def normalize(s: str) -> str:
    return (s or "").strip().lower()


def match_required_checks(summary: str, required: List[str], mode: str = "contains", accept_neutral: bool = False, accept_skipped: bool = False) -> Tuple[bool, List[str]]:
    """Return (ok, missing_list).
    summary format: 'name:conclusion, name2:success' (case-insensitive).
    Modes:
      - exact: required must match the check name exactly (case-insensitive)
      - contains: required substring must appear in the check name (case-insensitive)
      - regex: required entry treated as regex, matched against check name
    Success is considered if conclusion contains 'success'.
    """
    summary = summary or ""
    items = []
    for part in summary.split(","):
        p = part.strip()
        if not p:
            continue
        if ":" in p:
            name, conc = p.split(":", 1)
        else:
            name, conc = p, ""
        items.append((normalize(name), normalize(conc)))

    def is_success(conc: str) -> bool:
        if "success" in conc:
            return True
        if accept_neutral and "neutral" in conc:
            return True
        if accept_skipped and "skipped" in conc:
            return True
        return False

    missing = []
    for r in required:
        rr = r.strip()
        if not rr:
            continue
        rrn = normalize(rr)
        found = False
        for (n, c) in items:
            if not is_success(c):
                continue
            if mode == "exact":
                if n == rrn:
                    found = True
                    break
            elif mode == "regex":
                try:
                    if re.search(rr, n, flags=re.IGNORECASE):
                        found = True
                        break
                except re.error:
                    # invalid regex => fallback to contains
                    if rrn in n:
                        found = True
                        break
            else:  # contains
                if rrn in n:
                    found = True
                    break
        if not found:
            missing.append(rr)
    return (len(missing) == 0), missing
