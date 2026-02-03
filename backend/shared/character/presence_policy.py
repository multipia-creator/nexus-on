from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

Mode = Literal["friendly", "focused", "sexy", "jealous", "busy", "play"]


@dataclass(frozen=True)
class PresencePolicy:
    listening_tick_ms: Tuple[int, int] = (150, 350)
    think_pause_ms: Tuple[int, int] = (400, 900)  # used conditionally
    silence_frame_ms: int = 0  # 0 or 500
    gaze_target: Literal["user", "screen", "down_left", "down_right", "center"] = "user"
    gaze_tau: Tuple[float, float] = (0.08, 0.15)
    breath_rate_hz: Tuple[float, float] = (0.12, 0.35)
    breath_amp: Tuple[float, float] = (0.0, 1.0)
    breath_tau: Tuple[float, float] = (0.3, 0.6)
    blink_mean_s: Tuple[float, float] = (2.0, 8.0)
    movement_reduced: bool = False


def policy_for(mode: Mode, jealousy_level: int, sexy_level: int, task_busy: bool) -> PresencePolicy:
    """Policy table (v1).

    Hard rules:
    - 0.5s silence frame iff jealousy_level>=2 OR sexy_level==3
    - task_busy forces movement reduction
    - focused/busy gaze -> screen
    """
    silence = 500 if (jealousy_level >= 2 or sexy_level == 3) else 0

    if mode == "busy" or task_busy:
        return PresencePolicy(
            silence_frame_ms=silence,
            gaze_target="screen",
            breath_rate_hz=(0.18, 0.28),
            breath_amp=(0.10, 0.30),
            movement_reduced=True,
        )
    if mode == "focused":
        return PresencePolicy(
            silence_frame_ms=silence,
            gaze_target="screen",
            breath_rate_hz=(0.16, 0.26),
            breath_amp=(0.15, 0.35),
            movement_reduced=False,
        )
    if mode == "jealous":
        return PresencePolicy(
            silence_frame_ms=silence,
            gaze_target="user",
            breath_rate_hz=(0.14, 0.22),
            breath_amp=(0.25, 0.45),
            movement_reduced=False,
        )
    if mode == "sexy":
        return PresencePolicy(
            silence_frame_ms=silence,
            gaze_target="user",
            breath_rate_hz=(0.12, 0.20),
            breath_amp=(0.25, 0.50),
            movement_reduced=False,
        )
    if mode == "play":
        # Slightly more lively baseline: quicker breath + more frequent blink
        return PresencePolicy(
            silence_frame_ms=silence,
            gaze_target="user",
            breath_rate_hz=(0.18, 0.30),
            breath_amp=(0.25, 0.60),
            blink_mean_s=(2.5, 6.0),
            movement_reduced=False,
        )
    # friendly
    return PresencePolicy(
        silence_frame_ms=silence,
        gaze_target="user",
        breath_rate_hz=(0.14, 0.22),
        breath_amp=(0.20, 0.45),
        movement_reduced=False,
    )
