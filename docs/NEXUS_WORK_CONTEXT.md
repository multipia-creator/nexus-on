# NEXUS 작업 컨텍스트 (필수 참조)

**작성일**: 2026-02-03  
**목적**: NEXUS 시스템의 불변 계약 및 실행 기준선 정의

---

## 📌 핵심 원칙 (CLAUDE.md)

### 🚨 불변 계약 (절대 변경 금지)

#### 1. SSE 스트림 = UI 갱신의 단일 소스
```
/agent/reports/stream (SSE) ← 모든 UI 상태 변경은 여기서만
├─ snapshot 이벤트: 초기 상태
├─ report 이벤트: 상태 변경
└─ Last-Event-ID 리플레이 지원
```

**중요**: `/approvals/*`, `/sidecar/command`는 **202 Accepted만 반환**
- UI 상태 전이는 반드시 SSE 후속 report로만 처리
- 응답에서 직접 UI를 업데이트하면 안 됨

#### 2. Two-Phase Commit (RED 작업)
```
외부 공유/전송 작업 → 승인 없이 실행 불가
```

**프로세스**:
1. 사용자 요청 → `202 Accepted`
2. Ask(승인 요청) 생성 → SSE로 UI 전달
3. 사용자 승인 → `/approvals/{ask_id}/decide`
4. 실행 완료 → SSE로 결과 전달

#### 3. 멀티테넌트 컨텍스트
- **헤더**: `x-org-id`, `x-project-id`
- **범위**: 키 주입, 감사, 비용 태깅

#### 4. 위험도 정책
- **GREEN**: 자동 실행
- **YELLOW**: 경고만
- **RED**: 반드시 승인 필요

#### 5. RAG (HWP 포함)
```
로컬 미러 폴더 → 인덱싱
```
- HWP는 외부 변환이 선행되어야 함
- 같은 basename의 `.pdf` 또는 `.txt` 생성 권장

---

## 🏗️ 아키텍처 구성 (RUNBOOK_LOCALSERVER_CLAUDE45.md)

### 시스템 구성
```
┌─────────────────────────────────────────┐
│   Frontend: /ui (단일 HTML)             │
│   - SSE 스트림 연결                     │
│   - Worklog, Asks, Autopilot 표시       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Backend: FastAPI (Supervisor)         │
│   ├─ /agent/reports/stream (SSE)        │
│   ├─ /sidecar/command (202 Accepted)    │
│   ├─ /approvals/* (202 Accepted)        │
│   └─ /health                            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼─────┐  ┌─────▼──────┐
│  RabbitMQ  │  │   Redis    │
│  (Queue)   │  │  (Store)   │
└────────────┘  └────────────┘
```

### 주요 엔드포인트

#### SSE 스트림 (UI 갱신)
```
GET /agent/reports/stream
Headers:
  x-org-id: {org_id}
  x-project-id: {project_id}
  Last-Event-ID: {cursor} (옵션, 리플레이용)
```

#### 사이드카 명령 (비동기)
```
POST /sidecar/command
Body: {
  "command_type": "youtube.search",
  "params": {...},
  "correlation_id": "uuid"
}
Response: 202 Accepted
→ 후속 SSE report 대기
```

#### 승인 처리 (Two-phase commit)
```
POST /approvals/{ask_id}/decide
Body: {
  "decision": "approve" | "deny",
  "reason": "..."
}
Response: 202 Accepted
→ 후속 SSE report 대기
```

---

## ⚙️ 환경 변수 (.env.example)

### 필수 설정

#### 인증
```bash
NEXUS_API_KEY=your-api-key-here
ADMIN_API_KEY=your-admin-key-here
```

#### LLM (Claude Sonnet 4.5 권장)
```bash
LLM_PRIMARY_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
LLM_REQUIRED=true
```

#### Fallback 체인
```bash
LLM_FALLBACK_PROVIDERS=gemini,openai
GEMINI_API_KEY=your-gemini-key-here
OPENAI_API_KEY=your-openai-key-here
```

#### 데이터 저장소
```bash
# Redis
REDIS_URL=redis://redis:6379/0
TASK_TTL_SECONDS=604800

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
TASK_QUEUE=nexus.tasks
DLQ_QUEUE=nexus.dlq
MAX_RETRIES=3
```

### 선택 설정

#### YouTube
```bash
YOUTUBE_API_KEY=your-youtube-key-here
YOUTUBE_DEFAULT_REGION=KR
YOUTUBE_DEFAULT_LANGUAGE=ko
```

#### RAG (자동 ingest)
```bash
RAG_AUTO_INGEST_ENABLED=true
RAG_AUTO_INGEST_PATH=/data/gdrive_mirror
RAG_AUTO_INGEST_HOUR=3
RAG_AUTO_INGEST_MINUTE=0
RAG_AUTO_INGEST_EXTENSIONS=pdf,docx,pptx,xlsx,txt,md,hwp
RAG_AUTO_INGEST_MAX_FILES=5000
RAG_AUTO_INGEST_MAX_FILE_MB=50
```

#### SSE 스트림 설정
```bash
STREAM_EVENT_KEEP=2000
STREAM_WORKLOG_KEEP=200
```

#### Circuit Breaker
```bash
BREAKER_WINDOW_SECONDS=300
BREAKER_FAIL_THRESHOLD=5
BREAKER_COOLDOWN_SECONDS=120
```

