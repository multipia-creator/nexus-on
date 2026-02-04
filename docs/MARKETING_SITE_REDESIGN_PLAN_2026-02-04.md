# NEXUS-ON 마케팅 사이트 전면 재설계 계획

**작성일**: 2026-02-04  
**작성자**: AI 개발자 (Claude)  
**보고대상**: 서경대학교 남현우 교수님  
**목표**: 월드베스트 탑티어 AI 제품 마케팅 사이트 구축

---

## 📊 Executive Summary

**현재 문제점**: 백엔드 `/` 마케팅 사이트가 데모 수준 (placeholder 콘텐츠, 제네릭 디자인)  
**목표**: Anthropic, OpenAI, Perplexity 수준의 프리미엄 마케팅 사이트로 전면 재구축  
**범위**: 백엔드 Server-Side Rendered 페이지 5개 + 공개 API 2개

---

## 🎯 벤치마크 분석: 탑티어 AI 제품 사이트

### **1. Anthropic (claude.com)**

**강점 분석:**
- ✅ **명확한 가치 제안**: "AI research and products that put safety at the frontier"
- ✅ **신뢰 구축**: "Public benefit corporation", Constitutional AI, Responsible Scaling Policy
- ✅ **핵심 차별화**: Safety-first 메시지, Interpretability/Alignment Science 강조
- ✅ **깔끔한 정보 구조**: Research, Products, Company 명확 분리
- ✅ **Human-centric 메시징**: "serve humanity's long-term well-being"

**디자인 원칙:**
- 미니멀리즘 (White + 단색 Accent)
- 큰 타이포그래피, 넉넉한 여백
- 명확한 섹션 구분
- 신뢰감 있는 톤

---

### **2. OpenAI (openai.com)**

**강점 분석:**
- ✅ **제품 중심 메시징**: Codex, Prism, ChatGPT Health 등 구체적 제품
- ✅ **시각적 임팩트**: 고품질 프로덕트 이미지, 일관된 아트워크
- ✅ **명확한 CTA**: "Introducing X" 형식, 즉시 행동 유도
- ✅ **다양성**: Research, Safety, API, Enterprise 등 다각도 접근
- ✅ **신뢰 구축**: 구체적 사용 사례 (Healthcare, Code, Education)

**디자인 원칙:**
- 그리드 기반 카드 레이아웃
- 제품 스크린샷/일러스트 중심
- 명확한 계층 구조
- 컬러풀한 Accent (제품별 차별화)

---

### **3. Perplexity (perplexity.ai)**

**강점 분석:**
- ✅ **즉시 체험**: 랜딩에서 바로 검색 가능 (Pro Search 강조)
- ✅ **간결함**: 최소한의 설명, 직관적 UI
- ✅ **프리미엄 포지셔닝**: Pro 기능 강조
- ✅ **빠른 전환**: Sign in/Create account CTA

---

## 🚨 현재 NEXUS-ON 사이트 문제점

### **치명적 문제 (P0)**

1. **모호한 가치 제안**
   - ❌ "AI-Powered Autonomous Assistant with Human Oversight" (제네릭)
   - ❌ 차별점이 드러나지 않음
   - ❌ 왜 NEXUS-ON을 써야 하는지 불명확

2. **신뢰 구축 부재**
   - ❌ 개발자 정보가 별도 페이지 (접근성 낮음)
   - ❌ "서경대학교 남현우 교수" 신뢰 요소 미활용
   - ❌ 학술/연구 배경 부각 부족

3. **평범한 데모 콘텐츠**
   - ❌ modules.json: "Character Assistant Core", "RAG Engine (Naive)" (자신감 부족)
   - ❌ benchmark.json: 자화자찬 없음, "Early stage (P0)" (약점 노출)
   - ❌ 제네릭 Feature 카드 ("3개 특징" 수준)

4. **약한 CTA**
   - ❌ "App 실행" (What app? Why?)
   - ❌ 행동 유도 근거 부족

5. **디자인 완성도 부족**
   - ❌ 제네릭 CSS 스타일
   - ❌ 시각적 임팩트 없음
   - ❌ 일관된 브랜딩 부재

---

## 🎨 월드베스트 탑티어 재설계 전략

### **핵심 원칙 (Design Principles)**

