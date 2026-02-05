from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from shared.check_match import normalize


@dataclass
class CheckPolicy:
    allow: List[str]  # e.g. ["success","skipped","neutral"]


def load_policy(policy_json: str) -> Dict[str, CheckPolicy]:
    if not policy_json:
        return {}
    try:
        raw = json.loads(policy_json)
        out: Dict[str, CheckPolicy] = {}
        if isinstance(raw, dict):
            for k, v in raw.items():
                if not k:
                    continue
                allow = []
                if isinstance(v, dict):
                    allow = v.get("allow") or []
                if isinstance(allow, list):
                    allow = [normalize(str(x)) for x in allow if str(x)]
                if not allow:
                    allow = ["success"]
                out[normalize(k)] = CheckPolicy(allow=allow)
        return out
    except Exception:
        return {}


def verdict_for(conclusion: str, policy: CheckPolicy) -> bool:
    c = normalize(conclusion)
    # unify
    if c == "completed":
        c = "success"  # conservative fallback, but most GH uses conclusion=success
    for a in policy.allow:
        if a and a in c:
            return True
    return False


def evaluate_required_with_policy(
    checks: List[Tuple[str, str]],
    required: List[str],
    match_mode: str,
    policy_map: Dict[str, CheckPolicy],
    default_allow: List[str],
) -> Tuple[bool, List[str]]:
    # checks: list of (name, conclusion/status)
    # required entries matched by mode: exact/contains/regex handled externally by pre-normalized match logic; we'll implement small here.
    import re

    missing = []
    req_norm = [r.strip() for r in required if r and r.strip()]
    if not req_norm:
        return True, []

    # pre-normalize checks
    norm_checks = [(normalize(n), normalize(c)) for (n, c) in checks]

    def match(name: str, req: str) -> bool:
        rn = normalize(req)
        if match_mode == "exact":
            return name == rn
        if match_mode == "regex":
            try:
                return re.search(req, name, flags=re.IGNORECASE) is not None
            except re.error:
                return rn in name
        return rn in name  # contains

    for req in req_norm:
        pol = policy_map.get(normalize(req), CheckPolicy(allow=default_allow))
        found_ok = False
        for (n, c) in norm_checks:
            if match(n, req):
                if verdict_for(c, pol):
                    found_ok = True
                    break
        if not found_ok:
            missing.append(req)
    return (len(missing) == 0), missing