#### DLQ 정책
```bash
AUTO_REQUEUE_FAILURE_CODES=PROVIDER_TIMEOUT,PROVIDER_UPSTREAM_ERROR,PROVIDER_RATE_LIMIT
AUTO_HOLD_FAILURE_CODES=SCHEMA_PARSE_ERROR,SCHEMA_VALIDATION_ERROR,SCHEMA_REPAIR_FAILED
AUTO_ALARM_FAILURE_CODES=PROVIDER_AUTH_ERROR,PROVIDER_DISABLED
```

#### FinOps
```bash
LLM_BUDGET_DAILY_USD=20
LLM_BUDGET_SOFT_PCT=0.8
LLM_BUDGET_HARD_PCT=1.0
LLM_COST_LEDGER_PATH=logs/llm_cost_ledger.jsonl
LLM_AUDIT_ENABLED=true
LLM_AUDIT_LOG_PATH=logs/llm_audit.jsonl
```

---

## 🚀 실행 방법

### Docker Compose (권장)
```bash
cd /home/user/webapp/docs/backend_reference
cp .env.example .env
# .env 편집 (API 키 설정)
docker compose -f docker/docker-compose.nexus.yml up --build
```

### 접속
- **UI**: http://localhost:8000/ui
- **Health**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **RabbitMQ**: http://localhost:15672 (guest/guest)

---

## ✅ 검증 시나리오

### 1. SSE 연결 확인
1. UI 열기 (`http://localhost:8000/ui`)
2. 새 메시지 입력
3. Worklog/Asks/Autopilot에 반영 확인

### 2. Approvals (RED 흐름)
1. 외부 공유/전송 타입 커맨드 요청
2. Ask 생성 확인
3. 승인 버튼 클릭
4. SSE 후속 report로 상태 전이 확인

### 3. YouTube
1. `youtube.search` → 결과 표시
2. `youtube.queue.add` → 큐 반영
3. `youtube.queue.next` → 재생 프레임 변경

### 4. RAG
1. `data/gdrive_mirror`에 pdf/docx/txt 추가
2. 수동: `rag.folder.ingest` 실행
3. 자동: 03:00 KST 스케줄 대기

### 5. HWP
1. `.hwp` 파일 → pending 처리
2. 같은 basename의 `.pdf` 또는 `.txt` 생성
3. 정상 인덱싱 확인

---

## 🔍 변경 시 체크리스트

### 필수 통과 항목
- [ ] `python -m py_compile nexus_supervisor/app.py`
- [ ] `bash deploy/smoke_test.sh` (옵션)
- [ ] SSE 스트림에서 `report_id` dedupe 확인
- [ ] SSE 스트림에서 `correlation_id` 전파 확인
- [ ] 202 Accepted 응답 후 SSE report 전송 확인
- [ ] Two-phase commit 흐름 유지 확인

---

## 🎯 Cloudflare Pages 통합 시 고려사항

### Python 백엔드를 그대로 사용하는 경우 (전략 A)
```
Cloudflare Pages (UI + BFF)
         ↓ HTTPS
외부 백엔드 서버 (Python FastAPI)
  ├─ Heroku, Railway, Render
  └─ 또는 VPS (Linode, DigitalOcean)
```

**BFF 역할**:
- SSE 프록시 (헤더 첨부, Last-Event-ID 처리)
- 멀티테넌트 헤더 주입 (`x-org-id`, `x-project-id`)
- 인증/인가

### TypeScript로 재작성하는 경우 (전략 B)
**필수 구현 항목**:
1. SSE 스트림 (`/agent/reports/stream`)
   - ReadableStream 기반
   - Last-Event-ID 리플레이
   - correlation_id 전파
   
2. 202 Accepted 패턴
   - `/sidecar/command` → 202 → SSE report
   - `/approvals/*` → 202 → SSE report
   
3. Cloudflare 서비스 매핑
   - PostgreSQL → D1 Database
   - Redis → KV Storage
   - RabbitMQ → Queues
   - 파일 저장 → R2 Storage

---

## 📚 참고 문서

- **전체 가이드**: `/docs/backend_reference/NEXUS_BIBLE_README.md`
- **실행 가이드**: `/docs/backend_reference/docs/RUNBOOK_LOCALSERVER_CLAUDE45.md`
- **불변 계약**: `/docs/backend_reference/CLAUDE.md`
- **환경 변수**: `/docs/backend_reference/.env.example`
- **API 문서**: `/docs/backend_reference/openapi.yaml`
- **아키텍처**: `/docs/backend_reference/docs/architecture/NEXUS_Architecture.md`

---

## ⚠️ 주의사항

### 금지 사항
1. ❌ 202 응답으로 UI 상태 확정 금지
2. ❌ RED 작업 승인 없이 실행 금지
3. ❌ SSE 외의 채널로 UI 상태 변경 금지
4. ❌ report 이벤트 순서 역전 금지
5. ❌ correlation_id 전파 누락 금지

### 권장 사항
1. ✅ 항상 SSE 스트림으로 UI 업데이트
2. ✅ 비동기 작업은 202 Accepted 반환
3. ✅ correlation_id를 요청→report까지 전파
4. ✅ Last-Event-ID로 리플레이 지원
5. ✅ 멀티테넌트 헤더 일관 사용

---

**최종 업데이트**: 2026-02-03  
**버전**: v7.7 기준  
**상태**: 작업 컨텍스트 확정 완료
