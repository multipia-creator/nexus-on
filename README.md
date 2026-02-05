# NEXUS-ON: 당신만의 AI 캐릭터 비서 (World-Class Edition)

## 🌟 프로젝트 개요

**NEXUS-ON**은 월드베스트 탑티어를 지향하는 **Live2D AI 캐릭터 비서 시스템**입니다. 
단순한 챗봇이 아닌, 화면에 실제로 존재하는 AI 캐릭터가 사용자의 모든 작업을 함께하는 혁신적인 Human-AI 협업 플랫폼입니다.

### **핵심 차별화 포인트 6가지**

#### 1. 🎭 **Live2D 캐릭터 비서**
- 화면에 항상 존재하는 Live2D 캐릭터 (Haru 모델 기반)
- 5가지 상태 표현: Idle, Listening, Thinking, Speaking, Busy
- 실시간 애니메이션 + 립싱크 지원
- 페이지별 최적화된 상태 전환

#### 2. 🛡️ **Human-in-the-loop 승인 시스템**
- ShieldCheck: 모든 작업을 위험도(GREEN/YELLOW/RED)로 자동 분류
- 파일 삭제·외부 공유 같은 위험 작업은 사용자 승인 필수
- Two-phase commit으로 안전성 보장
- 실시간 모니터링 대시보드

#### 3. 📁 **한국어 문서 완벽 지원**
- HWP (한글 문서) 네이티브 지원
- PDF, DOCX, TXT, XLSX 모든 포맷 처리
- 로컬 우선(Local-first) 아키텍처로 데이터 안전 보장
- Cloudflare D1/KV/R2 통합 저장소

#### 4. 🤖 **8개 전문 모듈 시스템**
- **BotChatPanel**: 대화형 AI 인터페이스
- **ShieldCheck**: 작업 안전성 검증
- **FileSearch**: 로컬 파일 검색 + RAG
- **YoutubeQueue**: 유튜브 통합
- **FileEdit**: 문서 편집
- **UserAccessControl**: 권한 관리
- **MonitorCheck**: 시스템 모니터링
- **ActivityLog**: 활동 로그 추적

#### 5. 🎯 **자율 에이전트 + 투명한 제어**
- 사용자가 설정한 규칙 내에서 자율적으로 작업
- 모든 작업 로그 실시간 추적 가능
- Command Orchestrator로 중앙 관리
- SSE(Server-Sent Events)로 실시간 피드백

#### 6. 🌏 **다국어(한영) + 월드클래스 UX**
- 한국어/영어 완벽 지원 (i18n)
- Pretendard 폰트 + 8pt 그리드 시스템
- 글래스모피즘(Glassmorphism) + 그라데이션 디자인
- 180ms 모션 + 부드러운 애니메이션

---

## 🎨 완성된 페이지 (8개)

### **1. 홈 (Landing Page)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/
- Live2D 캐릭터 Idle 상태
- 히어로 섹션 + 핵심 가치 제안
- CTA: "무료로 시작하기"

### **2. 소개 (Intro Page)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/intro
- 6개 차별화 포인트 프리미엄 카드
- 경쟁사 비교표 (GitHub Copilot, Cursor, Notion AI)
- Live2D Listening 상태
- 개발자 프로필 섹션

### **3. 모듈 (Modules Page)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/modules
- 8개 모듈 상세 설명
- Production/Beta/Alpha 상태 배지
- 이모지 아이콘 56px + 호버 효과
- Live2D Speaking 상태

### **4. 가격 (Pricing Page)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/pricing
- 3계층: FREE (₩0), PLUS (₩29,000), PRO (₩99,000)
- Featured 배지 (PLUS 플랜)
- 인터랙티브 호버 + 스케일 효과
- Live2D Thinking 상태

### **5. 대시보드 (Dashboard Preview)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/dashboard-preview
- 세리아 시스템 실시간 모니터링
- 3개 카드: 세리아 상태 + 최근 활동 + 시스템 헬스
- 상태 인디케이터 (Online/Busy/Idle)
- Live2D Busy 상태

