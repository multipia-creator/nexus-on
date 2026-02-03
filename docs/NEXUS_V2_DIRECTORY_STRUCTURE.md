# NEXUS v2 디렉토리 구조 요약

**프로젝트**: NEXUS 세리아 AI 에이전트 시스템 v2.0  
**생성일**: 2026-02-03  
**분석 기준**: Frontend(React) 중심 웹앱 실행 가능 상태

---

## 📁 전체 디렉토리 트리

```
/home/user/webapp/
├── frontend/                      # React Frontend (393 lines)
│   ├── src/
│   │   ├── main.tsx               # 엔트리 포인트 (10 lines)
│   │   ├── types.ts               # TypeScript 타입 정의
│   │   ├── styles.css             # 글로벌 스타일
│   │   ├── lib/                   # 유틸리티
│   │   │   ├── http.ts            # HTTP 클라이언트
│   │   │   └── correlation.ts    # Correlation ID 생성
│   │   ├── stream/                # SSE 스트림
│   │   │   └── useAgentReportStream.ts  # SSE 커스텀 훅
│   │   ├── shell/                 # Shell 컴포넌트
│   │   │   ├── Shell.tsx          # 메인 Shell
│   │   │   └── components/
│   │   │       ├── Dock.tsx       # 하단 Dock
│   │   │       ├── AssistantStage.tsx  # 메인 스테이지
│   │   │       ├── Dashboard.tsx  # 대시보드
│   │   │       └── Sidecar.tsx    # 사이드카
│   │   └── devices/               # Devices 관리
│   │       ├── api.ts             # Device API 클라이언트
│   │       ├── DeviceBadge.tsx    # Device 상태 Badge
│   │       └── DevicesModal.tsx   # Devices Modal
│   ├── index.html                 # HTML 엔트리
│   ├── package.json               # 의존성 정의
│   ├── tsconfig.json              # TypeScript 설정
│   ├── vite.config.ts             # Vite 설정 (프록시 포함)
│   ├── .env.local.example         # 환경 변수 예시
│   └── README.md                  # Frontend README
│
├── backend/                       # FastAPI Backend (625 lines)
│   ├── app/
│   │   ├── __init__.py            # 패키지 초기화
│   │   ├── main.py                # 메인 애플리케이션 (217 lines)
│   │   ├── models.py              # Pydantic 모델 정의
│   │   ├── store.py               # In-memory 데이터 스토어
│   │   └── sse.py                 # SSE Broadcaster
│   ├── requirements.txt           # Python 의존성
│   └── README.md                  # Backend README
│
├── windows_companion/             # Windows Companion
│   ├── companion.py               # 메인 Companion 스크립트
│   ├── requirements.txt           # Python 의존성
│   ├── config.example.json        # 설정 예시
│   └── RUN_WINDOWS.cmd            # Windows 실행 스크립트
│
├── scripts/                       # 실행 스크립트
│   ├── START_BACKEND_WIN.cmd      # Backend 실행 (Windows)
│   └── START_FRONTEND_WIN.cmd     # Frontend 실행 (Windows)
│
├── docs/                          # 문서 디렉토리
│   ├── API_KEYS.md                # API 키 관리
│   ├── API_SETUP_COMPLETE.md      # API 설정 완료
│   ├── NEXUS_WORK_CONTEXT.md      # 작업 컨텍스트
│   ├── NEXUS_EXECUTION_CHECKLIST.md  # 실행 체크리스트
│   ├── NEXUS_SMOKE_TEST_SCENARIOS.md  # 스모크 테스트
│   ├── NEXUS_ERROR_FIXES.md       # 오류 수정 가이드
│   ├── NEXUS_IMPLEMENTATION_INSTRUCTIONS.md  # 구현 지시서
│   ├── NEXUS_V2_SETUP_CHECKLIST.md  # v2 실행 준비 체크리스트
│   ├── PROJECT_CONFIG.md          # 프로젝트 설정
│   ├── README.md                  # 문서 인덱스
│   ├── api/                       # API 문서 (빈 디렉토리)
│   ├── architecture/              # 아키텍처 문서 (빈 디렉토리)
│   └── python/                    # Python 문서 (빈 디렉토리)
│
├── src/                           # ⚠️ Legacy Hono 코드 (제거 예정)
│   ├── index.tsx                  # Legacy 엔트리
│   ├── types.ts                   # Legacy 타입
│   └── renderer.tsx               # Legacy 렌더러
│
├── public/                        # 정적 파일
│   └── static/
│       └── style.css              # 정적 CSS
│
├── dist/                          # ⚠️ Legacy 빌드 출력 (제거 예정)
│
├── node_modules/                  # ⚠️ Legacy npm 패키지 (정리 필요)
│
├── .git/                          # Git 저장소
├── .gitignore                     # Git 무시 파일
├── .wrangler/                     # ⚠️ Cloudflare Wrangler 캐시 (미사용)
├── .dev.vars                      # 개발 환경 변수 (Cloudflare)
├── .dev.vars.example              # 개발 환경 변수 예시
├── .env.example                   # 환경 변수 예시
├── README.md                      # ✅ 메인 README (v2 기준 재작성)
├── MANIFEST.sha256                # 파일 체크섬
├── package.json                   # ⚠️ Legacy npm 설정 (정리 필요)
├── package-lock.json              # ⚠️ Legacy npm 잠금 파일
├── tsconfig.json                  # ⚠️ Legacy TypeScript 설정
├── vite.config.ts                 # ⚠️ Legacy Vite 설정
├── ecosystem.config.cjs           # ⚠️ PM2 설정 (미사용)
└── wrangler.jsonc                 # ⚠️ Cloudflare 설정 (미사용)
```

