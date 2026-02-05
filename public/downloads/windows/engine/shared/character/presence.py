from __future__ import annotations

import hashlib
from typing import Any, Dict

from .presence_policy import policy_for
from .state_engine import CharacterContext, CharacterDecision, clamp_int


def _seeded_rand_u32(seed: str) -> int:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _pick_int(seed: str, lo: int, hi: int) -> int:
    r = _seeded_rand_u32(seed) % (hi - lo + 1)
    return lo + r


def _pick_float(seed: str, lo: float, hi: float, steps: int = 1000) -> float:
    """Deterministic float in [lo, hi]."""
    if hi <= lo:
        return float(lo)
    r = _seeded_rand_u32(seed) % (steps + 1)
    return lo + (hi - lo) * (r / steps)


def presence_to_live2d(request_id: str, decision: CharacterDecision, ctx: CharacterContext) -> Dict[str, Any]:
    """Create deterministic Live2D presence packet (v1.1).

    - Uses a policy table (presence_policy.py) so behavior is stable and auditable.
    - Deterministic by request_id for rehearsal evidence diffs.
    """
    mode = decision.mode
    intimacy = clamp_int(ctx.intimacy, 0, 100)
    jealousy = clamp_int(decision.jealousy_level, 0, 4)
    sexy_level = clamp_int(decision.sexy_level, 0, 3)

    pol = policy_for(mode=mode, jealousy_level=jealousy, sexy_level=sexy_level, task_busy=bool(ctx.task_busy))

    listen = _pick_int(f"{request_id}:listen:{mode}", pol.listening_tick_ms[0], pol.listening_tick_ms[1])
    # Think pause only for focused/busy by convention; else 0 (fast conversational feel).
    if mode in ("focused", "busy"):
        think = _pick_int(f"{request_id}:think:{mode}", pol.think_pause_ms[0], pol.think_pause_ms[1])
    else:
        think = 0

    gaze_target = pol.gaze_target
    lpf_tau = _pick_float(f"{request_id}:gaze_tau:{mode}", pol.gaze_tau[0], pol.gaze_tau[1], steps=1000)

    breath_tau = _pick_float(f"{request_id}:breath_tau:{mode}", pol.breath_tau[0], pol.breath_tau[1], steps=1000)
    breath_rate = _pick_float(f"{request_id}:breath_rate:{mode}", pol.breath_rate_hz[0], pol.breath_rate_hz[1], steps=1000)
    breath_amp = _pick_float(f"{request_id}:breath_amp:{mode}", pol.breath_amp[0], pol.breath_amp[1], steps=1000)

    blink_mean = _pick_float(f"{request_id}:blink_mean:{mode}", pol.blink_mean_s[0], pol.blink_mean_s[1], steps=1000)
    cluster_allowed = True

    # param defaults
    blush = 0.0
    tension = 0.0
    if mode == "sexy":
        blush = 0.30 + 0.20 * sexy_level
        tension = 0.20 + 0.15 * sexy_level
    elif mode == "jealous":
        blush = 0.20
        tension = 0.70 if jealousy >= 3 else 0.50
    elif mode == "busy":
        tension = 0.35

    params = {
        "AngleX": 0.0, "AngleY": 0.0, "AngleZ": 0.0,
        "EyeLOpen": 1.0, "EyeROpen": 1.0, "EyeBallX": 0.0, "EyeBallY": 0.0,
        "MouthOpenY": 0.0, "MouthForm": 0.0, "Smile": 0.2 if mode in ("friendly", "sexy") else 0.0,
        "Breath": breath_amp, "Idle": 0.5, "Blush": blush, "Tension": tension,
        "BrowLY": 0.0, "BrowRY": 0.0, "Cheek": blush,
        "HeadNod": 0.0, "BodyLean": 0.0, "HandPose": 0.0,
    }

    if pol.movement_reduced:
        params["Idle"] = 0.2
        params["HeadNod"] = 0.0
        params["BodyLean"] = 0.0

    return {
        "version": "1.0",
        "state": {
            "mode": mode,
            "intimacy": intimacy,
            "jealousy_level": jealousy,
            "sexy_level": sexy_level,
            "task_busy": bool(ctx.task_busy),
        },
        "timing": {
            "listening_tick_ms": int(listen),
            "think_pause_ms": int(think),
            "silence_frame_ms": int(pol.silence_frame_ms),
        },
        "gaze": {"target": gaze_target, "lpf_tau": float(lpf_tau)},
        "breath": {"rate_hz": float(breath_rate), "amplitude": float(breath_amp), "lpf_tau": float(breath_tau)},
        "blink": {"mean_interval_s": float(blink_mean), "cluster_allowed": bool(cluster_allowed)},
        "params": params,
    }
