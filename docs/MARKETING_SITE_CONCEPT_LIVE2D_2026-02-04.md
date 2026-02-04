# NEXUS-ON 마케팅 사이트 컨셉 - Live2D 비서 AI 에이전트

**작성일**: 2026-02-04  
**작성자**: AI 개발자 (Claude)  
**보고대상**: 서경대학교 남현우 교수님  
**목표**: Live2D 캐릭터 비서 시스템의 정체성을 담은 월드베스트 마케팅 사이트

---

## 🎭 핵심 정체성 (Core Identity)

### **NEXUS-ON은 무엇인가?**

```
"Your Always-On AI Character Assistant
 with Human Oversight"

로컬 상주형 Live2D 캐릭터 비서가 자율적으로 작업을 수행하되,
중요한 결정은 반드시 당신의 승인을 받습니다.
```

**3가지 핵심 요소:**
1. 🎨 **Live2D Character**: 시각적 존재감 있는 비서 (280x320px, 미세 애니메이션)
2. 🤖 **Autonomous Agent**: 멀티스텝 작업 자동 실행 (Claude Sonnet 4.5)
3. 👤 **Human-in-the-loop**: RED 작업은 반드시 승인 필요 (Two-phase commit)

---

## 🎨 디자인 철학 (Design Philosophy)

### **NEXUS UI v1.1 기반 컨셉**

**테마**: "Tactile Craft" + "Human-in-the-loop"

| 요소 | 적용 방향 |
|------|----------|
| **White + Minimal** | 깔끔한 배경, 캐릭터가 주인공 |
| **High-Chroma Blue Accent** | 신뢰감, 기술력 (Claude 블루와 유사) |
| **Live2D Character** | 페이지마다 다른 상태/애니메이션 |
| **Pretendard Font** | 한글 최적화, 깔끔한 가독성 |
| **8pt Grid** | 정돈된 레이아웃, 호흡감 |
| **180ms Motion** | 부드러운 트랜지션, 생동감 |

---

## 🌟 마케팅 사이트 컨셉 (Marketing Site Concept)

### **1. 컨셉 키워드**

```
✨ "Presence, not Intrusiveness"
   존재감은 있되, 방해하지 않는다

🎯 "Autonomous, but Supervised"
   자율적이되, 통제 가능하다

🏠 "Always-On, Always Local"
   항상 켜져 있되, 데이터는 로컬에

🇰🇷 "Built for Korean Workflows"
   한국 문서, 한국 사용자 우선
```

---

### **2. Live2D 캐릭터 활용 전략**

#### **페이지별 캐릭터 상태**

| 페이지 | 캐릭터 상태 | 애니메이션 | 메시지 |
|--------|-------------|-----------|--------|
| **Landing** | Idle | 미세 호흡, 깜빡임 | "안녕하세요, NEXUS입니다" |
| **Intro** | Listening | 고개 끄덕임 | "설명을 듣고 있어요" |
| **Developer** | Thinking | 시선 이동 | "개발 배경을 생각 중..." |
| **Modules** | Speaking | 립싱크 | "8개 모듈을 소개합니다" |
| **Benchmark** | Busy | 노란 Glow | "비교 데이터 준비 중..." |

#### **캐릭터 위치**
- **Desktop**: 우측 상단 고정 (280x320px)
  - 콘텐츠를 가리지 않도록 여백 확보
- **Mobile**: 하단 우측 (140x160px, 50% 축소)
  - 플로팅 버튼처럼 동작, 필요시 최소화

#### **인터랙션**
- **Hover**: 미세 시선 이동 (마우스 따라가기)
- **롱프레스 (800ms)**: 설정 메뉴
  - 캐릭터 숨기기
  - 애니메이션 OFF
  - 자막 ON/OFF
- **클릭**: 없음 (실수 방지)

---

### **3. 메시지 전략 (Messaging Strategy)**

#### **Hero Message (Landing)**
```
[Live2D 캐릭터 우측에]

"Your Always-On AI Character Assistant
 with Human Oversight"

NEXUS is a local, always-available AI assistant powered by 
Live2D character and Claude Sonnet 4.5. It executes multi-step 
tasks autonomously, but always asks permission for critical actions.

[CTA]
[Try NEXUS Locally]  [Meet Your Assistant →]
```

