"""
Automatic Cooldown Management for Ceria Character System
==========================================================

Manages sexy mode cooldown timer to prevent frequent mode switching.

Cooldown Rules:
- After sexy mode ends: 300 seconds (5 minutes) cooldown
- Cooldown decreases by elapsed time since last update
- When cooldown reaches 0: sexy mode can be triggered again
- User can manually override cooldown

Author: NEXUS-ON Team
Date: 2026-02-04
"""

import time
from dataclasses import dataclass
from typing import Optional

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_COOLDOWN_SECONDS = 300  # 5 minutes
MIN_COOLDOWN_SECONDS = 60       # 1 minute minimum

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class CooldownState:
    """Current cooldown state"""
    sexy_cooldown_seconds: int
    last_update_timestamp: float
    cooldown_active: bool
    
    @classmethod
    def create(cls, cooldown_seconds: int = 0) -> "CooldownState":
        """Create new cooldown state"""
        return cls(
            sexy_cooldown_seconds=cooldown_seconds,
            last_update_timestamp=time.time(),
            cooldown_active=cooldown_seconds > 0
        )

# ============================================================================
# Core Functions
# ============================================================================

def activate_cooldown(
    duration_seconds: int = DEFAULT_COOLDOWN_SECONDS
) -> CooldownState:
    """
    Activate sexy mode cooldown.
    
    Args:
        duration_seconds: Cooldown duration (default 300s)
        
    Returns:
        New CooldownState with active cooldown
    """
    return CooldownState.create(cooldown_seconds=duration_seconds)

def update_cooldown(state: CooldownState) -> CooldownState:
    """
    Update cooldown based on elapsed time.
    
    Args:
        state: Current cooldown state
        
    Returns:
        Updated CooldownState with decreased cooldown
    """
    if not state.cooldown_active or state.sexy_cooldown_seconds <= 0:
        return CooldownState.create(cooldown_seconds=0)
    
    current_time = time.time()
    elapsed_seconds = int(current_time - state.last_update_timestamp)
    
    # Decrease cooldown by elapsed time
    new_cooldown = max(0, state.sexy_cooldown_seconds - elapsed_seconds)
    
    return CooldownState(
        sexy_cooldown_seconds=new_cooldown,
        last_update_timestamp=current_time,
        cooldown_active=new_cooldown > 0
    )

def reset_cooldown(state: CooldownState) -> CooldownState:
    """
    Manually reset cooldown (admin override).
    
    Args:
        state: Current cooldown state
        
    Returns:
        CooldownState with cooldown reset to 0
    """
    return CooldownState.create(cooldown_seconds=0)

def extend_cooldown(
    state: CooldownState, 
    additional_seconds: int
) -> CooldownState:
    """
    Extend cooldown by additional time.
    
    Args:
        state: Current cooldown state
        additional_seconds: Additional cooldown time
        
    Returns:
        CooldownState with extended cooldown
    """
    # First update to get current cooldown
    updated_state = update_cooldown(state)
    
    new_cooldown = updated_state.sexy_cooldown_seconds + additional_seconds
    
    return CooldownState(
        sexy_cooldown_seconds=new_cooldown,
        last_update_timestamp=time.time(),
        cooldown_active=new_cooldown > 0
    )

def is_cooldown_active(state: CooldownState) -> bool:
    """
    Check if cooldown is currently active.
    
    Args:
        state: Current cooldown state
        
    Returns:
        True if cooldown is active
    """
    updated_state = update_cooldown(state)
    return updated_state.cooldown_active

def get_remaining_cooldown(state: CooldownState) -> int:
    """
    Get remaining cooldown time in seconds.
    
    Args:
        state: Current cooldown state
        
    Returns:
        Remaining cooldown seconds
    """
    updated_state = update_cooldown(state)
    return updated_state.sexy_cooldown_seconds

def format_cooldown_time(seconds: int) -> str:
    """
    Format cooldown time as human-readable string.
    
    Args:
        seconds: Cooldown seconds
        
    Returns:
        Formatted string (e.g., "3분 45초")
    """
    if seconds <= 0:
        return "쿨다운 없음"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes > 0:
        return f"{minutes}분 {remaining_seconds}초"
    else:
        return f"{remaining_seconds}초"

# ============================================================================
# Convenience Functions
# ============================================================================

def auto_manage_cooldown(
    current_cooldown_seconds: int,
    last_update_timestamp: Optional[float] = None,
    trigger_new_cooldown: bool = False,
    reset_override: bool = False
) -> tuple[int, str]:
    """
    Convenience function to auto-manage cooldown.
    
    Args:
        current_cooldown_seconds: Current cooldown value
        last_update_timestamp: Last update time (None = now)
        trigger_new_cooldown: Whether to activate new cooldown
        reset_override: Whether to reset cooldown manually
        
    Returns:
        (new_cooldown_seconds, message)
    """
    # Create state
    if last_update_timestamp is None:
        last_update_timestamp = time.time()
    
    state = CooldownState(
        sexy_cooldown_seconds=current_cooldown_seconds,
        last_update_timestamp=last_update_timestamp,
        cooldown_active=current_cooldown_seconds > 0
    )
    
    # Priority: reset > trigger > update
    if reset_override:
        new_state = reset_cooldown(state)
        return (new_state.sexy_cooldown_seconds, "쿨다운 수동 리셋")
    
    if trigger_new_cooldown:
        new_state = activate_cooldown()
        remaining_time = format_cooldown_time(new_state.sexy_cooldown_seconds)
        return (new_state.sexy_cooldown_seconds, f"쿨다운 활성화 ({remaining_time})")
    
    # Default: auto-update
    new_state = update_cooldown(state)
    if new_state.sexy_cooldown_seconds == 0:
        return (0, "쿨다운 만료")
    else:
        remaining_time = format_cooldown_time(new_state.sexy_cooldown_seconds)
        return (new_state.sexy_cooldown_seconds, f"쿨다운 진행 중 (남은 시간: {remaining_time})")

# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=== Cooldown Manager Test ===\n")
    
    # Test 1: Activate cooldown
    state = activate_cooldown(duration_seconds=10)
    print(f"1. 쿨다운 활성화: {state.sexy_cooldown_seconds}초")
    print(f"   상태: {'활성' if state.cooldown_active else '비활성'}\n")
    
    # Test 2: Wait and update
    print("2초 대기 중...")
    time.sleep(2)
    state = update_cooldown(state)
    remaining = format_cooldown_time(state.sexy_cooldown_seconds)
    print(f"2. 쿨다운 업데이트: {remaining} 남음\n")
    
    # Test 3: Extend cooldown
    state = extend_cooldown(state, additional_seconds=5)
    remaining = format_cooldown_time(state.sexy_cooldown_seconds)
    print(f"3. 쿨다운 연장 (+5초): {remaining} 남음\n")
    
    # Test 4: Reset cooldown
    state = reset_cooldown(state)
    print(f"4. 쿨다운 리셋: {state.sexy_cooldown_seconds}초")
    print(f"   상태: {'활성' if state.cooldown_active else '비활성'}\n")
    
    # Test 5: Auto-manage convenience function
    cooldown, msg = auto_manage_cooldown(300, trigger_new_cooldown=True)
    print(f"5. 자동 관리: {msg}")
    print(f"   현재 쿨다운: {cooldown}초")