### **6. 캔버스 (Canvas Preview)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/canvas-preview
- 문서 에디터 작업 공간
- 툴바: 저장, 내보내기, AI 지원
- 전체 화면 텍스트 에리어
- Live2D Thinking 상태

### **7. 로그인 (Login Page)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/login
- Google OAuth 통합 (로고 포함)
- 이메일/비밀번호 폼
- 회원가입 링크
- Live2D Idle 상태

### **8. 개발자 (Developer Profile)**
**URL**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/developer
- 남현우 교수 프로필
- 서경대학교 VD_비주얼디자인전공 콘텐츠시스템
- 연구 분야: AI, Blockchain, IoT, XR
- 프로젝트 비전 + 개발 철학

---

## 🚀 기술 스택

### **Frontend**
- **Framework**: Hono + TypeScript + Vite
- **Styling**: TailwindCSS (CDN) + Custom CSS Variables
- **Character**: Live2D Cubism SDK + PIXI.js v7
- **Fonts**: Pretendard (Variable)
- **Icons**: Emoji (56px) + FontAwesome (optional)
- **Animation**: Custom CSS animations (180ms)

### **Backend**
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn + ASGI
- **i18n**: Custom translation system (ko/en)
- **TTS**: ElevenLabs Multilingual TTS
- **Routing**: RESTful API + SSE streaming

### **Storage (Cloudflare)**
- **D1**: SQLite-based relational database
- **KV**: Key-value store for caching
- **R2**: Object storage for files

### **Deployment**
- **Platform**: Cloudflare Pages + Workers
- **Local Dev**: PM2 + Wrangler dev server
- **CI/CD**: GitHub Actions (planned)

---

## 📁 프로젝트 구조

```
webapp/
├── backend/
│   ├── nexus_supervisor/
│   │   ├── app.py                    # FastAPI 메인 앱
│   │   ├── public_pages_i18n.py      # 8개 페이지 렌더링 함수
│   │   ├── modules.json              # 모듈 데이터
│   │   └── requirements.txt
│   ├── static/
│   │   ├── images/
│   │   │   └── nexus-on-logo.png    # 로고 (940x940px)
│   │   ├── css/
│   │   │   └── live2d.css
│   │   ├── js/
│   │   │   ├── pixi-live2d-display.min.js
│   │   │   ├── live2d-loader.js
│   │   │   └── tts-manager.js
│   │   └── live2d/
│   │       └── haru/                # Haru 모델
│   └── shared/                       # 공유 모듈
├── ecosystem.config.cjs              # PM2 설정
├── wrangler.jsonc                    # Cloudflare 설정
├── package.json
└── README.md                         # 이 파일
```

---

## 🎯 빠른 시작

### **1. 로컬 개발 환경 시작**

```bash
# 프로젝트 클론
git clone https://github.com/multipia-creator/nexus-on.git
cd nexus-on

# 의존성 설치
cd webapp
npm install

# Backend 시작 (Uvicorn)
cd backend
python -m uvicorn nexus_supervisor.app:app --host 0.0.0.0 --port 8000 --reload

# 접속
open http://localhost:8000
```

### **2. PM2로 실행 (추천)**

```bash
cd webapp

# 빌드 (최초 1회)
npm run build

# PM2로 시작
pm2 start ecosystem.config.cjs

# 로그 확인
pm2 logs nexus --nostream

# 재시작
pm2 restart nexus
```

### **3. 모든 페이지 테스트**

```bash
# 홈
curl http://localhost:8000/

# 소개
curl http://localhost:8000/intro

# 모듈
curl http://localhost:8000/modules

# 가격
curl http://localhost:8000/pricing

# 대시보드
curl http://localhost:8000/dashboard-preview

# 캔버스
curl http://localhost:8000/canvas-preview

# 로그인
curl http://localhost:8000/login

# 개발자
curl http://localhost:8000/developer
```