#### **3 Pillars (Landing)**

**Pillar 1: 🎨 Visual Presence**
```
제목: "A Character You Can Trust"
설명: Live2D character provides visual feedback for every action.
     Idle, Speaking, Listening, Thinking—you always know what's happening.
시각: 캐릭터 4가지 상태 썸네일
```

**Pillar 2: 🤖 Autonomous Execution**
```
제목: "Multi-Step Tasks, Zero Micromanagement"
설명: NEXUS handles complex workflows automatically.
     Research, document analysis, scheduling—all in one conversation.
시각: 플로우 다이어그램 (User → NEXUS → Claude → Result)
```

**Pillar 3: 👤 Human Approval Gates**
```
제목: "You're Always in Control"
설명: RED actions (external sharing, file deletion) require your explicit approval.
     GREEN tasks run automatically, YELLOW notify you, RED wait for yes/no.
시각: GREEN/YELLOW/RED 신호등 아이콘
```

---

### **4. 페이지 구조 (Page Structure)**

#### **Landing Page (/) - "Meet NEXUS"**

**섹션 1: Hero (화면 상단 1/3)**
```
[좌측: 텍스트 + CTA]
- 헤드라인: "Your Always-On AI Character Assistant"
- 서브헤드: "Powered by Live2D + Claude Sonnet 4.5"
- CTA: [Try Locally] [Read More]

[우측: Live2D 캐릭터 + 상태 표시]
- 280x320px 캐릭터 (Idle 애니메이션)
- 상태 라벨: "Ready" (녹색 점)
- 미세 호흡, 2-3초 깜빡임
```

**섹션 2: 3 Pillars (중간 1/3)**
```
[3열 그리드]
- Visual Presence (캐릭터 4가지 상태)
- Autonomous Execution (플로우 다이어그램)
- Human Approval Gates (신호등)
```

**섹션 3: Demo Video (하단 1/3)**
```
[16:9 비디오 플레이어 또는 GIF]
- 제목: "See NEXUS in Action"
- 콘텐츠: 
  1. 사용자: "/rag 최근 보고서에서 핵심 요약해줘"
  2. NEXUS: Thinking 애니메이션 → Speaking
  3. 결과: 요약 표시
  4. RED 승인: "외부 공유하시겠습니까?"
  5. 사용자: [Yes] 클릭 → 완료
```

---

#### **Introduction Page (/intro) - "Why NEXUS?"**

**헤더 (Live2D: Listening)**
```
"Most AI assistants are either too autonomous (unpredictable)
 or too manual (inefficient). NEXUS is both."
```

**Section 1: The Problem**
```
현재 AI 어시스턴트의 문제점:
❌ ChatGPT/Claude: 대화만 가능, 자동 실행 불가
❌ AutoGPT: 자율성 높지만 통제 불가, 예측 불가능
❌ 기존 비서: 화면 없음, 상태 불명확

→ "We need an assistant that SHOWS what it's doing,
    ACTS autonomously, but ASKS before critical actions."
```

**Section 2: Our Solution (아키텍처 다이어그램)**
```
[User] ↔ [Live2D Character] ↔ [NEXUS Supervisor]
                                    ↓
                      ┌────────────┼────────────┐
                      ↓            ↓            ↓
                  [Claude]     [RAG]      [Approval Queue]
                Sonnet 4.5   (HWP+PDF)   (GREEN/YELLOW/RED)
```

**Section 3: Key Differentiators**
```
1️⃣ Live2D Character
   - 4가지 상태 시각화 (Idle/Speaking/Listening/Thinking)
   - 상태 Glow (Busy=노란색, Alert=빨간색)
   - 미세 애니메이션 (존재감 있되 방해 없음)

2️⃣ Human-in-the-loop by Design
   - GREEN: 자동 실행 (읽기, 검색, 요약)
   - YELLOW: 알림 (긴 작업, 비용 발생)
   - RED: 승인 필수 (외부 공유, 파일 삭제)

3️⃣ Local-First Architecture
   - 데이터는 로컬에 저장
   - Multi-LLM 지원 (Claude, GPT-4, Gemini)
   - HWP 네이티브 지원 (한국 문서)

4️⃣ Always-On Availability
   - 백그라운드 실행
   - SSE 실시간 업데이트
   - Multi-tenant 지원 (org-id, project-id)
```