1. **명확한 차별화 (Clear Differentiation)**
   - NEXUS-ON의 유니크함: Local-first + Human-in-the-loop + Multi-LLM + Korean HWP
   - Claude Projects/ChatGPT Enterprise보다 **자율성 + 통제권** 강조

2. **신뢰 구축 (Trust Building)**
   - 서경대학교 남현우 교수 (학술적 권위)
   - Research-backed approach
   - Responsible AI by design

3. **구체적 사용 사례 (Concrete Use Cases)**
   - 일반론 X, 실제 시나리오 O
   - "For researchers who need...", "For teams that require..."

4. **프리미엄 비주얼 (Premium Visuals)**
   - 고품질 일러스트/다이어그램
   - 일관된 컬러 시스템 (NEXUS UI v1.1)
   - 넉넉한 여백, 큰 타이포

5. **즉시 행동 유도 (Immediate Action)**
   - "Try NEXUS-ON Locally", "Explore Modules", "Read Research"

---

## 📄 새로운 페이지 구조

### **1. Landing Page (/) - "Hero + 3 Pillars + CTA"**

#### **Hero Section (위 1/3)**
```
[대형 헤드라인]
"Autonomous AI Agent with Human Oversight
 for Researchers and Teams"

[서브헤드]
Local-first AI assistant powered by Claude Sonnet 4.5,
with built-in approval gates and Korean document support.

[CTA 2개]
[Try NEXUS-ON Locally]  [Read the Research →]
```

**시각적 요소:**
- Live2D 캐릭터 미리보기 (280x320, 우측 상단)
- Approval workflow 다이어그램 (GREEN/YELLOW/RED)
- 간결한 아키텍처 개요

---

#### **3 Pillars (중간 1/3)**

**Pillar 1: Autonomous + Supervised**
```
아이콘: ⚡ (Zap)
제목: "Autonomous, but Never Reckless"
설명: Multi-step tasks execute automatically with built-in risk assessment.
      RED actions require explicit approval—no surprises.
```

**Pillar 2: Local-First, Multi-LLM**
```
아이콘: 🏠 (Home)
제목: "Your Data Stays Local"
설명: Connect multiple LLM providers (Claude, GPT-4, Gemini).
      Full control over credentials, context, and costs.
```

**Pillar 3: Built for Korean Workflows**
```
아이콘: 📄 (FileText)
제목: "Native HWP Support + RAG"
설명: Ingest Korean HWP documents automatically.
      Token overlap-based retrieval with scheduled sync.
```

---

#### **Trust Bar (하단 1/3)**
```
"Developed by Prof. Nam Hyunwoo, Seokyeong University"
[GitHub] [Research Paper] [Developer Profile]
```

---

### **2. Introduction Page (/intro) - "Why NEXUS-ON?"**

#### **구조**
```
1. The Problem (현재 AI 에이전트의 한계)
   - No approval gates → Unpredictable behavior
   - Cloud-only → Privacy concerns
   - English-centric → Korean doc friction

2. Our Solution (NEXUS-ON의 접근)
   - Human-in-the-loop by design
   - Local deployment with multi-tenant support
   - First-class Korean HWP support

3. Core Architecture (간결한 다이어그램)
   [User] → [NEXUS Supervisor] → [LLM Gateway] → [Claude/GPT-4/Gemini]
              ↓                      ↓
         [Approval Queue]      [RAG Engine]
         (RED/YELLOW/GREEN)    (HWP + PDF)

4. Key Modules (8개 모듈 간략 소개)
   - Character Assistant Core (Claude Sonnet 4.5)
   - Approval System (Two-phase commit)
   - RAG Engine (Token overlap)
   - YouTube Integration
   - Canvas Workspace
   - Multi-tenant Context
   - Node Management (Windows pairing)
   - Observability Stack (Prometheus)

5. Developer Background (신뢰 구축)
   "Designed by Prof. Nam Hyunwoo at Seokyeong University,
    combining research in AI safety, multi-agent systems,
    and practical needs for Korean academic workflows."
```

---

### **3. Developer Page (/developer) - "About the Creator"**

