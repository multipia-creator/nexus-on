from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import redis


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _k_play(tenant: str, session_id: str) -> str:
    return f"nexus:play:{tenant}:{session_id}"


@dataclass
class PlayReply:
    text: str
    state: Dict[str, Any]


class PlayEngine:
    """
    P0 'Play' engine:
      - state persisted per (tenant, session_id) in Redis
      - supports: balance_game, word_chain, twentyq-lite

    The goal is to provide a human-like "놀아주기" capability without complex dependencies.
    """

    def __init__(self, redis_url: str, ttl_seconds: int = 86400):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)
        self.ttl = int(ttl_seconds)

        self._balance_pairs = [
            ("평생 치킨", "평생 피자"),
            ("아침형 인간", "밤샘형 인간"),
            ("초능력: 순간이동", "초능력: 시간멈춤"),
            ("휴대폰 1년 금지", "SNS 1년 금지"),
            ("바다 여행", "산 여행"),
            ("혼자 여행", "친구랑 여행"),
            ("연애는 감정", "연애는 논리"),
            ("한 번에 1억", "매달 300만 평생"),
        ]

        # Minimal word list (fallback for assistant reply in 끝말잇기)
        self._words = [
            "사과", "과자", "자동차", "차표", "표정", "정리", "리본", "본능",
            "능력", "력사", "사랑", "랑데부", "부엌", "억울", "울음", "음악",
            "악기", "기차", "차가", "가방", "방울", "울산", "산책", "책상",
            "상자", "자전거", "거울", "울타리", "리듬", "믿음", "음료",
            "요리", "리더", "더위", "위로", "로봇", "봇물", "물병", "병원",
            "원숭이", "이불", "불꽃", "꽃병", "병아리", "리본", "본사",
        ]

        self._twentyq_items = [
            {"name": "고양이", "cat": "동물", "tags": ["집", "작다", "털"]},
            {"name": "강아지", "cat": "동물", "tags": ["집", "충성", "털"]},
            {"name": "김치", "cat": "음식", "tags": ["매움", "발효", "한국"]},
            {"name": "피자", "cat": "음식", "tags": ["치즈", "뜨거움"]},
            {"name": "노트북", "cat": "전자", "tags": ["일", "키보드"]},
            {"name": "스마트폰", "cat": "전자", "tags": ["전화", "앱"]},
            {"name": "책", "cat": "물건", "tags": ["종이", "읽기"]},
            {"name": "자전거", "cat": "탈것", "tags": ["바퀴", "야외"]},
        ]

    def _load(self, tenant: str, session_id: str) -> Dict[str, Any]:
        raw = self.r.get(_k_play(tenant, session_id))
        if not raw:
            return {"mode": "menu", "created_at": _utc_iso()}
        try:
            return json.loads(raw)
        except Exception:
            return {"mode": "menu", "created_at": _utc_iso()}

    def _save(self, tenant: str, session_id: str, state: Dict[str, Any]) -> None:
        self.r.set(_k_play(tenant, session_id), json.dumps(state, ensure_ascii=False), ex=self.ttl)

    def reset(self, tenant: str, session_id: str) -> None:
        self.r.delete(_k_play(tenant, session_id))

    def handle(self, tenant: str, session_id: str, user_text: str) -> PlayReply:
        t = (user_text or "").strip()
        if not session_id:
            session_id = "default"

        state = self._load(tenant, session_id)
        mode = state.get("mode", "menu")

        # global commands
        if t in ("/play", "놀아줘", "놀자", "게임", "게임하자", "재밌는거", "심심해"):
            state = {"mode": "menu", "created_at": _utc_iso()}
            self._save(tenant, session_id, state)
            return PlayReply(
                text="좋아요. 뭐 하고 놀까요?\n1) 밸런스 게임\n2) 끝말잇기\n3) 20문제(라이트)\n원하는 걸 말해줘요. 예: '밸런스', '끝말잇기', '20문제'\n그만하려면 '그만' 또는 '/play stop'.",
                state=state,
            )

        if t in ("/play stop", "그만", "끝", "종료", "stop"):
            self.reset(tenant, session_id)
            return PlayReply(text="오케이. 놀이는 여기까지. 다시 놀고 싶으면 '/play'라고 해줘요.", state={"mode": "stopped"})

        # choose mode from menu
        if mode == "menu":
            if "밸런스" in t:
                pair = random.choice(self._balance_pairs)
                state = {"mode": "balance", "pair": pair, "turn": 1, "created_at": state.get("created_at", _utc_iso())}
                self._save(tenant, session_id, state)
                return PlayReply(text=f"밸런스 게임 시작.\nA) {pair[0]}\nB) {pair[1]}\nA/B 중에 골라요. 이유도 한 줄!", state=state)
            if "끝말" in t or "끝말잇기" in t:
                start = random.choice(self._words)
                state = {"mode": "wordchain", "last": start, "used": [start], "turn": 1, "created_at": state.get("created_at", _utc_iso())}
                self._save(tenant, session_id, state)
                return PlayReply(text=f"끝말잇기 시작. 제가 먼저: '{start}'.\n당신 차례. '{start[-1]}'(으)로 시작하는 단어!", state=state)
            if "20" in t or "스무" in t:
                item = random.choice(self._twentyq_items)
                state = {"mode": "twentyq", "item": item, "q": 0, "created_at": state.get("created_at", _utc_iso())}
                self._save(tenant, session_id, state)
                return PlayReply(text="20문제(라이트) 시작. 네/아니오로 대답할게요. 질문해요.\n(예: '동물이야?', '음식이야?')\n맞히려면 '정답: ___'라고 해요.", state=state)
            # stay in menu
            return PlayReply(text="메뉴에서 골라줘요: 밸런스 / 끝말잇기 / 20문제", state=state)

        if mode == "balance":
            pair = tuple(state.get("pair") or ("A", "B"))
            pick = None
            if re.search(r"\bA\b", t, re.I) or t.startswith("A"):
                pick = "A"
            elif re.search(r"\bB\b", t, re.I) or t.startswith("B"):
                pick = "B"
            elif pair[0] in t:
                pick = "A"
            elif pair[1] in t:
                pick = "B"

            if not pick:
                return PlayReply(text="A 아니면 B로 골라줘요. (A/B)", state=state)

            comment = "오케이."
            if pick == "A":
                comment = f"A 선택. {pair[0]} 쪽이군요. 이유가 꽤 납득돼요."
            else:
                comment = f"B 선택. {pair[1]} 쪽이군요. 그 선택도 센스 있어요."

            # next
            pair2 = random.choice(self._balance_pairs)
            state["pair"] = pair2
            state["turn"] = int(state.get("turn", 1)) + 1
            self._save(tenant, session_id, state)
            return PlayReply(text=f"{comment}\n다음!\nA) {pair2[0]}\nB) {pair2[1]}\nA/B?", state=state)

        if mode == "wordchain":
            last = (state.get("last") or "")
            if not last:
                state["last"] = random.choice(self._words)
                last = state["last"]
            needed = last[-1]
            user_word = t.strip().split()[0] if t else ""
            if not user_word:
                return PlayReply(text=f"단어를 말해줘요. '{needed}'(으)로 시작!", state=state)
            if user_word[0] != needed:
                return PlayReply(text=f"첫 글자가 달라요. '{needed}'(으)로 시작해야 해요.", state=state)
            used = set(state.get("used") or [])
            if user_word in used:
                return PlayReply(text="그 단어는 이미 나왔어요. 다른 걸로!", state=state)

            used.add(user_word)

            # assistant picks a word starting with last char of user_word
            next_needed = user_word[-1]
            cand = [w for w in self._words if w and w[0] == next_needed and w not in used]
            if not cand:
                state["mode"] = "menu"
                self._save(tenant, session_id, state)
                return PlayReply(text=f"음… 제가 이어갈 단어가 없네요. 당신 승!\n다른 게임 할까요? (밸런스/20문제)", state=state)

            bot_word = random.choice(cand)
            used.add(bot_word)

            state["last"] = bot_word
            state["used"] = list(used)[:200]
            state["turn"] = int(state.get("turn", 1)) + 1
            self._save(tenant, session_id, state)

            return PlayReply(text=f"좋아요. '{user_word}'.\n그럼 저는 '{bot_word}'.\n당신 차례. '{bot_word[-1]}'(으)로 시작!", state=state)

        if mode == "twentyq":
            item = state.get("item") or {}
            name = item.get("name", "정답")
            cat = item.get("cat", "")
            tags = set(item.get("tags") or [])
            if t.lower().startswith("정답"):
                guess = t.split(":", 1)[-1].strip()
                if guess == name:
                    state["mode"] = "menu"
                    self._save(tenant, session_id, state)
                    return PlayReply(text=f"정답! {name} 맞아요.\n다른 게임 할까요? (밸런스/끝말잇기)", state=state)
                return PlayReply(text="아니에요. 계속 질문해도 돼요.", state=state)

            qn = int(state.get("q", 0)) + 1
            state["q"] = qn

            # keyword-based yes/no
            ans = "음… 애매한데요. 다시 물어봐줘요."
            lower = t.lower()
            if "동물" in t:
                ans = "네." if cat == "동물" else "아니오."
            elif "음식" in t or "먹" in t:
                ans = "네." if cat == "음식" else "아니오."
            elif "전자" in t or "기기" in t or "폰" in t:
                ans = "네." if cat == "전자" else "아니오."
            elif "탈것" in t or "바퀴" in t:
                ans = "네." if cat == "탈것" else "아니오."
            else:
                # tag heuristics
                for kw, tag in [("집", "집"), ("털", "털"), ("매", "매움"), ("치즈", "치즈"), ("읽", "읽기"), ("키보드", "키보드"), ("야외", "야외")]:
                    if kw in lower or kw in t:
                        ans = "네." if tag in tags else "아니오."
                        break
                else:
                    ans = random.choice(["네.", "아니오.", "음… 그럴 수도요.", "아마도요."])

            # soft hint after 8 questions
            hint = ""
            if qn in (6, 8, 10):
                hint = f" (힌트: 카테고리는 '{cat}')"

            self._save(tenant, session_id, state)
            return PlayReply(text=f"{ans}{hint}  (질문 {qn}/20)", state=state)

        # fallback
        state = {"mode": "menu", "created_at": state.get("created_at", _utc_iso())}
        self._save(tenant, session_id, state)
        return PlayReply(text="다시 시작할게요. '/play'라고 해줘요.", state=state)