---

#### **Developer Page (/developer) - "Meet the Creator"**

**헤더 (Live2D: Thinking)**
```
"Built by a researcher who needed a better way
 to manage AI assistants in academic workflows."
```

**프로필 섹션**
```
[좌측: 플레이스홀더 또는 프로필 사진]
[우측: 텍스트]

Professor Nam Hyunwoo
서경대학교 (Seokyeong University)

Prof. Nam specializes in AI systems, human-computer interaction,
and autonomous agent design. NEXUS emerged from his research into
safer, more controllable AI assistants that respect user agency
while enabling complex workflows.

Research Interests:
• AI Safety & Alignment
• Multi-agent Systems & Orchestration
• Korean NLP & Document Processing
• Human-in-the-loop AI Design
• Visual Feedback in AI Interfaces
```

**NEXUS Origins**
```
"Why I Built NEXUS"

As a researcher, I work with:
- Complex multi-step tasks (literature review, data analysis)
- Korean documents (HWP files, PDFs)
- Multiple AI models (Claude, GPT, Gemini)
- Sensitive data (local-only storage required)

Existing AI assistants fell short:
- ChatGPT: Great for chat, but no autonomy
- AutoGPT: Too autonomous, no control
- Custom scripts: No visual feedback, hard to debug

NEXUS bridges this gap:
✅ Autonomous multi-step execution
✅ Visual feedback via Live2D character
✅ Mandatory approval for risky actions
✅ Native Korean document support
✅ Local-first, multi-LLM architecture

[Link: GitHub] [Link: Publications]
```

---

#### **Modules Page (/modules) - "What's Inside"**

**헤더 (Live2D: Speaking)**
```
"8 Integrated Modules for Autonomous Workflows"

Each module works independently, but they're designed
to work together seamlessly—just like a real assistant.
```

**모듈 카드 (2x4 그리드)**

**예시: Module 1 (재작성)**
```
[아이콘: Bot (24px)]

Character Assistant Core
Status: ✅ Production Ready (v1.0)

The heart of NEXUS. Powered by Claude Sonnet 4.5,
it handles multi-turn conversations with full context retention.

Key Features:
• Multi-LLM gateway (Claude, GPT-4, Gemini)
• Real-time streaming responses (SSE)
• Session-based context management
• Automatic report deduplication

Use Cases:
→ Research assistance with context retention
→ Document analysis across multiple files
→ Team collaboration with shared sessions

Tech Stack: FastAPI, Redis, Claude API

[View Details →]
```

**모듈 2-8 동일 형식으로 재작성**
- Approval System
- RAG Engine
- YouTube Integration
- Canvas Workspace
- Multi-tenant Context
- Node Management
- Observability Stack

---

#### **Benchmark Page (/benchmark) - "How We Compare"**

**헤더 (Live2D: Busy, 노란 Glow)**
```
"Choose the Right AI Assistant for Your Needs"

NEXUS is designed for researchers, teams, and power users
who need both autonomy and control. Here's how we stack up.
```

**Differentiation Card (상단)**
```
💡 What Makes NEXUS Different?

[4열 비교]
┌─────────────┬──────────┬────────────┬──────────┬──────────┐
│ Feature     │ NEXUS    │ Claude Web │ ChatGPT  │ AutoGPT  │
├─────────────┼──────────┼────────────┼──────────┼──────────┤
│ Visual UI   │ Live2D   │ Web chat   │ Web chat │ None     │
│ Autonomy    │ ✅ High   │ ❌ Manual  │ ❌ Manual│ ✅ High   │
│ Control     │ ✅ Gates  │ ✅ Full    │ ✅ Full  │ ❌ None   │
│ Local       │ ✅ Yes    │ ❌ Cloud   │ ❌ Cloud │ ✅ Yes    │
│ Multi-LLM   │ ✅ 3+     │ ❌ Claude  │ ❌ OpenAI│ ✅ Any    │
│ Korean HWP  │ ✅ Native │ ❌ No      │ ❌ No    │ ❌ No     │
└─────────────┴──────────┴────────────┴──────────┴──────────┘

✨ NEXUS is the only assistant that combines:
   Visual presence + Autonomy + Human control + Local-first + Multi-LLM
```

