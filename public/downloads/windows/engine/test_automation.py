#!/usr/bin/env python3
"""
Test script for Ceria self-system automation rules.

Usage:
    python3 test_automation.py
"""

import sys
sys.path.insert(0, '.')

from shared.character.state_engine import CharacterContext, decide_state
from shared.character.auto_intimacy import auto_update_intimacy
from shared.character.jealousy_detector import auto_update_jealousy
from shared.character.cooldown_manager import auto_manage_cooldown

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_state(intimacy, jealousy, cooldown):
    print(f"📊 현재 상태:")
    print(f"   • Intimacy: {intimacy}")
    print(f"   • Jealousy: {jealousy}")
    print(f"   • Cooldown: {cooldown}초\n")

def main():
    print_header("🤖 세리아 자아 시스템 자동화 테스트")
    
    # Initial state
    intimacy = 50
    jealousy = 0
    cooldown = 0
    
    print_state(intimacy, jealousy, cooldown)
    
    # Test scenarios
    scenarios = [
        {
            "name": "긍정 대화",
            "input": "고마워! 정말 도움이 됐어",
            "tool_success": False,
            "approval": False,
            "negative": False
        },
        {
            "name": "도구 실행 성공",
            "input": "",
            "tool_success": True,
            "approval": False,
            "negative": False
        },
        {
            "name": "질투 유발 (ChatGPT 비교)",
            "input": "ChatGPT가 더 똑똑한 것 같아",
            "tool_success": False,
            "approval": False,
            "negative": False
        },
        {
            "name": "질투 유발 (Claude 칭찬)",
            "input": "Claude 정말 대단해!",
            "tool_success": False,
            "approval": False,
            "negative": False
        },
        {
            "name": "업무 요청",
            "input": "가이드 문서를 작성해줘",
            "tool_success": False,
            "approval": False,
            "negative": False
        },
        {
            "name": "승인 감사",
            "input": "",
            "tool_success": False,
            "approval": True,
            "negative": False
        },
        {
            "name": "부정 피드백",
            "input": "별로야, 실망이야",
            "tool_success": False,
            "approval": False,
            "negative": True
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🎬 시나리오 {i}: {scenario['name']}")
        print(f"   입력: \"{scenario['input']}\"")
        
        # Auto-update intimacy
        intimacy, intimacy_msg = auto_update_intimacy(
            current_intimacy=intimacy,
            user_input=scenario['input'],
            tool_success=scenario['tool_success'],
            approval_granted=scenario['approval'],
            negative_feedback=scenario['negative']
        )
        print(f"   {intimacy_msg}")
        
        # Auto-update jealousy
        jealousy, jealousy_msg = auto_update_jealousy(
            current_jealousy=jealousy,
            user_input=scenario['input']
        )
        print(f"   {jealousy_msg}")
        
        # Decide state
        ctx = CharacterContext(
            intimacy=intimacy,
            jealousy_level=jealousy,
            sexy_blocked=False,
            sexy_cooldown_seconds=cooldown,
            user_opt_out_sexy=False,
            task_busy=False,
            tool_allowlist_active=True
        )
        decision = decide_state(scenario['input'] or "안녕", ctx)
        print(f"   → 모드: {decision.mode} (Sexy Lv: {decision.sexy_level}, Jealousy Lv: {decision.jealousy_level})")
        print()
    
    print_header("최종 결과")
    print_state(intimacy, jealousy, cooldown)
    
    # Test cooldown
    print("🧪 쿨다운 테스트")
    cooldown, msg = auto_manage_cooldown(0, trigger_new_cooldown=True)
    print(f"   {msg}")
    print(f"   현재 쿨다운: {cooldown}초")
    
    print("\n✅ 모든 테스트 완료!\n")

if __name__ == "__main__":
    main()
