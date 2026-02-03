from __future__ import annotations

import random
from typing import Optional


def compute_backoff_s(attempt: int, *, base_s: float = 0.7, cap_s: float = 12.0, jitter_s: float = 0.25) -> float:
    """Standard backoff curve for provider retries (5xx, network, transient)."""
    a = max(0, int(attempt))
    return min(cap_s, (base_s * (2 ** a)) + random.uniform(0, jitter_s))


def retry_after_or_backoff(retry_after_s: Optional[float], attempt: int) -> float:
    if retry_after_s is not None and retry_after_s > 0:
        return float(retry_after_s)
    return compute_backoff_s(attempt)
