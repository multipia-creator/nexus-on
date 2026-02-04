# NEXUS-ON UI 현황 보고서

**보고 일시**: 2026-02-04  
**보고 대상**: 남현우 교수님  
**작성자**: AI Staff Engineer

---

## **Executive Summary**

NEXUS-ON은 현재 **이중 UI 아키텍처**로 구성되어 있습니다:
1. **백엔드 내장 마케팅 사이트** (FastAPI 서버 렌더링) - 새로 추가됨 ✅
2. **프론트엔드 React 앱** (Cloudflare Pages 배포) - 기존 유지 중

두 UI는 독립적으로 작동하며, 각각 다른 목적과 배포 환경을 가지고 있습니다.

---

## **1. 백엔드 내장 마케팅 사이트** (신규 구현)

### **현황**
- **구현 방식**: FastAPI가 HTML을 직접 반환 (Server-Side Rendering)
- **배포 위치**: Backend와 함께 배포 (Docker Compose)
- **접근 URL**: `http://localhost:8000/` (백엔드 서버)
- **상태**: ✅ **완전 구현 완료** (2026-02-04)

### **페이지 구성**
| 경로 | 설명 | 상태 |
|------|------|------|
| `GET /` | 랜딩 페이지 (제품 소개 + CTA) | ✅ 완료 |
| `GET /intro` | 소개 페이지 (목적 + 가치 + 아키텍처 + 개발자) | ✅ 완료 |
| `GET /developer` | 개발자 상세 소개 | ✅ 완료 |
| `GET /modules` | 모듈 현황 + 벤치마크 비교 | ✅ 완료 |
| `GET /benchmark` | 제품 비교표 | ✅ 완료 |
| `GET /app` | 기존 작업 UI (채팅/YouTube/RAG/Canvas) | ✅ 완료 |

### **API 엔드포인트**
| 경로 | 응답 | 용도 |
|------|------|------|
| `GET /api/public/modules` | JSON (8 modules) | 실시간 업데이트 준비 |
| `GET /api/public/benchmark` | JSON (8 products) | 실시간 업데이트 준비 |

### **데이터 소스**
- `/backend/data/modules.json` (2.1 KB, 8개 항목)
- `/backend/data/benchmark.json` (3.2 KB, 8개 항목)
- 데이터 로딩 함수 분리됨 → 향후 DB 전환 용이

### **디자인 시스템**
- **색상**: White 기반 (#FFFFFF), 텍스트 계층 (#111111, #3C3C43, #6B6B73)
- **타이포**: System UI 폰트 + Pretendard (한글 지원)
- **컴포넌트**: 카드, 배지, 버튼, 테이블
- **반응형**: 768px 브레이크포인트
- **파일**: `/backend/nexus_supervisor/public_pages.py` (7.4 KB)

### **특징**
✅ 프레임워크 의존성 없음 (순수 HTML/CSS)  
✅ 공유 템플릿 시스템 (`render_page()`)  
✅ 네비게이션 자동 활성화  
✅ CLAUDE.md 불변 규칙 준수 (SSE/202/Approvals)

---

## **2. 프론트엔드 React 앱** (기존)

### **현황**
- **구현 방식**: React 18 + TypeScript + Vite
- **배포 위치**: Cloudflare Pages
- **접근 URL**: `https://webapp-zrq.pages.dev/`
- **상태**: ✅ **배포 완료** (2026-02-03)

### **기술 스택**
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.5.4",
    "vite": "^5.4.1"
  }
}
```

### **컴포넌트 구조**
```
frontend/src/
├── shell/
│   ├── Shell.tsx                    # 메인 컨테이너 (view 상태 관리)
│   └── components/
│       ├── AssistantStage.tsx       # 채팅 인터페이스
│       ├── Dashboard.tsx            # 대시보드 뷰
│       ├── Dock.tsx                 # 하단 독 UI
│       └── Sidecar.tsx              # 사이드바
├── nodes/
│   ├── NodesManager.tsx             # Windows Node 관리
│   └── types.ts
├── youtube/
│   ├── YouTubePanel.tsx             # YouTube 검색/큐/플레이어
│   └── types.ts
├── devices/
│   ├── DeviceBadge.tsx              # 디바이스 배지
│   ├── DevicesModal.tsx             # 디바이스 모달
│   └── api.ts                        # API 유틸리티
├── lib/
│   ├── correlation.ts               # Correlation ID
│   ├── http.ts                      # HTTP 유틸리티
│   ├── mockData.ts                  # 데모 모드 데이터
│   └── useFocusTrap.ts              # 포커스 트랩 훅 (신규)
├── stream/
│   └── useAgentReportStream.ts     # SSE 스트림 훅
├── main.tsx                         # 엔트리 포인트
└── types.ts                         # 공통 타입
```

### **뷰 구성**
| 뷰 | 컴포넌트 | 설명 |
|-------|----------|------|
| `stage` | `AssistantStage` | 캐릭터 비서 채팅 UI |
| `dashboard` | `Dashboard` + `Sidecar` | 대시보드 + 사이드바 |
| `youtube` | `YouTubePanel` | YouTube 검색/재생 |

### **스타일 파일**
| 파일 | 라인 수 | 용도 |
|------|---------|------|
| `styles.css` | 168 | 기존 다크 테마 스타일 |
| `design-tokens.css` | 209 | NEXUS UI v1.1 디자인 토큰 |
| `styles-v1.1.css` | 677 | NEXUS UI v1.1 전면 개선 스타일 |
| **합계** | **1,054** | |

### **빌드 산출물**
```
dist/
├── index.html              # 402 bytes
└── assets/
    ├── index-DE36my5s.js   # 173.96 KB (gzip: 55.73 KB)
    └── index-DSHWWh2X.css  # 11.68 KB (gzip: 2.64 KB)
