"""
Automatic Intimacy Management for Ceria Character System
=========================================================

Handles automatic intimacy level updates based on user interactions.

Rules:
- Positive conversation: +1 intimacy
- Tool execution success: +3 intimacy
- User approval granted: +2 intimacy
- Negative feedback: -2 intimacy
- Intimacy clamped to [0, 100]

Author: NEXUS-ON Team
Date: 2026-02-04
"""

from dataclasses import dataclass
from typing import Literal

# ============================================================================
# Data Structures
# ============================================================================

@dataclass(frozen=True)
class IntimacyEvent:
    """Event that triggers intimacy change"""
    event_type: Literal["conversation", "tool_success", "approval_granted", "negative_feedback"]
    user_input: str = ""
    tool_name: str = ""
    sentiment_score: float = 0.0  # -1.0 to 1.0

# ============================================================================
# Intimacy Rules
# ============================================================================

INTIMACY_DELTAS = {
    "conversation": 1,      # Positive conversation
    "tool_success": 3,      # Tool executed successfully
    "approval_granted": 2,  # User approved RED task
    "negative_feedback": -2 # User expressed dissatisfaction
}

# ============================================================================
# Sentiment Detection (Simple Heuristic)
# ============================================================================

POSITIVE_KEYWORDS = [
    # English
    "thank", "thanks", "great", "good", "awesome", "nice", "perfect", "excellent", 
    "love", "like", "appreciate", "helpful", "amazing", "wonderful",
    # Korean
    "고마워", "감사", "좋아", "최고", "완벽", "훌륭", "멋져", "짱", "대박", 
    "도움", "유용", "사랑", "마음에 들어", "칭찬", "잘했어"
]

NEGATIVE_KEYWORDS = [
    # English
    "bad", "wrong", "error", "fail", "terrible", "awful", "hate", "dislike", 
    "useless", "stupid", "annoying", "frustrating",
    # Korean
    "싫어", "별로", "이상해", "안 돼", "틀려", "실패", "짜증", "화나", 
    "최악", "쓰레기", "멍청", "답답", "실망"
]

def _detect_sentiment(text: str) -> float:
    """
    Simple sentiment detection based on keyword matching.
    Returns: -1.0 (negative) to 1.0 (positive)
    """
    text_lower = text.lower()
    
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    
    if positive_count > negative_count:
        return min(1.0, positive_count * 0.3)
    elif negative_count > positive_count:
        return max(-1.0, -negative_count * 0.3)
    else:
        return 0.0

# ============================================================================
# Core Functions
# ============================================================================

def calculate_intimacy_change(event: IntimacyEvent) -> int:
    """
    Calculate intimacy change based on event.
    
    Args:
        event: IntimacyEvent with type and context
        
    Returns:
        Delta intimacy value (can be negative)
    """
    delta = INTIMACY_DELTAS.get(event.event_type, 0)
    
    # For conversation events, check sentiment
    if event.event_type == "conversation":
        sentiment = _detect_sentiment(event.user_input)
        
        # Positive sentiment (>0.5): +1 intimacy
        if sentiment > 0.5:
            return delta
        # Very negative sentiment (<-0.5): -1 intimacy
        elif sentiment < -0.5:
            return -1
        # Neutral: no change
        else:
            return 0
    
    return delta

def apply_intimacy_change(current_intimacy: int, delta: int) -> int:
    """
    Apply intimacy change and clamp to [0, 100].
    
    Args:
        current_intimacy: Current intimacy level
        delta: Change amount
        
    Returns:
        New intimacy level (clamped to 0-100)
    """
    new_intimacy = current_intimacy + delta
    return max(0, min(100, new_intimacy))

def auto_update_intimacy(
    current_intimacy: int,
    user_input: str = "",
    tool_success: bool = False,
    approval_granted: bool = False,
    negative_feedback: bool = False
) -> tuple[int, str]:
    """
    Convenience function to auto-update intimacy.
    
    Args:
        current_intimacy: Current intimacy level
        user_input: User's message
        tool_success: Whether a tool was successfully executed
        approval_granted: Whether user approved a RED task
        negative_feedback: Whether user gave negative feedback
        
    Returns:
        (new_intimacy, reason_message)
    """
    # Priority: tool_success > approval > negative > conversation
    if tool_success:
        event = IntimacyEvent(event_type="tool_success", tool_name="")
        delta = calculate_intimacy_change(event)
        new_intimacy = apply_intimacy_change(current_intimacy, delta)
        return (new_intimacy, f"도구 실행 성공 +{delta} (총 {new_intimacy})")
    
    if approval_granted:
        event = IntimacyEvent(event_type="approval_granted")
        delta = calculate_intimacy_change(event)
        new_intimacy = apply_intimacy_change(current_intimacy, delta)
        return (new_intimacy, f"승인 감사 +{delta} (총 {new_intimacy})")
    
    if negative_feedback:
        event = IntimacyEvent(event_type="negative_feedback")
        delta = calculate_intimacy_change(event)
        new_intimacy = apply_intimacy_change(current_intimacy, delta)
        return (new_intimacy, f"부정 피드백 {delta} (총 {new_intimacy})")
    
    # Default: check conversation sentiment
    if user_input:
        event = IntimacyEvent(event_type="conversation", user_input=user_input)
        delta = calculate_intimacy_change(event)
        new_intimacy = apply_intimacy_change(current_intimacy, delta)
        
        if delta > 0:
            return (new_intimacy, f"긍정 대화 +{delta} (총 {new_intimacy})")
        elif delta < 0:
            return (new_intimacy, f"부정 대화 {delta} (총 {new_intimacy})")
        else:
            return (current_intimacy, "중립 대화 (변화 없음)")
    
    return (current_intimacy, "변화 없음")

# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=== Auto Intimacy Test ===\n")
    
    intimacy = 50
    print(f"초기 친밀도: {intimacy}\n")
    
    # Test 1: Positive conversation
    intimacy, msg = auto_update_intimacy(intimacy, user_input="고마워! 정말 도움이 됐어")
    print(f"1. {msg}")
    
    # Test 2: Tool success
    intimacy, msg = auto_update_intimacy(intimacy, tool_success=True)
    print(f"2. {msg}")
    
    # Test 3: Approval granted
    intimacy, msg = auto_update_intimacy(intimacy, approval_granted=True)
    print(f"3. {msg}")
    
    # Test 4: Negative feedback
    intimacy, msg = auto_update_intimacy(intimacy, negative_feedback=True)
    print(f"4. {msg}")
    
    # Test 5: Neutral conversation
    intimacy, msg = auto_update_intimacy(intimacy, user_input="오늘 날씨 어때?")
    print(f"5. {msg}")
    
    print(f"\n최종 친밀도: {intimacy}")
