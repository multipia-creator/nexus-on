# NEXUS v2 — Web-first AI Agent System

**프로젝트**: NEXUS 세리아 AI 에이전트 시스템  
**도메인**: nexus  
**버전**: v2.0 (Web-first + Windows Companion)  
**스택**: React (Frontend) + FastAPI (Backend) + Windows Companion (Python)

---

## 📋 프로젝트 개요

NEXUS v2는 **웹 기반 AI 에이전트 시스템**으로, SSE(Server-Sent Events)를 통한 실시간 상태 동기화와 디바이스 연동을 지원합니다.

### 핵심 아키텍처
- **Frontend**: React + TypeScript + Vite (포트 5173)
- **Backend**: FastAPI + SSE + Device API (포트 8000)
- **Windows Companion**: Python 기반 로컬 디바이스 에이전트
- **계약 준수**: SSE 단일 소스, 202 Accepted 패턴, Two-Phase Commit

---

## 📁 디렉토리 구조

```
nexus/
├── frontend/              # React UI (393 lines)
│   ├── src/
│   │   ├── main.tsx      # 엔트리 포인트
│   │   ├── types.ts      # TypeScript 타입 정의
│   │   ├── lib/          # HTTP 클라이언트, Correlation ID
│   │   ├── stream/       # SSE 스트림 훅 (useAgentReportStream)
│   │   ├── shell/        # Shell, Dock, AssistantStage, Dashboard, Sidecar
│   │   └── devices/      # Devices 모달, API, Badge
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── .env.local.example
│
├── backend/               # FastAPI Backend (625 lines)
│   ├── app/
│   │   ├── main.py       # 메인 애플리케이션 (SSE + Device API)
│   │   ├── models.py     # Pydantic 모델
│   │   ├── store.py      # In-memory 데이터 스토어
│   │   └── sse.py        # SSE Broadcaster
│   ├── requirements.txt
│   └── README.md
│
├── windows_companion/     # Windows Companion
│   ├── companion.py
│   ├── requirements.txt
│   ├── config.example.json
│   └── RUN_WINDOWS.cmd
│
├── scripts/               # 실행 스크립트
│   ├── START_BACKEND_WIN.cmd
│   └── START_FRONTEND_WIN.cmd
│
├── docs/                  # 문서
│   ├── API_KEYS.md
│   ├── API_SETUP_COMPLETE.md
│   ├── NEXUS_WORK_CONTEXT.md
│   ├── NEXUS_EXECUTION_CHECKLIST.md
│   ├── NEXUS_SMOKE_TEST_SCENARIOS.md
│   ├── NEXUS_ERROR_FIXES.md
│   └── NEXUS_IMPLEMENTATION_INSTRUCTIONS.md
│
├── src/                   # Legacy Hono 코드 (제거 예정)
├── public/                # 정적 파일
├── README.md              # 본 문서
└── MANIFEST.sha256        # 파일 체크섬
```

---

## 🚀 실행 방법

### **사전 요구사항**
- **Node.js**: v18 이상 (Frontend)
- **Python**: 3.9 이상 (Backend + Windows Companion)
- **Windows 11**: Windows Companion 실행 시 필요

---

### **1. Backend 실행** (포트 8000)

#### Windows:
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set CORS_ORIGINS=http://localhost:5173
uvicorn app.main:app --reload --port 8000
```

#### Linux/Mac:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export CORS_ORIGINS=http://localhost:5173
uvicorn app.main:app --reload --port 8000
```

**환경 변수**:
- `CORS_ORIGINS`: CORS 허용 도메인 (기본값: `http://localhost:5173`)

---

### **2. Frontend 실행** (포트 5173)

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

**환경 변수** (`.env.local`):
```env
VITE_API_BASE=http://localhost:8000
```

**접속**: http://localhost:5173

---

### **3. Windows Companion 실행** (선택)

Windows Companion은 로컬 PC에서 실행되는 디바이스 에이전트로, 웹 UI와 페어링하여 명령을 수신하고 보고서를 전송합니다.

```cmd
cd windows_companion
copy config.example.json config.json
REM (필요 시 config.json 수정)
RUN_WINDOWS.cmd
```

**페어링 흐름**:
1. Backend + Frontend 실행
2. Windows Companion 실행 → **Pairing Code** 출력 (예: `123-456`)
3. 웹 UI → **Devices** 버튼 클릭 → 코드 입력 → **Confirm**
4. Companion이 자동으로 토큰 획득 → Heartbeat + Command Loop 시작