```

### **주요 기능**
✅ SSE 기반 실시간 업데이트 (`useAgentReportStream`)  
✅ Demo 모드 지원 (`isDemoMode()`, mock data)  
✅ 채팅 인터페이스 (`/chat` API 연동)  
✅ YouTube 검색/큐/임베드 플레이어  
✅ Nodes 관리 (페어링, 명령, 상태)  
✅ Dock UI (뷰 전환, 상태 표시)

### **배포 상태**
- **Cloudflare Project**: `webapp` (not `nexus-frontend`)
- **Production URL**: https://webapp-zrq.pages.dev/
- **Branch URL**: https://main.webapp-zrq.pages.dev/
- **Last Deploy**: 2026-02-03 16:23:24 UTC
- **Status**: ✅ HTTP 200 (정상)

---

## **3. UI 아키텍처 비교**

| 측면 | 백엔드 마케팅 사이트 | 프론트엔드 React 앱 |
|------|---------------------|-------------------|
| **목적** | 제품 소개, 개발자 정보, 모듈 현황 | 실제 작업 UI (채팅, YouTube, RAG) |
| **사용자** | 방문자, 잠재 고객 | 실제 사용자 |
| **렌더링** | Server-Side (FastAPI) | Client-Side (React) |
| **배포** | Docker Compose (Backend와 함께) | Cloudflare Pages (독립) |
| **URL** | `http://localhost:8000/` | `https://webapp-zrq.pages.dev/` |
| **데이터** | JSON 파일 (`modules.json`, `benchmark.json`) | SSE 스트림 + API 호출 |
| **스타일** | 인라인 CSS (7.4 KB) | CSS 파일 (1,054 lines) |
| **프레임워크** | 없음 (순수 HTML) | React 18 + TypeScript |
| **상태 관리** | 없음 (정적 페이지) | React State + SSE |
| **빌드** | 없음 | Vite (173.96 KB JS) |
| **인증** | 불필요 (public pages) | API Key 필요 (`/app` 영역) |

---

## **4. 디자인 시스템 현황**

### **NEXUS UI v1.1 (준비됨, 미적용)**
- **디자인 토큰**: `/frontend/src/design-tokens.css` (209 lines)
  - Icon System (xs/sm/md/lg/xl)
  - Live2D Character (280x320px, glow 효과)
  - 컬러 시스템 (White + High-Chroma Blue)
  - 타이포그래피 (Pretendard, 5단계)
  - 간격 (8pt 그리드)
  - 모션 (micro/ui/modal)

- **전면 개선 스타일**: `/frontend/src/styles-v1.1.css` (677 lines)
  - TopNav 컴포넌트
  - Stage 3카드 레이아웃
  - Dashboard 3컬럼
  - Sidecar 3섹션
  - Dock 상태 표시
  - 접근성 (WCAG AA)
  - 반응형 (모바일/태블릿/데스크탑)

- **유틸리티**: `/frontend/src/lib/useFocusTrap.ts`
  - Focus trap 구현 (WCAG 2.1 AA)
  - Tab/Shift+Tab 순환
  - ESC 키 닫기
  - 포커스 복원

### **적용 상태**
⚠️ **미적용**: 디자인 토큰과 v1.1 스타일은 파일로 존재하지만 `main.tsx`에서 import되지 않음

**현재 사용 중**: `styles.css` (168 lines, 다크 테마)

---

## **5. 통합 시나리오 분석**

### **시나리오 A: 현재 상태 유지**
- 백엔드 마케팅 사이트: `http://localhost:8000/` (제품 소개)
- 프론트엔드 React 앱: `https://webapp-zrq.pages.dev/` (작업 UI)
- **문제**: URL이 분리되어 사용자 혼란 가능

