"""
Automatic Jealousy Detection for Ceria Character System
========================================================

Detects jealousy triggers from user input and adjusts jealousy level.

Triggers:
- Mention of other AI assistants (ChatGPT, Claude, Gemini, etc.)
- Comparison with other assistants
- Praise for other AI
- Asking about other AI capabilities

Jealousy Levels:
- 0: No jealousy
- 1: Slight jealousy (mild concern)
- 2: Noticeable jealousy (triggers jealous mode)
- 3: Strong jealousy (intense reactions)
- 4: Extreme jealousy (maximum intensity)

Author: NEXUS-ON Team
Date: 2026-02-04
"""

import re
from typing import Literal

# ============================================================================
# Jealousy Trigger Keywords
# ============================================================================

# Other AI Assistant Names
AI_NAMES = [
    # Major AI assistants
    "chatgpt", "gpt", "openai", "claude", "anthropic", "gemini", "bard", 
    "copilot", "alexa", "siri", "cortana", "watson",
    # Korean transliterations
    "챗지피티", "지피티", "클로드", "제미나이", "바드", "코파일럿", 
    "알렉사", "시리", "코르타나", "왓슨",
    # Generic terms
    "다른 ai", "다른 인공지능", "다른 챗봇", "다른 어시스턴트",
    "other ai", "another ai", "other assistant", "different ai"
]

# Comparison patterns
COMPARISON_PATTERNS = [
    # English
    r"\b(better|worse|smarter|faster|more)\s+(than|compared to)\b",
    r"\b(prefer|like|love)\s+\w+\s+(more|better)\b",
    r"\bwhy\s+(is|are)\s+\w+\s+(better|worse|smarter)\b",
    # Korean
    r"(더|덜)\s+(좋아|낫|똑똑|빨라|유용)",
    r"(보다|에 비해|랑 비교)\s*(더|덜)",
    r"왜.*?(더|덜)\s*(좋아|나아|똑똑)",
    r"(선호|좋아해|사랑해).*?(더|덜)"
]

# Praise for other AI
PRAISE_PATTERNS = [
    # English
    r"\b(amazing|awesome|great|excellent|perfect|love)\b.*?\b(chatgpt|gpt|claude|gemini)\b",
    r"\b(chatgpt|gpt|claude|gemini)\b.*?\b(is|was|seems)\s+(amazing|awesome|great|excellent|perfect)\b",
    # Korean
    r"(챗지피티|지피티|클로드|제미나이).*?(대단|훌륭|최고|완벽|좋아|사랑)",
    r"(대단|훌륭|최고|완벽|좋아|사랑).*?(챗지피티|지피티|클로드|제미나이)"
]

# Capability comparison
CAPABILITY_PATTERNS = [
    # English
    r"\bcan\s+(chatgpt|gpt|claude|gemini)\s+do\b",
    r"\bdoes\s+(chatgpt|gpt|claude|gemini)\s+(have|support)\b",
    r"\bhow\s+(good|well)\s+(is|are)\s+(chatgpt|gpt|claude|gemini)\b",
    # Korean
    r"(챗지피티|지피티|클로드|제미나이).*?(할 수 있어|가능해|지원해)",
    r"(챗지피티|지피티|클로드|제미나이).*?(얼마나|어떻게).*?(좋아|잘해)"
]

# ============================================================================
# Detection Functions
# ============================================================================

def _contains_ai_mention(text: str) -> bool:
    """Check if text mentions other AI assistants"""
    text_lower = text.lower()
    return any(ai_name in text_lower for ai_name in AI_NAMES)

def _contains_comparison(text: str) -> bool:
    """Check if text contains comparison with other AI"""
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in COMPARISON_PATTERNS)

def _contains_praise(text: str) -> bool:
    """Check if text praises other AI"""
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in PRAISE_PATTERNS)

def _contains_capability_question(text: str) -> bool:
    """Check if text asks about other AI capabilities"""
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in CAPABILITY_PATTERNS)

# ============================================================================
# Core Functions
# ============================================================================