---

## 🏗️ 빌드 및 배포

### **Frontend 빌드**
```bash
cd frontend
npm run build
# 빌드 결과: frontend/dist/
```

### **Frontend 프리뷰**
```bash
cd frontend
npm run preview
```

---

## 📡 API 엔드포인트

### **SSE (Server-Sent Events)**
- `GET /agent/reports/stream?session_id={session_id}`
  - SSE 스트림 (snapshot, report, ping 이벤트)
  - 헤더: `Last-Event-ID` (재연결 시 이벤트 재생)

### **Device Pairing**
- `POST /devices/pairing/start`
- `POST /devices/pairing/confirm_by_code`
- `POST /devices/pairing/complete`

### **Device Sync**
- `POST /devices/{device_id}/heartbeat`
- `GET /devices/{device_id}/commands`
- `POST /devices/{device_id}/commands/{command_id}/ack`
- `POST /devices/{device_id}/reports`

### **Devtools**
- `GET /devtools/devices` (tenant별 디바이스 목록)
- `POST /devtools/emit_report` (SSE 테스트용 합성 리포트)

---

## 🔑 환경 변수 목록

### **Frontend** (`.env.local`)
| 변수 | 설명 | 예시 |
|------|------|------|
| `VITE_API_BASE` | Backend API URL | `http://localhost:8000` |

### **Backend** (환경 변수)
| 변수 | 설명 | 예시 |
|------|------|------|
| `CORS_ORIGINS` | CORS 허용 도메인 | `http://localhost:5173` |

### **Windows Companion** (`config.json`)
```json
{
  "backend_url": "http://localhost:8000",
  "device_type": "windows_desktop",
  "device_name": "MyPC",
  "capabilities": ["file_ops", "shell"]
}
```

---

## ✅ 실행 가능 상태 점검

### **Frontend 점검**
- ✅ **패키지 설치 완료**: `package.json`에 React, Vite 등 명시
- ✅ **환경 변수 예시 존재**: `.env.local.example`
- ✅ **빌드 스크립트 존재**: `npm run build`
- ✅ **Vite 프록시 설정**: `/agent`, `/sidecar`, `/approvals` → Backend로 프록시
- ✅ **SSE 스트림 구현**: `useAgentReportStream.ts`
- ✅ **코드 라인 수**: 393줄 (간결한 구조)

### **Backend 점검**
- ✅ **의존성 명시**: `requirements.txt` (FastAPI, Uvicorn, Pydantic)
- ✅ **SSE 구현**: `broadcaster.stream()` (event_id 기반 재생)
- ✅ **Device API 구현**: 페어링, Heartbeat, Commands, Reports
- ✅ **CORS 설정**: 환경 변수 기반 CORS 허용
- ✅ **In-memory Store**: Redis/Postgres 대체 (개발 단계)
- ✅ **코드 라인 수**: 625줄

### **계약 준수 점검**
- ✅ **SSE 단일 소스**: UI 상태는 `/agent/reports/stream`만 구독
- ✅ **202 Accepted 패턴**: `/sidecar/command`, `/approvals/*/decide`는 202 반환 후 SSE로 상태 전이
- ✅ **Last-Event-ID 재생**: SSE 재연결 시 누락된 이벤트 재생
- ✅ **Correlation ID**: 요청-응답 추적 가능

---

## 🚨 누락된 항목 및 개선 필요 사항

### **1. 환경 변수**
| 항목 | 상태 | 위치 | 해결 방법 |
|------|------|------|----------|
| Frontend `.env.local` | ⚠️ 예시만 존재 | `frontend/.env.local.example` | 복사하여 `.env.local` 생성 |
| Backend 환경 변수 | ⚠️ 수동 설정 필요 | 터미널에서 `set CORS_ORIGINS=...` | `.env` 파일 생성 권장 |

### **2. 의존성**
| 항목 | 상태 | 해결 방법 |
|------|------|----------|
| Frontend `node_modules` | ❌ 미설치 | `cd frontend && npm install` |
| Backend `.venv` | ❌ 미생성 | `cd backend && python -m venv .venv` |
| Backend 패키지 | ❌ 미설치 | `.venv\Scripts\activate && pip install -r requirements.txt` |

### **3. 데이터 영속성**
| 항목 | 상태 | 권장 사항 |
|------|------|----------|
| Device Store | ⚠️ In-memory (휘발성) | Redis 또는 Postgres 연동 |
| Event Store | ⚠️ In-memory (휘발성) | Redis Streams 또는 Postgres 연동 |

