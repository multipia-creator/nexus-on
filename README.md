# NEXUS v7.7 통합 프로젝트

## 🎯 프로젝트 개요

NEXUS는 **SaaS + Windows Node E2E 통합 시스템**으로, 웹앱 본체와 Windows Node 확장을 연결한 Full-stack 솔루션입니다.

### **주요 특징**
- ✅ **Frontend**: React + TypeScript + Vite + Tailwind CSS
- ✅ **Backend**: FastAPI + v7.7 NEXUS Supervisor
- ✅ **Windows Node**: Python Agent (페어링, Poll, 로컬 인제스트)
- ✅ **LLM 통합**: Claude Sonnet 4.5, Gemini, OpenAI, Z.ai
- ✅ **RAG**: 로컬 파일 인덱싱 + 검색 + Evidence 추적
- ✅ **YouTube**: 검색, 큐, Embed Player
- ✅ **인프라**: Redis (상태 저장) + RabbitMQ (메시지 큐)
- ✅ **관측성**: Prometheus metrics
- ✅ **배포**: Docker Compose + Cloudflare Pages

---

## 🚀 빠른 시작 (로컬 개발)

### **1. 환경 변수 설정**

``bash
# 1. 환경 변수 파일 생성
cp .env.example .env

# 2. API 키 설정 (.env 파일 편집)
# 최소 요구사항: ANTHROPIC_API_KEY 또는 GEMINI_API_KEY
``

### **2. Docker Compose로 실행**

```bash
# 전체 스택 실행 (Frontend + Backend + Redis + RabbitMQ)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### **3. 접속**

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **Backend Health**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics (Prometheus)
- **RabbitMQ UI**: http://localhost:15672 (guest/guest)

---

## 📁 프로젝트 구조

```
nexus/
├── frontend/              # React Frontend
│   ├── src/              # TypeScript 소스
│   │   ├── main.tsx      # 엔트리 포인트
│   │   ├── types.ts      # 타입 정의
│   │   ├── lib/          # HTTP 클라이언트
│   │   ├── stream/       # SSE 스트림
│   │   ├── shell/        # UI 컴포넌트
│   │   ├── devices/      # 디바이스 API
│   │   ├── youtube/      # YouTube 패널
│   │   └── nodes/        # Windows Node 관리
│   ├── public/           # 정적 자산
│   ├── Dockerfile        # Frontend 빌드
│   └── package.json
│
├── backend/              # v7.7 NEXUS Backend
│   ├── nexus_supervisor/ # 메인 애플리케이션
│   │   ├── app.py        # FastAPI 앱
│   │   ├── Dockerfile    # Backend 빌드
│   │   └── requirements.txt
│   ├── shared/           # 공유 모듈 (68개 파일)
│   │   ├── llm_client.py # LLM 통합
│   │   ├── rag_naive.py  # RAG 엔진
│   │   ├── rag_folder_ingest.py # RAG 폴더 인제스트
│   │   ├── node_store.py # Windows Node 상태 관리
│   │   ├── youtube_client.py
│   │   └── ...
│   ├── agents/           # 에이전트 워커
│   ├── data/             # RAG 데이터 (볼륨 마운트)
│   ├── docs/             # 문서
│   └── .env.example      # 환경 변수 템플릿
│
├── node_agent/           # Windows Node Agent
│   ├── node_agent.py     # Python 프로토타입
│   └── node_config.json  # 노드 설정 (자동 생성)
│
├── docs/                 # 통합 문서
│   ├── NEXUS_V7_INTEGRATION.md  # 통합 가이드
│   ├── API_COMPATIBILITY.md      # API 호환성
│   └── ...
│
├── DEPLOYMENT_GUIDE.md   # 배포 가이드
├── docker-compose.yml    # 기본 설정
├── docker-compose.dev.yml   # 개발 환경
├── docker-compose.prod.yml  # 프로덕션 환경
├── .env.example          # 환경 변수 템플릿
└── README.md             # 이 파일
```

---

## 🔧 개발 환경 설정

### **Frontend 개발 (로컬)**

```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

### **Backend 개발 (로컬)**

```bash
cd backend

# Python 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r nexus_supervisor/requirements.txt

# Redis & RabbitMQ 실행 (Docker)
docker-compose up -d redis rabbitmq

# Backend 실행
cd nexus_supervisor
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 배포

### **1. Cloudflare Pages (Frontend Only - 데모 모드)**

```bash
cd frontend
npm run build

# Cloudflare Pages 배포
npx wrangler pages deploy dist --project-name nexus-frontend

# 환경 변수 설정
# VITE_DEMO_MODE=true
```

**배포 URL**: https://nexus-frontend-b4d.pages.dev/

### **2. Docker Compose (Full-stack)**

```bash
# 프로덕션 모드로 실행
docker-compose -f docker-compose.prod.yml up -d

# 외부 포트 80으로 접속
curl http://your-server-ip/
```

---

## 📊 v7.7 Backend 주요 기능

### **1. LLM 통합 (멀티 프로바이더)**

```python
# 지원 LLM:
# - Claude Sonnet 4.5 (Anthropic) ⭐ 추천
# - Gemini 3 Flash (Google)
# - GPT-4/GPT-5 (OpenAI)
# - GLM-4.7 (Z.ai)

# Fallback 체인 지원
LLM_PROVIDER=anthropic
LLM_FALLBACKS=gemini,openai
```

### **2. RAG (Retrieval-Augmented Generation)**

```bash
# 로컬 파일을 /data/gdrive_mirror에 배치
# Backend가 자동으로 인덱싱 (03:00 KST)
# HWP 파일은 외부 변환 후 PDF/TXT로 저장
```

### **3. YouTube 통합**

```python
# YouTube 검색, 큐, 재생
# YOUTUBE_API_KEY 필요
```

### **4. 관측성 (Observability)**

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# 핵심 메트릭:
# - task_create_total
# - llm_generate_total
# - callback_total
# - queue_publish_fail_total
```

