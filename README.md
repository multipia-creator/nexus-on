# NEXUS v7.7 통합 프로젝트

## 🎯 프로젝트 개요

NEXUS는 **Web-first AI Agent System**으로, 최신 v7.7 Backend와 React Frontend를 결합한 Full-stack 솔루션입니다.

### **주요 특징**
- ✅ **Frontend**: React + TypeScript + Vite + Tailwind CSS
- ✅ **Backend**: FastAPI + v7.7 NEXUS Supervisor
- ✅ **LLM 통합**: Claude Sonnet 4.5, Gemini, OpenAI, Z.ai
- ✅ **RAG**: 로컬 파일 인덱싱 + 검색
- ✅ **YouTube**: 검색, 큐, 재생
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
│   │   └── devices/      # 디바이스 API
│   ├── public/           # 정적 자산
│   ├── Dockerfile        # Frontend 빌드
│   └── package.json
│
├── backend/              # v7.7 NEXUS Backend
│   ├── nexus_supervisor/ # 메인 애플리케이션
│   │   ├── app.py        # FastAPI 앱
│   │   ├── Dockerfile    # Backend 빌드
│   │   └── requirements.txt
│   ├── shared/           # 공유 모듈 (67개 파일)
│   │   ├── llm_client.py # LLM 통합
│   │   ├── rag_naive.py  # RAG 엔진
│   │   ├── youtube_client.py
│   │   └── ...
│   ├── agents/           # 에이전트 워커
│   ├── data/             # RAG 데이터 (볼륨 마운트)
│   ├── docs/             # 문서
│   └── .env.example      # 환경 변수 템플릿
│
├── docs/                 # 통합 문서
│   ├── NEXUS_V7_INTEGRATION.md  # 통합 가이드
│   ├── API_COMPATIBILITY.md      # API 호환성
│   └── ...
│
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

## 🔄 v7.7 통합 히스토리

### **통합 작업 (2026-02-03)**

1. ✅ v7.7 Backend 코드 분석
2. ✅ 기존 backend를 v7.7로 교체
3. ✅ Docker Compose에 Redis + RabbitMQ 추가
4. ✅ 환경 변수 설정 (.env.example)
5. ✅ Dockerfile 수정 (Build context 최적화)
6. ⏳ Frontend API 호환성 검증 (진행 중)
7. ⏳ 통합 테스트

### **백업된 파일**

기존 Backend는 `backend_backup_YYYYMMDD_HHMMSS/`로 백업되었습니다.

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
**버전**: v7.7 통합  
**상태**: 통합 테스트 진행 중