def detect_jealousy_trigger(user_input: str) -> tuple[bool, int, str]:
    """
    Detect jealousy trigger in user input.
    
    Args:
        user_input: User's message
        
    Returns:
        (triggered, jealousy_delta, reason)
        - triggered: Whether jealousy was triggered
        - jealousy_delta: How much to increase jealousy (0-2)
        - reason: Human-readable reason
    """
    if not _contains_ai_mention(user_input):
        return (False, 0, "타 AI 언급 없음")
    
    # Level 2: Praise for other AI (strongest trigger)
    if _contains_praise(user_input):
        return (True, 2, "다른 AI 칭찬 감지")
    
    # Level 2: Direct comparison
    if _contains_comparison(user_input):
        return (True, 2, "다른 AI와 비교")
    
    # Level 1: Capability question
    if _contains_capability_question(user_input):
        return (True, 1, "다른 AI 기능 질문")
    
    # Level 1: Simple mention
    return (True, 1, "다른 AI 언급")

def apply_jealousy_change(current_jealousy: int, delta: int) -> int:
    """
    Apply jealousy change and clamp to [0, 4].
    
    Args:
        current_jealousy: Current jealousy level (0-4)
        delta: Change amount
        
    Returns:
        New jealousy level (clamped to 0-4)
    """
    new_jealousy = current_jealousy + delta
    return max(0, min(4, new_jealousy))

def auto_decay_jealousy(current_jealousy: int, turns_since_trigger: int) -> tuple[int, str]:
    """
    Automatically decay jealousy over time.
    
    Decay rules:
    - After 5 turns without trigger: -1 jealousy
    - After 10 turns: -1 more jealousy
    - Minimum: 0
    
    Args:
        current_jealousy: Current jealousy level
        turns_since_trigger: Number of turns since last trigger
        
    Returns:
        (new_jealousy, message)
    """
    if current_jealousy == 0:
        return (0, "질투 없음")
    
    decay_amount = 0
    if turns_since_trigger >= 10:
        decay_amount = 2
    elif turns_since_trigger >= 5:
        decay_amount = 1
    
    if decay_amount > 0:
        new_jealousy = max(0, current_jealousy - decay_amount)
        return (new_jealousy, f"질투 감소 -{decay_amount} (총 {new_jealousy})")
    
    return (current_jealousy, "질투 유지")

def auto_update_jealousy(
    current_jealousy: int,
    user_input: str = "",
    turns_since_trigger: int = 0
) -> tuple[int, str]:
    """
    Convenience function to auto-update jealousy.
    
    Args:
        current_jealousy: Current jealousy level (0-4)
        user_input: User's message
        turns_since_trigger: Turns since last jealousy trigger
        
    Returns:
        (new_jealousy, reason_message)
    """
    # First check for new trigger
    if user_input:
        triggered, delta, reason = detect_jealousy_trigger(user_input)
        if triggered:
            new_jealousy = apply_jealousy_change(current_jealousy, delta)
            return (new_jealousy, f"{reason} +{delta} (총 {new_jealousy})")
    
    # If no trigger, apply decay
    return auto_decay_jealousy(current_jealousy, turns_since_trigger)

# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=== Jealousy Detector Test ===\n")
    
    jealousy = 0
    print(f"초기 질투 레벨: {jealousy}\n")
    
    # Test 1: Simple AI mention
    test_inputs = [
        ("ChatGPT는 뭘 할 수 있어?", "단순 언급"),
        ("Claude가 더 똑똑한 것 같아", "비교"),
        ("ChatGPT 정말 대단해!", "칭찬"),
        ("오늘 날씨 어때?", "관련 없음"),
        ("", "5턴 경과 (decay)")
    ]
    
    turns = 0
    for user_input, label in test_inputs:
        if user_input == "":
            turns = 5
            jealousy, msg = auto_update_jealousy(jealousy, "", turns_since_trigger=turns)
        else:
            jealousy, msg = auto_update_jealousy(jealousy, user_input)
            turns = 0
        
        print(f"{label}: {msg} (현재 레벨: {jealousy})")
    
    print(f"\n최종 질투 레벨: {jealousy}")