### **시나리오 B: 백엔드에서 프론트엔드로 리다이렉트**
```python
@app.get("/")
def root_redirect():
    return RedirectResponse(url="https://webapp-zrq.pages.dev/")
```
- 백엔드 `/`에서 자동으로 Cloudflare Pages로 이동
- **문제**: 마케팅 페이지가 사라짐

### **시나리오 C: 프론트엔드에 마케팅 페이지 통합**
- React 앱에 `/`, `/intro`, `/developer` 등 추가
- NEXUS UI v1.1 디자인 시스템 적용
- **문제**: 추가 개발 시간 필요

### **권장 사항**: **시나리오 A (현재 상태)**
- 백엔드 마케팅 사이트는 **제품 소개** 목적
- 프론트엔드 앱은 **실제 사용** 목적
- `/app` 링크로 자연스럽게 연결
- 향후 단일 도메인으로 통합 가능

---

## **6. 개선 제안 (우선순위)**

### **P0 (즉시)**
1. ✅ **백엔드 마케팅 사이트 완료** (완료됨)
2. ⏳ **프론트엔드 v1.1 디자인 적용** (토큰 파일 존재, 미적용)
3. ⏳ **프론트엔드 빌드 + 재배포**

### **P1 (1주 내)**
1. 프론트엔드에 TopNav 추가 (Home / Intro / Developer 등)
2. NEXUS UI v1.1 스타일 import
3. Live2D 캐릭터 통합
4. 아이콘 라이브러리 설치 (Lucide React)

### **P2 (1개월 내)**
1. 프론트엔드에 마케팅 페이지 React 컴포넌트 추가
2. SSE 스트림으로 모듈/벤치마크 실시간 업데이트
3. 단일 도메인 통합 (리버스 프록시)
4. A/B 테스트, 애널리틱스

---

## **7. 배포 URL 요약**

| 서비스 | URL | 상태 |
|--------|-----|------|
| **백엔드 마케팅** | http://localhost:8000/ | ✅ Local (Docker) |
| **백엔드 마케팅** | (배포 필요) | ⏳ Not deployed |
| **프론트엔드 앱** | https://webapp-zrq.pages.dev/ | ✅ Deployed (Cloudflare) |
| **GitHub** | https://github.com/multipia-creator/nexus-on | ✅ Pushed |

---

## **8. 파일 통계**

### **프론트엔드**
```
TypeScript 파일: 19개
  - Components: 10개
  - Utilities: 6개
  - Types: 3개

CSS 파일: 3개 (총 1,054 lines)
  - styles.css: 168 lines (현재 사용 중)
  - design-tokens.css: 209 lines (준비됨)
  - styles-v1.1.css: 677 lines (준비됨)

빌드 산출물:
  - JS: 173.96 KB (gzip: 55.73 KB)
  - CSS: 11.68 KB (gzip: 2.64 KB)
  - HTML: 402 bytes
```

### **백엔드**
```
마케팅 사이트: 
  - public_pages.py: 7.4 KB (템플릿 + 로더)
  - app.py: +312 lines (6개 페이지 + 2개 API)

데이터:
  - modules.json: 2.1 KB (8개 항목)
  - benchmark.json: 3.2 KB (8개 항목)

문서:
  - MARKETING_SITE_IMPLEMENTATION.md: 9.9 KB
```

---

## **9. 다음 액션 아이템**

### **교수님 결정 필요**
1. ❓ 프론트엔드 v1.1 디자인 시스템 적용 여부
2. ❓ 백엔드 마케팅 사이트 별도 배포 필요 여부
3. ❓ 두 UI 통합 전략 선택 (A/B/C)

### **즉시 실행 가능**
- 프론트엔드 v1.1 스타일 적용
- Lucide React 아이콘 설치
- TopNav 컴포넌트 구현
- 프론트엔드 재빌드 + 재배포

---

## **10. 결론**

NEXUS-ON은 현재 **이중 UI 아키텍처**를 가지고 있습니다:

✅ **백엔드 마케팅 사이트**: 제품 소개, 개발자 정보, 모듈 현황 (완전 구현 완료)  
✅ **프론트엔드 React 앱**: 실제 작업 UI (채팅, YouTube, RAG, Nodes) (배포 완료)

두 시스템은 독립적으로 작동하며, 각각의 목적에 최적화되어 있습니다.

**즉시 개선 가능 항목**:
1. 프론트엔드에 NEXUS UI v1.1 디자인 적용
2. 백엔드 마케팅 사이트 프로덕션 배포

**교수님, 어떤 방향으로 진행할까요?** 🚀