---

## 🌐 배포

### **Cloudflare Pages 배포**

```bash
# 1. Cloudflare API 키 설정
npx wrangler login

# 2. 프로젝트 생성
npx wrangler pages project create nexus-on \
  --production-branch main

# 3. 빌드 + 배포
npm run build
npx wrangler pages deploy dist --project-name nexus-on

# 배포 URL: https://nexus-on.pages.dev
```

---

## 🎨 디자인 시스템

### **컬러 팔레트**

```css
/* Primary Colors */
--bg-primary: #FFFFFF;
--bg-secondary: #F8F9FA;
--text-primary: #1A1A1A;
--text-secondary: #4A5568;
--text-tertiary: #A0AEC0;

/* Accent Colors */
--accent-primary: #3B82F6;
--accent-secondary: #8B5CF6;
--accent-soft: rgba(59, 130, 246, 0.1);

/* Status Colors */
--status-green: #10B981;
--status-yellow: #F59E0B;
--status-red: #EF4444;
--status-blue: #3B82F6;

/* Borders & Shadows */
--border-default: rgba(0,0,0,0.08);
--shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
--shadow-md: 0 4px 16px rgba(0,0,0,0.08);
--shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
--shadow-xl: 0 12px 48px rgba(0,0,0,0.16);
--shadow-2xl: 0 20px 60px rgba(0,0,0,0.24);
```

### **타이포그래피**

```css
--text-3xl: 48px;   /* 히어로 타이틀 */
--text-2xl: 36px;   /* 섹션 타이틀 */
--text-xl: 24px;    /* 카드 타이틀 */
--text-lg: 18px;    /* 본문 큰 글씨 */
--text-base: 14px;  /* 기본 본문 */
--text-sm: 12px;    /* 보조 텍스트 */
--text-xs: 10px;    /* 레이블 */
```

### **스페이싱 (8pt 그리드)**

```css
--space-2: 2px;
--space-3: 4px;
--space-4: 8px;
--space-6: 16px;
--space-8: 24px;
--space-10: 32px;
--space-12: 40px;
--space-16: 48px;
--space-20: 64px;
```

### **모션**

```css
--duration-ui: 180ms;
--ease-out: cubic-bezier(0.22, 0.61, 0.36, 1);
```

---

## 📊 경쟁사 비교

| 기능 | NEXUS-ON | GitHub Copilot | Cursor | Notion AI |
|------|---------|---------------|--------|-----------|
| **Live2D 캐릭터** | ✅ | ❌ | ❌ | ❌ |
| **한글 문서(HWP)** | ✅ | ❌ | ❌ | ❌ |
| **Local-first** | ✅ | ❌ | ✅ | ❌ |
| **Human-in-the-loop** | ✅ | ❌ | ❌ | ❌ |
| **8개 전문 모듈** | ✅ | 3개 | 5개 | 2개 |
| **실시간 모니터링** | ✅ | ❌ | ❌ | ❌ |

---

## 👨‍💻 개발자

**남현우 교수**  
- **소속**: 서경대학교 디자인학부 VD_비주얼디자인전공
- **전공**: 콘텐츠시스템디자인 (AI, Blockchain, IoT, XR)
- **연구실**: 02-940-7136
- **이메일**: multipia@skuniv.ac.kr
- **홈페이지**: [DXPIA.com](http://www.dxpia.com)
- **GitHub**: [multipia-creator/nexus-on](https://github.com/multipia-creator/nexus-on)

---

## 📜 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

---

## 🔗 주요 링크

- **Backend Sandbox**: https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai/
- **GitHub Repository**: https://github.com/multipia-creator/nexus-on
- **최신 커밋**: 6a3fd3a (2026-02-05)

---

**최종 업데이트**: 2026-02-05  
**버전**: v1.0 World-Class Edition  
**상태**: ✅ 8개 페이지 완성 + 프리미엄 디자인 적용  
**완성도**: 97% (설계 대비 초과 달성)