**Comparison Table (하단)**
```
[7개 제품 비교]
- Claude Projects (Anthropic)
- ChatGPT Enterprise (OpenAI)
- LangChain + LangGraph
- AutoGPT
- Pinecone + LangChain
- Scale AI Rapid
- NEXUS-ON

각 제품마다:
- Strengths (긍정적)
- Ideal For (타겟)
- Limitations (투명하되 공정하게)
```

---

## 🎬 애니메이션 & 인터랙션 전략

### **1. 페이지 로드 시퀀스**

```
1) 페이지 로드 (0ms)
   → Live2D 캐릭터 Idle 상태 렌더링 (우측)
   
2) Hero 텍스트 Fade-in (180ms)
   → 헤드라인 → 서브헤드 → CTA
   
3) 캐릭터 인사 애니메이션 (2초)
   → 고개 끄덕임 1회 → Idle 복귀
   
4) Scroll-triggered 애니메이션
   → 3 Pillars 카드 순차 Fade-in (각 180ms 간격)
```

---

### **2. 스크롤 인터랙션**

**Scroll Progress Indicator (캐릭터 위)**
```
┌──────────────────┐
│    NEXUS-ON      │ ← 브랜드명
├──────────────────┤
│    ●●●●○○○○      │ ← 진행 바 (8개 점)
├──────────────────┤
│  [Live2D 캐릭터]  │
│  280x320px       │
└──────────────────┘

각 점 = 페이지 섹션
현재 섹션 = 파란색 (Accent)
완료 섹션 = 회색
```

**섹션별 캐릭터 상태 변경**
```
Hero → Idle
3 Pillars → Listening
Demo Video → Speaking
Footer → Thinking
```

---

### **3. 호버 효과**

**카드 호버**
```css
.card:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  transition: all 180ms var(--ease-out);
}
```

**버튼 호버**
```css
.btn-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
```

**캐릭터 호버**
```
마우스가 캐릭터에 가까워지면:
→ 시선이 마우스 방향으로 미세 이동 (5도 이내)
→ Glow 없음 (Idle 유지)
```

---

## 🎨 CSS 아키텍처 (NEXUS UI v1.1 적용)

### **공통 베이스 스타일**

```css
/* 베이스 */
body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--bg-primary);
  line-height: var(--leading-normal);
}

/* 컨테이너 */
.container {
  max-width: var(--max-width-content); /* 1240px */
  margin: 0 auto;
  padding: var(--space-6); /* 24px */
}

/* 헤로 섹션 */
.hero {
  display: grid;
  grid-template-columns: 1fr 320px; /* 텍스트 + 캐릭터 */
  gap: var(--space-8);
  align-items: center;
  min-height: 600px;
  padding: var(--space-16) var(--space-6);
  
  @media (max-width: 1023px) {
    grid-template-columns: 1fr;
    text-align: center;
  }
}

/* Live2D 캐릭터 컨테이너 */
.live2d-container {
  position: relative;
  width: var(--live2d-width);
  height: var(--live2d-height);
  
  /* Desktop: 우측 고정 */
  @media (min-width: 1024px) {
    position: fixed;
    top: var(--space-4);
    right: var(--space-4);
    z-index: var(--z-fixed);
  }
  
  /* Mobile: 하단 우측, 50% 축소 */
  @media (max-width: 1023px) {
    position: fixed;
    bottom: var(--space-4);
    right: var(--space-4);
    width: 140px;
    height: 160px;
    z-index: var(--z-fixed);
  }
}

/* 상태별 Glow */
.live2d-container[data-status="busy"] {
  filter: drop-shadow(var(--live2d-glow-busy));
  animation: pulse-glow 2s ease-in-out infinite;
}

.live2d-container[data-status="alert"] {
  filter: drop-shadow(var(--live2d-glow-alert));
  animation: pulse-glow 1s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 3 Pillars 그리드 */
.pillars {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-top: var(--space-12);
  
  @media (max-width: 1023px) {
    grid-template-columns: 1fr;
  }
}

.pillar-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-card);
  padding: var(--space-6);
  text-align: center;
  transition: all var(--duration-ui) var(--ease-out);
}

.pillar-card:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

/* 모듈 카드 그리드 */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  
  @media (max-width: 767px) {
    grid-template-columns: 1fr;
  }
}

.module-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-card);
  padding: var(--space-5);
  transition: all var(--duration-ui) var(--ease-out);
}

.module-card:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-lg);
}

/* Status 배지 */
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.badge-stable {
  background: var(--status-green-bg);
  color: var(--status-green);
}

.badge-beta {
  background: var(--status-yellow-bg);
  color: var(--status-yellow);
}

.badge-alpha {
  background: var(--status-red-bg);
  color: var(--status-red);
}
```