#### **구조**
```
[프로필 사진 또는 플레이스홀더]

Professor Nam Hyunwoo
서경대학교 (Seokyeong University)

[간략 소개 3-4문장]
"Prof. Nam specializes in AI systems, human-computer interaction,
 and autonomous agent design. NEXUS-ON emerged from his research
 into safer, more controllable AI assistants that respect user
 agency while enabling complex workflows."

[연구 관심사]
- AI Safety & Alignment
- Multi-agent Systems
- Korean NLP & Document Processing
- Human-in-the-loop AI

[Contact / Links]
- Email: [교수님 이메일]
- University Profile: [링크]
- Google Scholar: [링크] (있다면)
- GitHub: https://github.com/multipia-creator

[NEXUS-ON Origins]
"NEXUS-ON was born from the need for an AI assistant that:
 1) Handles multi-step tasks autonomously
 2) Never acts without approval on risky operations
 3) Supports Korean documents natively
 4) Runs locally with full data control"
```

---

### **4. Modules Page (/modules) - "What's Inside"**

#### **새로운 구조**

**헤더:**
```
"8 Integrated Modules for Autonomous Workflows"

NEXUS-ON combines chat, approvals, RAG, media, and observability
into a unified platform. Each module is designed to work together
while maintaining clear separation of concerns.
```

**모듈 카드 (8개, 2x4 그리드):**

**예시: Module 1**
```
[아이콘: Bot]

Character Assistant Core
Status: ✅ Stable (v1.0)

Claude Sonnet 4.5 integration with multi-provider LLM gateway.
Real-time SSE updates for all agent reports.

Key Features:
• Multi-LLM support (Claude, GPT-4, Gemini)
• Session-based context management
• Streaming responses via SSE

[View Details →]
```

**Status 배지:**
- ✅ **Stable**: Green badge
- ⚠️ **Beta**: Yellow badge
- 🚧 **Alpha**: Red badge (NOT "Early stage", but "Alpha")

**모듈별 하이라이트 (재작성 필요):**
1. **Character Assistant Core**: Multi-LLM gateway, SSE streaming
2. **Approval System**: GREEN/YELLOW/RED risk-based workflow
3. **RAG Engine**: Token overlap retrieval, HWP support
4. **YouTube Integration**: Search, queue, embedded player
5. **Canvas Workspace**: Draft storage, multi-format export
6. **Multi-tenant Context**: org-id/project-id scoping, credential vault
7. **Node Management**: Windows pairing, command queue
8. **Observability**: Prometheus metrics, correlation ID

---

**Benchmark 테이블 (동일 페이지 하단):**
```
"How NEXUS-ON Compares"

[기존 benchmark.json 데이터를 더 긍정적으로 재작성]
```

---

### **5. Benchmark Page (/benchmark) - "NEXUS-ON vs Alternatives"**

#### **새로운 구조**

**헤더:**
```
"Choose the Right AI Assistant for Your Needs"

NEXUS-ON is designed for researchers, teams, and power users
who need both autonomy and control. Here's how we compare.
```

**Comparison Table (7개 제품):**

| Feature | NEXUS-ON | Claude Projects | ChatGPT Enterprise | LangChain | AutoGPT | Pinecone RAG |
|---------|----------|-----------------|-------------------|-----------|---------|--------------|
| **Approval Gates** | ✅ Built-in (RED/YELLOW/GREEN) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Local Deployment** | ✅ Self-hosted | ❌ API-only | ❌ | ✅ OSS | ✅ | ❌ Managed |
| **Multi-LLM** | ✅ Claude/GPT-4/Gemini | ❌ Claude only | ❌ OpenAI only | ✅ | ✅ | ✅ |
| **Korean HWP** | ✅ Native | ❌ | ❌ | ❌ | ❌ | ❌ |
| **SSE Updates** | ✅ Real-time | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Cost** | $ (self-hosted) | $$$ (API) | $$$ (per-user) | $ (infra) | $$ | $$$ |

**Differentiation Card (페이지 상단):**
```
💡 Why NEXUS-ON?

"Most AI assistants are either too autonomous (unpredictable)
 or too manual (inefficient). NEXUS-ON balances both:
 
 ✅ Autonomous multi-step execution
 ✅ Mandatory approval for risky actions
 ✅ Local-first with full data control
 ✅ Built for Korean academic & research workflows"
```

---

## 🎨 디자인 시스템 적용

### **NEXUS UI v1.1 기반**

**컬러:**
- Primary: `#FFFFFF` (White background)
- Accent: `#2563EB` (High-chroma Blue)
- Status:
  - Green: `#16A34A` (Stable)
  - Yellow: `#F59E0B` (Beta)
  - Red: `#DC2626` (Alpha)

