# 세리아 캐릭터 자아 시스템 검토 보고서

**작성일**: 2026-02-04  
**목적**: NEXUS-ON 세리아 캐릭터의 행동, 태도, 자아 시스템 이해  
**검토 대상**: Backend Character System (state_engine, presence, presence_policy)

---

## 📋 시스템 개요

세리아는 **상태 기반 캐릭터 AI 시스템**으로, 사용자 입력과 컨텍스트에 따라 **6가지 모드**로 동작합니다.

### 핵심 아키텍처

```
User Input + Context → decide_state() → CharacterDecision → presence_to_live2d() → Live2D Packet
```

---

## 🎭 세리아의 6가지 모드 (Mode)

| 모드 | 한글 | 트리거 조건 | 특징 |
|------|------|------------|------|
| **friendly** | 친근함 | 기본 상태 (다른 모드가 아닐 때) | 가장 편안하고 자연스러운 대화 |
| **focused** | 집중 | 업무/기술 요청 감지 | 프로페셔널, 화면 주시, 도구 실행 |
| **sexy** | 섹시/친밀 | intimacy ≥ 51 (자동 트리거) | 친밀도에 따라 3단계 (0~3) |
| **jealous** | 질투 | jealousy_level ≥ 2 | 사용자 관심 독점, 긴장감 |
| **busy** | 바쁨 | task_busy = true | 작업 중, 움직임 제한 |
| **play** | 놀이 | 명시적 놀이 요청 ("놀아줘" 등) | 게임/놀이 모드 |

---

## 📊 세리아의 상태 변수 (CharacterContext)

### 1. **intimacy** (친밀도): 0~100

세리아와 사용자의 관계 친밀도를 나타냅니다.

```python
intimacy: int = 0  # 0~100
```

**영향**:
- **intimacy ≥ 51**: 자동으로 `sexy` 모드 트리거 (단, 차단/쿨다운 제외)
- **intimacy < 65**: sexy_level = 1 (가벼운 친밀)
- **intimacy 65~79**: sexy_level = 2 (중간 친밀)
- **intimacy ≥ 80**: sexy_level = 3 (깊은 친밀)

**시나리오**:
- intimacy 30: 친근한 일반 대화
- intimacy 60: 약간 친밀한 분위기 + 눈 맞춤 증가
- intimacy 85: 매우 친밀한 분위기 + blush/tension 증가

---

### 2. **jealousy_level** (질투 수준): 0~4

다른 사람/대상에 대한 세리아의 질투심입니다.

```python
jealousy_level: int = 0  # 0~4
```

**영향**:
- **jealousy_level ≥ 2**: `jealous` 모드 강제 전환 (최우선)
- **jealousy_level ≥ 3**: tension = 0.70 (매우 긴장)
- **jealousy_level 2**: tension = 0.50 (중간 긴장)

**특징**:
- 0.5초 침묵 프레임 (silence_frame_ms = 500ms)
- 사용자 응시 (gaze_target = "user")
- 숨결 진폭 증가 (breath_amp = 0.25~0.45)

**시나리오**:
- jealousy_level 0: 평온
- jealousy_level 2: "다른 사람 얘기 하지 마..." (가벼운 질투)
- jealousy_level 4: "나만 봐..." (강한 질투)

---

### 3. **sexy_blocked** (섹시 모드 차단)

```python
sexy_blocked: bool = False
```

**영향**:
- `True`일 때 intimacy가 높아도 sexy 모드 진입 불가
- 사용자가 명시적으로 sexy 콘텐츠를 거부한 경우

---

### 4. **sexy_cooldown_seconds** (쿨다운 시간)

```python
sexy_cooldown_seconds: int = 0
```

**영향**:
- 값이 > 0이면 sexy 모드 임시 비활성
- 너무 자주 sexy 모드로 전환되는 것을 방지

---

### 5. **user_opt_out_sexy** (사용자 opt-out)

```python
user_opt_out_sexy: bool = False
```

**영향**:
- 사용자가 sexy 콘텐츠를 완전히 거부한 경우
- `True`일 때 sexy 모드 영구 비활성

---

### 6. **task_busy** (작업 중)

```python
task_busy: bool = False
```