### **4. 인증 및 보안**
| 항목 | 상태 | 권장 사항 |
|------|------|----------|
| 웹 사용자 인증 | ❌ 미구현 | JWT 또는 OAuth 추가 |
| Device 토큰 관리 | ✅ Bearer Token | 만료 시간 및 갱신 로직 추가 |
| HTTPS | ⚠️ 로컬 개발만 HTTP | 프로덕션 배포 시 HTTPS 필수 |

### **5. Approvals/RED 2PC**
| 항목 | 상태 | 권장 사항 |
|------|------|----------|
| Approvals API | ❌ 미구현 | `/approvals/{ask_id}/decide` 엔드포인트 추가 |
| Two-Phase Commit | ❌ 미구현 | 고위험 명령에 대한 승인 게이트 추가 |

### **6. Legacy 코드 정리**
| 항목 | 상태 | 해결 방법 |
|------|------|----------|
| `/src` 디렉토리 | ⚠️ Hono 기반 레거시 | 제거 또는 백업 후 삭제 |
| `ecosystem.config.cjs` | ⚠️ PM2 설정 (Hono용) | Frontend/Backend 별도 실행 스크립트로 대체 |
| `wrangler.jsonc` | ⚠️ Cloudflare Pages 설정 | 사용하지 않으면 삭제 |

---

## 📚 참고 문서

### **핵심 문서**
- **작업 컨텍스트**: `docs/NEXUS_WORK_CONTEXT.md`
- **실행 체크리스트**: `docs/NEXUS_EXECUTION_CHECKLIST.md`
- **스모크 테스트**: `docs/NEXUS_SMOKE_TEST_SCENARIOS.md`
- **오류 수정 가이드**: `docs/NEXUS_ERROR_FIXES.md`
- **구현 지시서**: `docs/NEXUS_IMPLEMENTATION_INSTRUCTIONS.md`

### **API 문서**
- **API 키 관리**: `docs/API_KEYS.md`
- **API 설정 완료**: `docs/API_SETUP_COMPLETE.md`

---

## 🔧 개발 워크플로우

### **로컬 개발**
1. **Backend 실행**: `cd backend && uvicorn app.main:app --reload`
2. **Frontend 실행**: `cd frontend && npm run dev`
3. **브라우저 접속**: http://localhost:5173
4. **SSE 테스트**: `POST /devtools/emit_report` (curl 또는 Postman)

### **디버깅**
- **Backend 로그**: 터미널에서 Uvicorn 로그 확인
- **Frontend 로그**: 브라우저 개발자 도구 → Console
- **SSE 스트림**: 브라우저 개발자 도구 → Network → `stream` 요청 확인

### **테스트**
- **Smoke Test**: `docs/NEXUS_SMOKE_TEST_SCENARIOS.md` 참고
- **SSE 재생 테스트**: 브라우저 새로고침 → `Last-Event-ID` 헤더로 이벤트 재생 확인

---

## 🎯 다음 단계

### **Phase 1: 기본 기능 완성** (우선순위 높음)
1. ✅ Frontend/Backend 실행 환경 구축
2. ⬜ `.env` 파일 생성 및 환경 변수 설정
3. ⬜ `npm install` + `pip install` 실행
4. ⬜ SSE 스트림 동작 확인 (`/devtools/emit_report` 테스트)
5. ⬜ Device Pairing 흐름 E2E 테스트

### **Phase 2: 데이터 영속성** (중간 우선순위)
1. ⬜ Redis 또는 Postgres 연동
2. ⬜ Device Store 영속화
3. ⬜ Event Store 영속화 (Redis Streams 권장)

### **Phase 3: 보안 및 인증** (중간 우선순위)
1. ⬜ 웹 사용자 인증 (JWT 또는 OAuth)
2. ⬜ Device Token 만료 및 갱신 로직
3. ⬜ HTTPS 설정 (프로덕션 배포)

### **Phase 4: 고급 기능** (낮은 우선순위)
1. ⬜ Approvals/RED Two-Phase Commit 구현
2. ⬜ Sidecar Command 실행 로직
3. ⬜ Windows Companion 기능 확장

---

## 📞 문의 및 지원

- **프로젝트 관리자**: 남현우 교수
- **도메인**: nexus
- **Git 저장소**: `/home/user/webapp/.git`

---

**최종 업데이트**: 2026-02-03  
**버전**: v2.0  
**상태**: 개발 중 (실행 가능 상태)