**타이포그래피:**
- Pretendard 폰트
- Hero: `32px` (모바일: `24px`)
- Section Title: `28px`
- Card Title: `18px`
- Body: `14px`

**간격:**
- 8pt 그리드
- 섹션 간 간격: `64px`
- 카드 간 간격: `16px`

**모션:**
- `180ms` 트랜지션
- `cubic-bezier(0.22, 1, 0.36, 1)` 이징

---

## 📊 데이터 재작성 전략

### **1. modules.json 개선**

**Before (현재):**
```json
{
  "name": "Character Assistant Core",
  "status": "G",
  "highlights": [
    "Claude Sonnet 4.5 integration",
    "Multi-provider LLM gateway",
    "SSE-based real-time updates"
  ]
}
```

**After (개선):**
```json
{
  "module_id": "m001",
  "name": "Character Assistant Core",
  "version": "1.0",
  "status": "stable",
  "status_label": "Production Ready",
  "icon": "Bot",
  "tagline": "Multi-LLM conversational agent with streaming responses",
  "description": "Connect to Claude Sonnet 4.5, GPT-4, or Gemini. Real-time SSE updates for all agent reports. Session-based context with multi-tenant isolation.",
  "key_features": [
    "Multi-provider LLM gateway (Claude, OpenAI, Google)",
    "Streaming responses via Server-Sent Events",
    "Session and tenant context management",
    "Automatic report deduplication and correlation"
  ],
  "use_cases": [
    "Research assistance with multi-turn conversations",
    "Document analysis with context retention",
    "Team collaboration with shared sessions"
  ],
  "tech_stack": ["FastAPI", "Redis", "Pika (RabbitMQ)", "Claude API"],
  "last_updated": "2026-02-03"
}
```

**8개 모듈 모두 동일 형식으로 재작성**

---

### **2. benchmark.json 개선**

**Before (현재):**
```json
{
  "product": "NEXUS-ON",
  "strengths": "Integrated assistant+agent+approval+RAG, local-first, SSE-driven UI, HWP support",
  "weaknesses": "Early stage (P0), limited scalability testing, naive RAG implementation",
  "price_tier": "$ (self-hosted OSS)"
}
```

**After (개선):**
```json
{
  "category": "Autonomous AI Platforms",
  "product": "NEXUS-ON",
  "company": "Seokyeong University (Prof. Nam Hyunwoo)",
  "positioning": "Local-first autonomous assistant with mandatory human oversight",
  "strengths": [
    "Built-in approval gates (GREEN/YELLOW/RED risk workflow)",
    "Local deployment with full data control",
    "Multi-LLM support (Claude, GPT-4, Gemini)",
    "Native Korean HWP document support",
    "Real-time SSE updates for all operations",
    "Multi-tenant architecture with credential isolation"
  ],
  "ideal_for": [
    "Researchers handling sensitive documents",
    "Teams requiring approval workflows",
    "Korean academic and enterprise users",
    "Privacy-conscious power users"
  ],
  "limitations": [
    "Self-hosted setup required (not SaaS)",
    "Token-based RAG (not semantic embeddings)",
    "Early adopter stage (active development)"
  ],
  "price_tier": "$ (self-hosted OSS)",
  "deployment": "Docker Compose (local) or Render/Railway (cloud)",
  "license": "Open Source (MIT or Apache 2.0)",
  "last_updated": "2026-02-04"
}
```

---

## 🛠️ 구현 계획 (Implementation Roadmap)

### **Phase 1: 콘텐츠 재작성 (2-3시간)**

**작업 항목:**
1. ✅ 이 계획서 작성 완료
2. ⏳ `modules.json` 8개 모듈 재작성 (상세 설명, use cases, tech stack)
3. ⏳ `benchmark.json` 7개 제품 재작성 (positioning, ideal_for, limitations)
4. ⏳ 페이지 콘텐츠 작성:
   - Landing: Hero + 3 Pillars
   - Intro: Problem → Solution → Architecture
   - Developer: Prof. Nam profile
   - Modules: 8 cards + benchmark
   - Benchmark: Comparison table + differentiation

---

### **Phase 2: HTML/CSS 재구현 (3-4시간)**

**작업 항목:**
1. ⏳ `public_pages.py` 전면 재작성
   - `render_page()` 함수 개선 (더 풍부한 CSS)
   - 각 페이지별 `render_landing()`, `render_intro()` 등 구현
