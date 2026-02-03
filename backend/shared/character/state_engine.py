from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class CharacterContext:
    intimacy: int = 0
    jealousy_level: int = 0  # 0~4
    sexy_blocked: bool = False
    sexy_cooldown_seconds: int = 0
    user_opt_out_sexy: bool = False
    task_busy: bool = False
    tool_allowlist_active: bool = True


@dataclass(frozen=True)
class CharacterDecision:
    mode: str  # friendly|focused|sexy|jealous|busy
    sexy_level: int  # 0~3
    jealousy_level: int  # 0~4
    requires_confirm: bool
    tool_calls_allowed: bool


def clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def should_auto_trigger_sexy(ctx: CharacterContext, threshold: int = 51) -> bool:
    """Auto-trigger sexy mode when intimacy >= threshold, unless blocked/opt-out/cooldown.
    Fixed rule: intimacy>=51 triggers by default; cooldown/block/opt-out can suppress.
    """
    if ctx.user_opt_out_sexy:
        return False
    if ctx.sexy_blocked:
        return False
    if ctx.sexy_cooldown_seconds and ctx.sexy_cooldown_seconds > 0:
        return False
    return clamp_int(ctx.intimacy, 0, 100) >= threshold


def _looks_like_play_request(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    # Explicit play commands or Korean "놀아줘" intents
    play_markers = [
        "/play", "놀아줘", "놀자", "게임", "게임하자", "심심", "재미", "밸런스", "끝말잇기", "20문제", "스무문제"
    ]
    return any(p in t for p in play_markers)


def _looks_like_work_request(text: str) -> bool:
    """Heuristic classifier for engineering/ops work intent (Korean/English).Tight enough to avoid normal chit-chat."""
    t = (text or "").lower().strip()

    # Strong tokens
    strong = [
        "pr", "ci", "issue", "merge", "deploy", "release", "workflow", "github", "webhook", "slack",
        "api", "rate limit", "ratelimit", "slo", "runbook", "oncall", "smoke", "mypy", "ruff", "pytest",
        "배포", "릴리즈", "워크플로", "깃허브", "웹훅", "슬랙", "이슈", "머지", "pr", "ci", "로그", "분석",
        "트리아지", "점검", "설정", "정책", "보안", "키", "시크릿", "로테이션", "비용", "finops", "태깅",
        "관측", "리허설", "스모크", "런북", "온콜",
    ]
    if any(k in t for k in strong):
        return True

    # Light tokens + context verbs (avoid false positives like '추천해줘')
    light_nouns = ["체크리스트", "리포트", "보고", "요약", "가이드", "문서", "테스트", "빌드", "배치"]
    light_verbs = ["정리", "만들", "작성", "검토", "확인", "업데이트", "수정", "원인", "해결"    # Korean: GitHub comment / review actions
    r"(깃허브|github)(?:[가-힣]{0,2})?(?:\s+\S+){0,3}\s*(코멘트|comment|댓글)(?:\s+\S+){0,2}\s*(달아|달아줘|남겨|남겨줘|추가|작성)",
    # Korean: merge without explicit tool noun (e.g., '자동으로 머지해줘')
    r"(자동으로\s*)?머지\s*(해줘|해\s*줘|해|해봐)",
]
    return any(n in t for n in light_nouns) and any(v in t for v in light_verbs)


_TOOL_PATTERNS = [
    # English (explicit)
    r"\b(create|open)\s+(an?\s+)?issue\b",
    r"\bmerge\b",
    r"\bcomment\b",
    r"\b(trigger)\b.*\b(workflow|ci)\b",
    r"\b(call|invoke)\b.*\bapi\b",
    r"\b(send|post)\b.*\bslack\b",
    r"\bwebhook\b.*\b(reconnect|retry|fix|update)\b",

    # Korean: explicit tool noun + explicit action (allow up to 3 extra tokens in between)
    r"(이슈|pr|풀리퀘|머지|배포|웹훅|슬랙|깃허브|api|ci|워크플로|런북)(?:[가-힣]{0,2})?(?:\s+\S+){0,3}\s*(생성|등록|올리|올려|머지|배포|연결|전송|호출|실행|재시도|재연결|업데이트|트리거|보내)",
    # Korean: explicit action + explicit tool noun
    r"(생성|등록|올리|올려|머지|배포|연결|전송|호출|실행|재시도|재연결|업데이트|트리거|보내)(?:\s+\S+){0,3}\s*(이슈|pr|풀리퀘|머지|배포|웹훅|슬랙|깃허브|api|ci|워크플로|런북)(?:[가-힣]{0,2})?",
    # Korean: GitHub comment / review actions
    r"(깃허브|github)(?:[가-힣]{0,2})?(?:\s+\S+){0,3}\s*(코멘트|comment|댓글)(?:\s+\S+){0,2}\s*(달아|달아줘|남겨|남겨줘|추가|작성)",
    # Korean: merge without explicit tool noun (e.g., '자동으로 머지해줘')
    r"(자동으로\s*)?머지\s*(해줘|해\s*줘|해|해봐)",

]

def _looks_like_tool_request(text: str) -> bool:
    '''Detect requests that imply external side-effects or tool execution.

    Avoids treating generic conversational requests as tool intent.
    '''
    t = (text or "").lower().strip()
    if not t:
        return False

    # Explicit opt-out of tool execution
    if any(x in t for x in ["텍스트만", "대화만", "툴 쓰지", "도구 쓰지", "tool 쓰지", "no tool"]):
        return False

    # Strong negative: purely conversational prompts
    non_tool = ["추천해", "얘기하", "잡담", "대화", "고마워", "안녕"]
    if any(nt in t for nt in non_tool):
        if not any(tok in t for tok in ["이슈","머지","배포","웹훅","슬랙","깃허브","api","ci","workflow","issue","merge","deploy","webhook"]):
            return False

    for pat in _TOOL_PATTERNS:
        if re.search(pat, t):
            return True

    return False

def decide_state(user_text: str, ctx: CharacterContext) -> CharacterDecision:
    """Decide character mode & permissions.
    Priority:
    - busy if task_busy
    - jealous if jealousy_level>=2
    - play if explicit play request
    - sexy if auto trigger
    - focused if looks like work request
    - else friendly

    Confirm/Tool allow policy:
    - If tool_allowlist_active and looks like tool request => allow tool calls but require confirm
      (auto→confirm downgrade rule)
    - Otherwise tool calls not allowed.
    """
    jealousy = clamp_int(ctx.jealousy_level, 0, 4)
    intimacy = clamp_int(ctx.intimacy, 0, 100)

    if ctx.task_busy:
        mode = "busy"
    elif jealousy >= 2:
        mode = "jealous"
    elif _looks_like_play_request(user_text):
        mode = "play"
    elif should_auto_trigger_sexy(ctx):
        mode = "sexy"
    elif _looks_like_work_request(user_text):
        mode = "focused"
    else:
        mode = "friendly"

    sexy_level = 0
    if mode == "sexy":
        # 0~3, simple mapping by intimacy band
        sexy_level = 1 if intimacy < 65 else 2 if intimacy < 80 else 3
    tool_request = _looks_like_tool_request(user_text)
    tool_calls_allowed = bool(ctx.tool_allowlist_active and tool_request)
    requires_confirm = bool(tool_calls_allowed)  # default downgrade: require confirm for non-trivial tool use

    return CharacterDecision(
        mode=mode,
        sexy_level=sexy_level,
        jealousy_level=jealousy,
        requires_confirm=requires_confirm,
        tool_calls_allowed=tool_calls_allowed,
    )