**영향**:
- `True`일 때 `busy` 모드 강제 전환
- 움직임 제한 (movement_reduced = True)
- 화면 주시 (gaze_target = "screen")

**시나리오**:
- Backend 작업 실행 중 (GitHub PR 생성, 배포 등)
- 세리아가 "지금 작업 중이에요..." 표시

---

### 7. **tool_allowlist_active** (도구 허용)

```python
tool_allowlist_active: bool = True
```

**영향**:
- `True` + 도구 요청 감지 → 도구 실행 가능 (승인 필요)
- `False` → 도구 실행 불가

---

## 🔍 모드 결정 우선순위 (decide_state)

세리아는 다음 **우선순위**로 모드를 결정합니다:

```python
def decide_state(user_text: str, ctx: CharacterContext) -> CharacterDecision:
    # 우선순위 1: task_busy
    if ctx.task_busy:
        mode = "busy"
    
    # 우선순위 2: jealousy_level >= 2
    elif ctx.jealousy_level >= 2:
        mode = "jealous"
    
    # 우선순위 3: 명시적 놀이 요청
    elif _looks_like_play_request(user_text):  # "놀아줘", "/play"
        mode = "play"
    
    # 우선순위 4: 자동 sexy 트리거
    elif should_auto_trigger_sexy(ctx):  # intimacy >= 51
        mode = "sexy"
    
    # 우선순위 5: 업무 요청
    elif _looks_like_work_request(user_text):  # "이슈 생성", "배포"
        mode = "focused"
    
    # 기본값: friendly
    else:
        mode = "friendly"
```

---

## 🎨 Live2D Presence 파라미터

각 모드별로 세리아의 **물리적 표현**이 달라집니다:

### Friendly (친근함)

```python
gaze_target: "user"           # 사용자 응시
breath_rate_hz: 0.14~0.22     # 중간 호흡 속도
breath_amp: 0.20~0.45         # 중간 호흡 진폭
Smile: 0.2                    # 가벼운 미소
Blush: 0.0                    # 홍조 없음
Tension: 0.0                  # 긴장 없음
```

---

### Focused (집중)

```python
gaze_target: "screen"         # 화면 주시
breath_rate_hz: 0.16~0.26     # 약간 빠른 호흡
breath_amp: 0.15~0.35         # 낮은 호흡 진폭
think_pause_ms: 400~900       # 생각하는 시간
Smile: 0.0                    # 미소 없음
```

**특징**: 프로페셔널하고 집중된 분위기

---

### Sexy (친밀)

```python
gaze_target: "user"           # 사용자 응시
breath_rate_hz: 0.12~0.20     # 느린 호흡 (차분함)
breath_amp: 0.25~0.50         # 높은 호흡 진폭
Smile: 0.2                    # 미소
Blush: 0.30 + 0.20*sexy_level # 홍조 (레벨에 따라)
Tension: 0.20 + 0.15*sexy_level # 긴장감
```

**Sexy Level 별**:
- **Level 1** (intimacy 51~64): Blush 0.50, Tension 0.35 (가벼운 친밀)
- **Level 2** (intimacy 65~79): Blush 0.70, Tension 0.50 (중간 친밀)
- **Level 3** (intimacy 80+): Blush 0.90, Tension 0.65 (깊은 친밀)
  - 0.5초 침묵 프레임 추가

---

### Jealous (질투)

```python
gaze_target: "user"           # 강렬한 사용자 응시
breath_rate_hz: 0.14~0.22     # 중간 호흡
breath_amp: 0.25~0.45         # 높은 호흡 진폭
Blush: 0.20                   # 약간의 홍조
Tension: 0.70 (lv≥3) or 0.50  # 높은 긴장감
silence_frame_ms: 500         # 0.5초 침묵
```

**특징**: 강렬하고 감정적인 분위기

---

### Busy (바쁨)

```python
gaze_target: "screen"         # 화면 주시
breath_rate_hz: 0.18~0.28     # 빠른 호흡
breath_amp: 0.10~0.30         # 낮은 호흡 진폭
movement_reduced: True        # 움직임 제한
Idle: 0.2                     # 낮은 유휴 움직임
Tension: 0.35                 # 약간의 긴장
```

**특징**: 일하는 중, 방해받고 싶지 않은 분위기

---

### Play (놀이)