---

## 📊 코드 통계

### **Frontend (React + TypeScript)**
| 파일 | 라인 수 | 설명 |
|------|---------|------|
| `main.tsx` | 10 | 엔트리 포인트 |
| `types.ts` | ~50 | TypeScript 타입 정의 |
| `lib/http.ts` | ~30 | HTTP 클라이언트 |
| `lib/correlation.ts` | ~15 | Correlation ID 생성 |
| `stream/useAgentReportStream.ts` | ~80 | SSE 커스텀 훅 |
| `shell/Shell.tsx` | ~50 | 메인 Shell |
| `shell/components/*.tsx` | ~120 | Dock, AssistantStage, Dashboard, Sidecar |
| `devices/*.tsx` | ~38 | Devices Modal, Badge, API |
| **합계** | **393 lines** | React 컴포넌트 + 훅 |

### **Backend (FastAPI + Python)**
| 파일 | 라인 수 | 설명 |
|------|---------|------|
| `main.py` | 217 | 메인 애플리케이션 (SSE + Device API) |
| `models.py` | ~150 | Pydantic 모델 |
| `store.py` | ~200 | In-memory 데이터 스토어 |
| `sse.py` | ~58 | SSE Broadcaster |
| **합계** | **625 lines** | FastAPI 백엔드 |

### **Windows Companion (Python)**
| 파일 | 라인 수 | 설명 |
|------|---------|------|
| `companion.py` | ~150 | Windows Companion 메인 스크립트 |
| **합계** | **~150 lines** | Windows 디바이스 에이전트 |

### **문서 (Markdown)**
| 디렉토리 | 파일 수 | 총 라인 수 |
|----------|---------|------------|
| `docs/` | 12개 | ~3,053 lines |
| `frontend/README.md` | 1개 | ~22 lines |
| `backend/README.md` | 1개 | ~33 lines |
| `README.md` (루트) | 1개 | ~340 lines |
| **합계** | **15개** | **~3,448 lines** |

---

## 🔑 핵심 파일 설명

### **Frontend 핵심 파일**

#### `frontend/src/main.tsx` (엔트리 포인트)
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Shell } from './shell/Shell'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Shell />
  </React.StrictMode>
)
```
- React 애플리케이션의 진입점
- `Shell` 컴포넌트를 렌더링

#### `frontend/src/stream/useAgentReportStream.ts` (SSE 훅)
- **역할**: `/agent/reports/stream` SSE 구독
- **기능**:
  - `Last-Event-ID` 헤더로 재연결 시 이벤트 재생
  - `snapshot`, `report`, `ping` 이벤트 처리
  - `localStorage`에 cursor 저장
- **계약 준수**: SSE 단일 소스 (UI 상태는 SSE만 구독)

#### `frontend/src/shell/Shell.tsx` (메인 Shell)
- **역할**: 전체 UI 레이아웃
- **구성**:
  - `AssistantStage` (메인 스테이지)
  - `Dashboard` (대시보드)
  - `Sidecar` (사이드카)
  - `Dock` (하단 버튼)

#### `frontend/src/devices/DevicesModal.tsx` (Devices Modal)
- **역할**: Device Pairing UI
- **기능**:
  - Pairing Code 입력
  - `/devices/pairing/confirm_by_code` 호출
  - Device 목록 표시

#### `frontend/vite.config.ts` (Vite 설정)
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/agent': 'http://localhost:8000',
      '/sidecar': 'http://localhost:8000',
      '/approvals': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    }
  }
})
```
- **프록시 설정**: `/agent/*`, `/sidecar/*` 등을 Backend로 프록시
- **개발 환경**: CORS 문제 해결

---

### **Backend 핵심 파일**

#### `backend/app/main.py` (메인 애플리케이션)
- **역할**: FastAPI 애플리케이션 정의
- **주요 엔드포인트**:
  - `GET /agent/reports/stream` (SSE 스트림)
  - `POST /devices/pairing/start` (페어링 시작)
  - `POST /devices/pairing/confirm_by_code` (페어링 확인)
  - `POST /devices/pairing/complete` (페어링 완료)
  - `POST /devices/{device_id}/heartbeat` (Heartbeat)
  - `GET /devices/{device_id}/commands` (명령 조회)
  - `POST /devices/{device_id}/reports` (리포트 전송)
  - `GET /devtools/devices` (디바이스 목록)
  - `POST /devtools/emit_report` (테스트용 리포트)