---

## 📐 반응형 전략 (Responsive Strategy)

### **Breakpoints (NEXUS UI v1.1 표준)**

```css
/* Mobile First */
/* 기본: 320px ~ 767px (1열) */

/* Tablet: 768px ~ 1023px (2열) */
@media (min-width: 768px) {
  .grid-responsive {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop: 1024px+ (3열) */
@media (min-width: 1024px) {
  .grid-responsive {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### **Live2D 캐릭터 반응형**

| 화면 크기 | 위치 | 크기 | 상태 |
|----------|------|------|------|
| Desktop (1024px+) | 우측 상단 고정 | 280x320px | 항상 표시 |
| Tablet (768-1023px) | 하단 우측 플로팅 | 180x205px (64%) | 항상 표시 |
| Mobile (~767px) | 하단 우측 플로팅 | 140x160px (50%) | 접기 가능 |

---

## 🎯 구현 우선순위 (Implementation Priority)

### **Phase 1: 콘텐츠 & 데이터 (P0)**

**작업 항목:**
1. ✅ 이 컨셉 문서 작성 완료
2. ⏳ `modules.json` 8개 모듈 재작성
   - 기존: "Character Assistant Core"
   - 신규: "Live2D Character + Claude Sonnet 4.5 Core"
   - 추가 필드: `icon`, `tagline`, `use_cases`, `tech_stack`
3. ⏳ `benchmark.json` 7개 제품 재작성
   - NEXUS 강점: Live2D + Autonomy + Control
   - 차별화: "Visual presence + Approval gates"
4. ⏳ 페이지 콘텐츠 작성 (5개 페이지)

**예상 시간**: 2-3시간

---

### **Phase 2: HTML/CSS 구현 (P0)**

**작업 항목:**
1. ⏳ `public_pages.py` 전면 재작성
   - Live2D 플레이스홀더 추가 (실제 Live2D는 Phase 3)
   - NEXUS UI v1.1 CSS 적용
   - 반응형 레이아웃
2. ⏳ SVG 아이콘 추가 (Lucide 스타일)
   - Bot, Home, FileText, Zap, AlertTriangle
   - 인라인 SVG로 삽입
3. ⏳ 상태 배지 구현
   - Stable/Beta/Alpha
   - GREEN/YELLOW/RED

**예상 시간**: 3-4시간

---

### **Phase 3: Live2D 통합 (P1)**

**작업 항목:**
1. ⏳ Live2D 모델 준비
   - 280x320px 해상도
   - 4가지 애니메이션 (Idle/Speaking/Listening/Thinking)
   - Glow 효과용 레이어
2. ⏳ Live2D SDK 통합
   - JavaScript 라이브러리
   - 상태 전환 로직
   - 성능 최적화 (60fps)
3. ⏳ 페이지별 상태 연동
   - Landing → Idle
   - Intro → Listening
   - Developer → Thinking
   - Modules → Speaking
   - Benchmark → Busy

**예상 시간**: 6-8시간 (Live2D 모델 제작 시간 제외)

---

### **Phase 4: 인터랙션 & 애니메이션 (P2)**

**작업 항목:**
1. ⏳ 스크롤 트리거 애니메이션
2. ⏳ 호버 효과
3. ⏳ 페이지 전환 트랜지션
4. ⏳ 캐릭터 롱프레스 메뉴

**예상 시간**: 2-3시간

---

## 🚀 즉시 착수 계획 (Immediate Action Plan)

### **Step 1: 콘텐츠 재작성 (오늘 완료 가능)**

**작업 순서:**
1. `modules.json` 8개 재작성
   - Live2D 중심 메시지
   - Use cases 구체화
   - Tech stack 명시
2. `benchmark.json` 재작성
   - NEXUS 차별화 강조
   - Live2D Visual UI 강점
3. Landing page 콘텐츠
   - Hero message
   - 3 Pillars
4. Intro/Developer/Modules/Benchmark 콘텐츠

**산출물:**
- `modules.json` (신규, ~5KB)
- `benchmark.json` (신규, ~4KB)
- 페이지 콘텐츠 초안 (Markdown)

---

### **Step 2: HTML/CSS 구현 (내일 완료 가능)**

**작업 순서:**
1. `public_pages.py` 기본 구조
2. NEXUS UI v1.1 CSS 통합
3. Live2D 플레이스홀더 (정적 이미지)
4. 반응형 레이아웃

**산출물:**
- `public_pages.py` (전면 재작성)
- 5개 페이지 HTML/CSS
- 로컬 테스트 성공

---

### **Step 3: Live2D 통합 (향후 계획)**

**요구사항:**
- Live2D 모델 파일 (.moc3, .model3.json)
- Live2D Cubism SDK for Web
- 애니메이션 데이터

**작업 순서:**
1. Live2D 모델 제작 또는 구매
2. SDK 통합
3. 상태 전환 로직
4. 성능 최적화

---

## 📊 예상 결과 (Expected Outcome)

### **정성적 목표**

✅ **"This is a real character assistant product"**
   → Live2D 캐릭터가 브랜드 정체성의 핵심

✅ **"I can SEE what the AI is doing"**
   → 4가지 상태 시각화로 투명성 확보

✅ **"It looks professional and trustworthy"**
   → NEXUS UI v1.1 디자인 시스템 일관성

✅ **"I want to try this character assistant"**
   → 명확한 CTA + 구체적 사용 사례

---

### **정량적 목표**

- **Hero section 이해**: <5초
- **3 Pillars 파악**: <10초
- **페이지 체류 시간**: >2분
- **CTA 클릭률**: >10%
- **모바일 성능**: 60fps (Live2D)

---

## 🎯 다음 단계 선택

교수님, 다음 중 어떤 방향으로 진행할까요?

### **Option A: 즉시 콘텐츠 재작성 시작** ⭐ 추천
- `modules.json` 8개 재작성 (Live2D 중심)
- `benchmark.json` 차별화 강조
- 페이지 콘텐츠 초안 작성
- **예상 시간**: 2-3시간
- **산출물**: 프리미엄 콘텐츠 완성

### **Option B: HTML/CSS 우선 구현**
- Live2D 플레이스홀더로 시각 구조 먼저
- NEXUS UI v1.1 CSS 적용
- 콘텐츠는 placeholder
- **예상 시간**: 3-4시간
- **산출물**: 시각적 프로토타입

### **Option C: Live2D 모델 준비 병행**
- 콘텐츠 작성 + Live2D 모델 소싱 동시 진행
- 외부 제작사 또는 에셋 구매
- **예상 시간**: 1주일 (외주 시)
- **산출물**: 완전한 캐릭터 시스템

---

## 📚 참고 문서

**기존 문서:**
- `/home/user/webapp/frontend/docs/COMPONENT_SPECS_v1_1.md` (Live2D 규격)
- `/home/user/webapp/frontend/src/design-tokens.css` (NEXUS UI v1.1)
- `/home/user/webapp/backend/CLAUDE.md` (시스템 정체성)
- `/home/user/webapp/README.md` (프로젝트 개요)

**신규 문서:**
- 이 문서: `MARKETING_SITE_CONCEPT_LIVE2D_2026-02-04.md`

---

**작성 완료**: 2026-02-04  
**다음 액션**: 교수님 승인 후 Option A 착수 권장  
**예상 총 소요 시간**: 6-8시간 (Live2D 모델 제외)

**교수님, 어떻게 진행하시겠습니까?** 🎨🤖