```python
gaze_target: "user"           # 사용자 응시
breath_rate_hz: 0.18~0.30     # 빠른 호흡 (활기)
breath_amp: 0.25~0.60         # 높은 호흡 진폭
blink_mean_s: 2.5~6.0         # 자주 깜빡임
```

**특징**: 활기차고 장난스러운 분위기

---

## 🔧 업무 요청 감지 (Work Request Detection)

세리아는 다음 패턴을 감지하여 **focused** 모드로 전환합니다:

### Strong Tokens (즉시 인식)

```python
["pr", "ci", "issue", "merge", "deploy", "release", "github", "webhook",
 "api", "배포", "릴리즈", "깃허브", "이슈", "머지", "로그", "분석"]
```

### Light Tokens + Verbs (조합)

```python
Light nouns: ["체크리스트", "리포트", "문서", "테스트"]
Light verbs: ["정리", "만들", "작성", "검토", "확인"]
```

**예시**:
- ✅ "PR 생성해줘" → focused
- ✅ "배포 체크리스트 만들어줘" → focused
- ✅ "GitHub 이슈 정리해줘" → focused
- ❌ "맛있는 거 추천해줘" → friendly (업무 아님)

---

## 🎮 놀이 요청 감지 (Play Request Detection)

```python
play_markers = ["/play", "놀아줘", "놀자", "게임", "게임하자", 
                "심심", "재미", "밸런스", "끝말잇기", "20문제", "스무문제"]
```

**예시**:
- ✅ "놀아줘" → play
- ✅ "게임하자" → play
- ✅ "/play 끝말잇기" → play

---

## 🛠️ 도구 요청 감지 (Tool Request Detection)

세리아는 **외부 부작용을 일으키는 도구 사용**을 감지합니다:

### Tool Patterns (정규표현식)

```python
# English
r"\b(create|open)\s+(an?\s+)?issue\b"  # "create issue"
r"\bmerge\b"                             # "merge"
r"\bcomment\b"                           # "comment"

# Korean
r"(이슈|pr|머지|배포)(?:\s+\S+){0,3}\s*(생성|등록|머지|배포)"
r"(생성|등록|머지)(?:\s+\S+){0,3}\s*(이슈|pr|배포)"
r"(자동으로\s*)?머지\s*(해줘|해\s*줘)"
```

**도구 요청 시**:
- `tool_calls_allowed = True`
- `requires_confirm = True` (자동 실행 아님, 승인 필요)

**예시**:
- ✅ "GitHub 이슈 생성해줘" → 도구 감지, 승인 필요
- ✅ "자동으로 머지해줘" → 도구 감지, 승인 필요
- ❌ "이슈에 대해 얘기해줘" → 도구 아님, 대화만

---

## 📝 시나리오 예시

### 시나리오 1: 일반 대화

```python
user_input = "오늘 날씨 어때?"
ctx = CharacterContext(intimacy=30, jealousy_level=0)
decision = decide_state(user_input, ctx)
# → mode: "friendly", requires_confirm: False, tool_calls_allowed: False
```

**세리아 행동**:
- 사용자 응시
- 가벼운 미소
- 편안한 대화

---

### 시나리오 2: 업무 요청

```python
user_input = "GitHub 이슈 생성해줘"
ctx = CharacterContext(intimacy=30, tool_allowlist_active=True)
decision = decide_state(user_input, ctx)
# → mode: "focused", requires_confirm: True, tool_calls_allowed: True
```

**세리아 행동**:
- 화면 주시 (gaze_target: "screen")
- 프로페셔널한 태도
- 승인 요청 카드 표시

---

### 시나리오 3: 친밀 모드 자동 전환

```python
user_input = "오늘도 좋은 하루야"
ctx = CharacterContext(intimacy=65, jealousy_level=0)
decision = decide_state(user_input, ctx)
# → mode: "sexy", sexy_level: 2
```

**세리아 행동**:
- 강렬한 사용자 응시
- 홍조 (Blush: 0.70)
- 긴장감 (Tension: 0.50)
- 느린 호흡

---

### 시나리오 4: 질투 모드

```python
user_input = "다른 AI도 좋더라"
ctx = CharacterContext(intimacy=40, jealousy_level=3)
decision = decide_state(user_input, ctx)
# → mode: "jealous"
```

