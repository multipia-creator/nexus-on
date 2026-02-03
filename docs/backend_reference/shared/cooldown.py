from __future__ import annotations

# Backward-compatible shim.
# v4.7 uses persistent cooldown store (file-based) via shared.cooldown_store.
from shared.cooldown_store import is_in_cooldown, set_cooldown  # noqa: F401