### **5. Redis + RabbitMQ**

```bash
# Redis: 상태 저장, 캐싱 (7일 TTL)
# RabbitMQ: 비동기 작업 큐, DLQ (Dead Letter Queue)
```

---

## 🔐 보안

### **인증**
- `NEXUS_API_KEY`: API 인증
- `ADMIN_API_KEY`: 관리자 작업 (DLQ 등)
- HMAC 서명: 콜백 무결성 (옵션)

### **PII 마스킹**
- 전화번호, 이메일, API 키 자동 마스킹
- 로그에 민감 정보 노출 방지

---

## 🧪 테스트

### **Contract Tests (계약 검증)**

```bash
# Frontend 계약 테스트
cd frontend
npm test

# Backend 계약 테스트
cd backend
python -m pytest tests/test_contracts.py -v

# 통합 테스트
./test-contracts.sh
```

### **CI/CD (GitHub Actions)**

```bash
# .github/workflows/contracts.yml
# - Frontend 계약 테스트
# - Backend 계약 테스트
# - Docker 빌드 테스트
```

---

## 📖 문서

- **Backend 문서**: `backend/docs/`
  - `CLAUDE.md`: Claude Code 작업 규칙
  - `NEXUS_BIBLE_README.md`: v7.7 전체 가이드
  - `RUNBOOK_LOCALSERVER_CLAUDE45.md`: 로컬 서버 실행 가이드
  - `CONTRACT.md`: API 계약 명세

- **프로젝트 문서**: `docs/`
  - `NEXUS_V7_INTEGRATION.md`: 통합 가이드
  - `PRODUCTION_CHECKLIST.md`: 상용화 체크리스트
  - `CLOUDFLARE_DEPLOYMENT_SUCCESS.md`: 배포 가이드

---

## 🐛 트러블슈팅

### **Docker 빌드 실패**

```bash
# 캐시 클리어 후 재빌드
docker-compose build --no-cache

# 특정 서비스만 재빌드
docker-compose build backend
```

### **Backend 연결 실패**

```bash
# Backend 로그 확인
docker-compose logs backend

# Health check
curl http://localhost:8000/health
```

### **Redis/RabbitMQ 연결 실패**

```bash
# 서비스 상태 확인
docker-compose ps

# Redis 연결 테스트
docker-compose exec redis redis-cli ping

# RabbitMQ 연결 테스트
curl http://localhost:15672/api/overview
```

---

## 🔄 프로젝트 히스토리

### **최신 구현 (2026-02-03)**

1. ✅ **SaaS + Windows Node E2E 통합**
   - Node 페어링 (6자리 코드, 5분 TTL)
   - Poll 기반 명령 수신 (Outbound Only)
   - 로컬 폴더 스캔 + 텍스트 추출
   - 리포트 업로드 (SSE 실시간 UI 반영)
   - RAG 자동 인제스트

2. ✅ **RAG 인제스트/정규화 파이프라인 개선**
   - Evidence 정보 추가 (doc_id, chunk_id, page, offset)
   - HWP 무조건 변환 정책 (fallback 검색)
   - 실패 파일 격리 + 재시도 메커니즘

3. ✅ **YouTube 기능 구현**
   - 검색 (YouTube Data API v3 + 1시간 캐시)
   - 큐 관리 (Redis 기반, tenant+session 격리)
   - Embed Player (iframe)

4. ✅ **Orchestrator 개선**
   - RED 강제 검증 (7개 명령 타입)
   - command_id 검증 (Idempotency)
   - 202 Accepted + SSE 스트리밍

5. ✅ **Frontend 채팅 UI**
   - 입력창 + Enter 전송
   - /chat 엔드포인트 연동
   - Demo 모드 지원

### **백업**

- **최신 백업**: https://www.genspark.ai/api/files/s/ji1pPLeA
- **크기**: 1.39 MB
- **내용**: SaaS + Windows Node E2E 구현 완료

---

## 🚀 배포 가이드

상세한 배포 가이드는 `DEPLOYMENT_GUIDE.md`를 참조하세요.

### **빠른 배포 (Cloudflare Pages)**

```bash
cd frontend
npm run build
npx wrangler pages deploy dist --project-name webapp
```

**배포 URL**: https://webapp.pages.dev

---

## 🖥️ Windows Node Agent

### **설치**

```bash
cd node_agent
pip install requests
```

### **사용법**

```bash
# 1. 페어링
python node_agent.py --enroll ABC123 --base-url https://your-backend.com

# 2. 에이전트 실행 (Poll 모드)
python node_agent.py --run --base-url https://your-backend.com
```

### **기능**

- ✅ Enrollment (페어링 코드)
- ✅ Poll Commands (HTTP Long Polling, 30초)
- ✅ Execute: `local.folder.ingest` (로컬 폴더 스캔)
- ✅ Report Upload (진행 상황 + 최종 결과)
- ✅ Config 저장 (`node_config.json`)

---

## 📞 지원

문제가 발생하면:
1. `backend/CLAUDE.md` 읽기 (작업 규칙)
2. `docker-compose logs backend` 확인
3. GitHub Issues 생성

---

## 📜 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

---

**최종 업데이트**: 2026-02-03  
**버전**: v7.7 + SaaS + Windows Node E2E  
**상태**: 빌드 완료, 배포 대기  
**백업 URL**: https://www.genspark.ai/api/files/s/ji1pPLeA