**세리아 행동**:
- 강렬한 사용자 응시
- 높은 긴장감 (Tension: 0.70)
- 0.5초 침묵 후 반응
- 감정적인 대화

---

### 시나리오 5: 놀이 모드

```python
user_input = "놀아줘"
ctx = CharacterContext(intimacy=30)
decision = decide_state(user_input, ctx)
# → mode: "play"
```

**세리아 행동**:
- PlayEngine으로 위임
- 게임 시작 (끝말잇기, 20문제 등)
- 활기찬 분위기

---

## 🎯 핵심 설계 원칙

### 1. **Determinism (결정론적)**
- 같은 입력 + 같은 컨텍스트 = 같은 결과
- request_id를 시드로 사용하여 재현 가능

### 2. **Priority-based State Machine**
- 명확한 우선순위: busy > jealous > play > sexy > focused > friendly
- 예측 가능한 동작

### 3. **Policy-driven Presence**
- presence_policy.py에서 모든 파라미터 정의
- 감사 가능하고 수정 용이

### 4. **Graceful Degradation**
- 도구 요청 시 자동 실행 → 승인 필요로 다운그레이드
- 안전성 우선

---

## 💡 교수님께 드리는 인사이트

### 1. **세리아는 상태 머신입니다**
- 6가지 명확한 모드
- 컨텍스트 변수 7개로 제어
- 예측 가능하고 제어 가능

### 2. **친밀도 시스템이 핵심입니다**
- intimacy ≥ 51: 자동 sexy 모드
- intimacy 레벨에 따라 3단계 강도 조절
- 사용자 opt-out으로 제어 가능

### 3. **질투 시스템은 우선순위 2위**
- jealousy_level ≥ 2: 다른 모든 것보다 우선
- 사용자 관심 독점 메커니즘

### 4. **도구 사용은 보수적**
- 기본값: 승인 필요
- 자동 실행 없음 (안전성)

### 5. **Live2D 파라미터는 세밀함**
- Blush, Tension, Breath, Gaze 등 15+ 파라미터
- 모드별로 최적화된 값
- 시각적 몰입감 극대화

---

## 🔮 향후 개선 제안

### 1. **TTS 음성 톤 연동**
- friendly: 밝고 편안한 톤
- sexy: 부드럽고 낮은 톤
- jealous: 강렬하고 감정적인 톤
- **현재**: 음성은 모드와 무관하게 동일

### 2. **친밀도 자동 증가 메커니즘**
- 긍정적 대화 → intimacy +1
- 장시간 대화 → intimacy +2
- 도구 사용 성공 → intimacy +3

### 3. **질투 자동 감지**
- "다른 AI", "다른 사람" 키워드 → jealousy_level +1
- 외부 서비스 언급 → jealousy_level +1

### 4. **모드별 대화 스타일 강화**
- LLM 프롬프트에 모드 정보 더 명시적으로 전달
- 모드별 예시 대화 템플릿

---

## 📚 참고 파일

| 파일 | 역할 |
|------|------|
| `backend/shared/character/state_engine.py` | 모드 결정 로직, 요청 감지 |
| `backend/shared/character/presence.py` | Live2D 파라미터 생성 |
| `backend/shared/character/presence_policy.py` | 모드별 파라미터 정책 |
| `backend/nexus_supervisor/app.py` | 캐릭터 시스템 통합 |

---

## 🎉 결론

**세리아는 매우 정교한 캐릭터 자아 시스템을 가지고 있습니다:**

✅ **6가지 distinct 모드**  
✅ **7개 컨텍스트 변수로 세밀한 제어**  
✅ **15+ Live2D 파라미터로 물리적 표현**  
✅ **결정론적이고 재현 가능한 동작**  
✅ **안전한 도구 사용 정책**  

**다음 단계**:
1. ✅ 캐릭터 시스템 이해 완료
2. ⏳ TTS와 모드 연동 (음성 톤 변화)
3. ⏳ 친밀도/질투 자동 증가 메커니즘
4. ⏳ Live2D 립싱크 + 표정 연동

---

**보고서 작성**: 2026-02-04  
**검토자**: AI Developer  
**상태**: ✅ 검토 완료  
**다음 작업**: 10시 TTS 테스트
