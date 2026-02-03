from __future__ import annotations

import math
from typing import Tuple


def estimate_tokens(text: str) -> int:
    """Heuristic token estimator when provider does not return usage.
    Assumptions:
      - For mixed Korean/English, a conservative ratio works better than english-only rules.
      - Use ~3.2 chars/token as a rough baseline, clamp minimum.
    """
    if not text:
        return 0
    n = len(text)
    return max(1, int(math.ceil(n / 3.2)))


def estimate_prompt_completion(prompt: str, completion: str) -> Tuple[int, int, int]:
    pt = estimate_tokens(prompt)
    ct = estimate_tokens(completion)
    return pt, ct, pt + ct