#### `backend/app/models.py` (Pydantic 모델)
- **역할**: 요청/응답 데이터 모델 정의
- **주요 모델**:
  - `PairingStartReq`, `PairingStartResp`
  - `PairingConfirmByCodeReq`, `PairingConfirmByCodeResp`
  - `PairingCompleteReq`, `PairingCompleteResp`
  - `HeartbeatReq`, `CommandsResp`
  - `ReportsPushReq`, `AgentReport`
  - `DeviceCommand`, `DevicePolicy`, `ClientContext`

#### `backend/app/store.py` (In-memory 스토어)
- **역할**: 디바이스 및 이벤트 저장소
- **구성**:
  - `DeviceStore`: 디바이스 정보, 페어링, Heartbeat
  - `EventStore`: SSE 이벤트 저장 및 재생
- **주의**: In-memory (휘발성) → Redis/Postgres 연동 필요

#### `backend/app/sse.py` (SSE Broadcaster)
- **역할**: SSE 이벤트 발행 및 스트리밍
- **기능**:
  - `publish(tenant, session_id, event)`: 이벤트 발행
  - `stream(tenant, session_id, last_event_id)`: 스트림 생성
  - `Last-Event-ID` 기반 이벤트 재생

---

## 🚨 정리 필요 항목

### **1. Legacy 코드 (Hono 기반)**
| 디렉토리/파일 | 용도 | 조치 |
|--------------|------|------|
| `/src/` | Legacy Hono 코드 | 🗑️ 삭제 또는 백업 |
| `/dist/` | Legacy 빌드 출력 | 🗑️ 삭제 |
| `ecosystem.config.cjs` | PM2 설정 (Hono용) | 🗑️ 삭제 또는 주석 처리 |
| `wrangler.jsonc` | Cloudflare Pages 설정 | 🗑️ 삭제 (사용 안 함) |
| `package.json` (루트) | Legacy npm 설정 | 🗑️ 정리 (Frontend 별도 관리) |
| `tsconfig.json` (루트) | Legacy TypeScript 설정 | 🗑️ 정리 (Frontend 별도 관리) |
| `vite.config.ts` (루트) | Legacy Vite 설정 | 🗑️ 정리 (Frontend 별도 관리) |

**조치 방법**:
```bash
cd /home/user/webapp
mkdir -p archive/legacy_hono
mv src dist ecosystem.config.cjs wrangler.jsonc archive/legacy_hono/
mv package.json package-lock.json tsconfig.json vite.config.ts archive/legacy_hono/
```

---

### **2. 중복 설정 파일**
| 파일 | 위치 | 우선순위 | 조치 |
|------|------|----------|------|
| `package.json` | 루트 | ⚠️ 낮음 | Frontend로 통합 |
| `package.json` | Frontend | ✅ 높음 | 유지 |
| `tsconfig.json` | 루트 | ⚠️ 낮음 | Frontend로 통합 |
| `tsconfig.json` | Frontend | ✅ 높음 | 유지 |
| `vite.config.ts` | 루트 | ⚠️ 낮음 | Frontend로 통합 |
| `vite.config.ts` | Frontend | ✅ 높음 | 유지 |

---

## 📦 의존성 정리

### **Frontend 의존성** (`frontend/package.json`)
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
- **설치**: `cd frontend && npm install`

### **Backend 의존성** (`backend/requirements.txt`)
```
fastapi==0.115.6
uvicorn[standard]==0.30.6
pydantic==2.10.3
```
- **설치**: `cd backend && pip install -r requirements.txt`

### **Windows Companion 의존성** (`windows_companion/requirements.txt`)
```
requests>=2.31.0
```
- **설치**: `cd windows_companion && pip install -r requirements.txt`

---

## 🎯 실행 우선순위

### **Phase 1: 필수 설정** (즉시 실행)
1. ✅ Frontend 의존성 설치: `cd frontend && npm install`
2. ✅ Backend 의존성 설치: `cd backend && pip install -r requirements.txt`
3. ✅ 환경 변수 설정: `cp frontend/.env.local.example frontend/.env.local`
4. ✅ Backend 실행: `cd backend && uvicorn app.main:app --reload`
5. ✅ Frontend 실행: `cd frontend && npm run dev`

### **Phase 2: Legacy 정리** (선택)
1. ⬜ Legacy Hono 코드 백업 및 삭제
2. ⬜ 중복 설정 파일 정리
3. ⬜ `node_modules` (루트) 삭제

### **Phase 3: 기능 확장** (추후)
1. ⬜ Redis/Postgres 연동 (데이터 영속성)
2. ⬜ JWT 인증 추가 (웹 사용자)
3. ⬜ Approvals/RED 2PC 구현

---

## 📚 참고 문서

- **메인 README**: `/home/user/webapp/README.md`
- **v2 실행 준비**: `docs/NEXUS_V2_SETUP_CHECKLIST.md`
- **작업 컨텍스트**: `docs/NEXUS_WORK_CONTEXT.md`
- **스모크 테스트**: `docs/NEXUS_SMOKE_TEST_SCENARIOS.md`

---

**최종 업데이트**: 2026-02-03  
**분석 기준**: Frontend(React) 중심 웹앱 실행 가능 상태  
**상태**: 의존성 설치 후 즉시 실행 가능 ✅