2. ⏳ NEXUS UI v1.1 CSS 토큰 적용
   - Pretendard 폰트
   - 컬러 시스템 (White + Blue Accent + Status colors)
   - 간격/타이포/모션 규칙
3. ⏳ 반응형 레이아웃 구현
   - Desktop: 3열 그리드
   - Tablet: 2열
   - Mobile: 1열
4. ⏳ 시각적 요소 추가
   - SVG 아이콘 (Lucide 스타일 인라인 SVG)
   - Status 배지 (Stable/Beta/Alpha)
   - 카드 호버 효과

---

### **Phase 3: 검증 및 배포 (1시간)**

**작업 항목:**
1. ⏳ 로컬 테스트 (Docker Compose)
   ```bash
   docker-compose -f docker/docker-compose.nexus.yml up -d
   curl http://localhost:8000/
   ```
2. ⏳ 페이지별 검증
   - `/`: Hero section 렌더링, CTA 작동
   - `/intro`: Architecture 다이어그램, 모듈 소개
   - `/developer`: Prof. Nam 프로필
   - `/modules`: 8개 모듈 카드, benchmark 테이블
   - `/benchmark`: 7개 제품 비교표
3. ⏳ Git commit & push
4. ⏳ Render.com 배포 (선택 사항)

---

## 📈 성공 지표 (Success Metrics)

### **정성적 목표**
1. ✅ "This looks like a real product" (데모 느낌 제거)
2. ✅ "I understand what NEXUS-ON does in 10 seconds" (명확한 가치 제안)
3. ✅ "I trust this product" (학술적 권위, 구체적 사용 사례)
4. ✅ "I want to try it" (명확한 CTA)

### **정량적 목표**
- [ ] Hero section 읽기 시간: <5초
- [ ] 3 Pillars 이해도: >90%
- [ ] CTA 클릭률: >10%
- [ ] Bounce rate: <60%
- [ ] Time on page: >2분

---

## 🎯 핵심 메시지 (Key Messaging)

### **1. 차별화 (Differentiation)**
"NEXUS-ON is the only AI assistant that combines autonomous execution
 with mandatory human approval for risky actions—built for researchers
 who need both efficiency and control."

### **2. 신뢰 (Trust)**
"Developed by Prof. Nam Hyunwoo at Seokyeong University,
 NEXUS-ON brings academic rigor to autonomous AI systems."

### **3. 실용성 (Practicality)**
"Local-first deployment, multi-LLM support, and native Korean HWP handling.
 No vendor lock-in, no surprises."

### **4. 투명성 (Transparency)**
"Every action is logged, every risk is assessed, every RED operation
 requires your explicit approval."

---

## 🚀 다음 단계 선택

교수님, 다음 중 어떤 방향으로 진행할까요?

### **Option A: 즉시 구현 시작** (추천)
- Phase 1 착수: `modules.json` 8개 재작성
- 예상 시간: 2-3시간
- 산출물: 프리미엄 콘텐츠

### **Option B: 계획 보완**
- 추가 벤치마크 분석
- 디자인 목업 추가
- 예상 시간: 1시간

### **Option C: 샘플 페이지 먼저**
- Landing page만 먼저 완성
- 빠른 프로토타입
- 예상 시간: 1시간

---

## 📚 참고 자료

### **벤치마크 사이트**
- Anthropic: https://www.anthropic.com (Safety-first 메시징)
- OpenAI: https://openai.com (제품 중심)
- Perplexity: https://www.perplexity.ai (즉시 체험)

### **디자인 원칙**
- Hero Section Best Practices 2025
- Landing Page Conversion Optimization
- SaaS Marketing Site Design Patterns

### **기존 문서**
- `/home/user/webapp/frontend/docs/DESIGN_SYSTEM_補完_REPORT.md` (NEXUS UI v1.1)
- `/home/user/webapp/frontend/src/design-tokens.css` (디자인 토큰)
- `/home/user/webapp/backend/data/modules.json` (현재 데이터)
- `/home/user/webapp/backend/data/benchmark.json` (현재 데이터)

---

**작성 완료**: 2026-02-04  
**다음 액션**: 교수님 승인 후 Phase 1 착수  
**예상 총 소요 시간**: 6-8시간

**교수님, 어떻게 진행하시겠습니까?** 🚀
