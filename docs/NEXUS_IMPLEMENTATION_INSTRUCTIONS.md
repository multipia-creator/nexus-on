# NEXUS Claude Sonnet 4.5 구현 지시서 (PR 단위)

**작성일**: 2026-02-03  
**대상**: Claude Sonnet 4.5 (또는 동등 수준 AI Assistant)  
**목적**: 로컬 Docker Compose 환경에서 NEXUS 실행을 위한 단계별 구현

---

## 📋 전체 구현 로드맵

### Phase 0: 준비 (완료)
- ✅ 프로젝트 구조 분석
- ✅ 불변 계약 이해
- ✅ 실행 체크리스트 작성
- ✅ 테스트 시나리오 작성

### Phase 1: 환경 설정 (1-2 PR)
- [ ] PR-001: Docker Compose 설정 수정
- [ ] PR-002: 환경 변수 템플릿 정리

### Phase 2: 불변 계약 준수 (3-4 PR)
- [ ] PR-003: 202 Accepted 패턴 적용
- [ ] PR-004: SSE 스트림 구현
- [ ] PR-005: correlation_id 전파
- [ ] PR-006: Two-Phase Commit 구현

### Phase 3: 안정성 개선 (2-3 PR)
- [ ] PR-007: 오류 처리 강화
- [ ] PR-008: 로깅 및 모니터링
- [ ] PR-009: 재연결 로직 추가

---

## 🎯 PR-001: Docker Compose 설정 수정

### 목표
로컬 PC에서 안정적으로 실행되도록 Docker Compose 설정 개선

### 배경
현재 `docker-compose.nexus.yml`은 기본 설정으로, 다음 개선 필요:
1. Health check 추가
2. 의존성 순서 명확화
3. 메모리 제한 설정
4. 재시작 정책 추가

### Definition of Done
- [ ] 모든 컨테이너에 healthcheck 추가
- [ ] depends_on에 condition 추가
- [ ] 메모리 제한 설정 (최소 4GB 환경 고려)
- [ ] restart: unless-stopped 설정
- [ ] smoke test 통과

### 구현 지시

**파일**: `/home/user/webapp/docs/backend_reference/docker/docker-compose.nexus.yml`

#### 1. Redis 컨테이너 개선
```yaml
redis:
  image: redis:7-alpine
  container_name: nexus-redis-1
  restart: unless-stopped
  mem_limit: 512m
  mem_reservation: 256m
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 3s
    retries: 3
    start_period: 5s
  volumes:
    - redis_data:/data
  networks:
    - nexus
```

#### 2. RabbitMQ 컨테이너 개선
```yaml
rabbitmq:
  image: rabbitmq:3-management-alpine
  container_name: nexus-rabbitmq-1
  restart: unless-stopped
  mem_limit: 1g
  mem_reservation: 512m
  environment:
    RABBITMQ_DEFAULT_USER: guest
    RABBITMQ_DEFAULT_PASS: guest
  ports:
    - "5672:5672"
    - "15672:15672"
  healthcheck:
    test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s
  volumes:
    - rabbitmq_data:/var/lib/rabbitmq
  networks:
    - nexus
```

#### 3. Supervisor 컨테이너 개선
```yaml
nexus-supervisor:
  build:
    context: ../
    dockerfile: nexus_supervisor/Dockerfile
  container_name: nexus-supervisor-1
  restart: unless-stopped
  mem_limit: 2g
  mem_reservation: 1g
  depends_on:
    redis:
      condition: service_healthy
    rabbitmq:
      condition: service_healthy
  environment:
    - REDIS_URL=redis://redis:6379/0
    - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
  env_file:
    - ../.env
  ports:
    - "8000:8000"
  volumes:
    - ../data:/data
    - ../logs:/app/logs
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 15s
    timeout: 5s
    retries: 3
    start_period: 40s
  networks:
    - nexus
```

#### 4. 네트워크 및 볼륨 정의
```yaml
networks:
  nexus:
    driver: bridge

volumes:
  redis_data:
  rabbitmq_data:
```

### 검증 방법
```bash
cd /home/user/webapp/docs/backend_reference

# 빌드 및 실행
docker compose -f docker/docker-compose.nexus.yml up --build -d

# Health check 확인
docker compose -f docker/docker-compose.nexus.yml ps
# 모든 서비스가 "healthy" 상태여야 함

# Health 엔드포인트 확인
curl http://localhost:8000/health
```

### 예상 출력
```
NAME                    STATUS
nexus-redis-1          Up (healthy)
nexus-rabbitmq-1       Up (healthy)
nexus-supervisor-1     Up (healthy)
```

---

## 🎯 PR-002: 환경 변수 템플릿 정리

### 목표
로컬 실행에 최적화된 `.env.example` 정리

### 배경
현재 `.env.example`이 너무 복잡하고, 로컬 실행에 불필요한 옵션 포함

### Definition of Done
- [ ] 필수/선택 섹션 명확 구분
- [ ] 로컬 실행에 불필요한 옵션 제거 또는 주석 처리
- [ ] 각 변수에 설명 추가
- [ ] 기본값 권장 사항 명시

### 구현 지시

**파일**: `/home/user/webapp/docs/backend_reference/.env.example`

```bash
# ============================================
# NEXUS 로컬 실행 환경 변수
# ============================================

# ============================================
# 필수 설정 (REQUIRED)
# ============================================

# 내부 인증 키 (개발 환경용, 프로덕션에서는 강력한 키 사용)
NEXUS_API_KEY=dev-key-change-in-production
ADMIN_API_KEY=admin-key-change-in-production

# Redis 연결 (Docker Compose 기본값)
REDIS_URL=redis://redis:6379/0
TASK_TTL_SECONDS=604800

# RabbitMQ 연결 (Docker Compose 기본값)
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
TASK_QUEUE=nexus.tasks
DLQ_QUEUE=nexus.dlq
MAX_RETRIES=3

# LLM Primary Provider (최소 1개 필수)
# 옵션: anthropic, gemini, openai, zai
LLM_PRIMARY_PROVIDER=anthropic
LLM_REQUIRED=true

# Anthropic Claude (권장)
# 발급: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# ============================================
# 선택 설정 (OPTIONAL)
# ============================================

# Fallback Providers (comma-separated)
# LLM_FALLBACK_PROVIDERS=gemini,openai

# Google Gemini (Fallback용)
# GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
# GEMINI_MODEL=gemini-3-flash-preview

# OpenAI (Fallback용)
# OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE
# OPENAI_MODEL=gpt-4

# Circuit Breaker (기본값 유지 권장)
BREAKER_WINDOW_SECONDS=300
BREAKER_FAIL_THRESHOLD=5
BREAKER_COOLDOWN_SECONDS=120

# YouTube Data API (검색 기능 사용 시)
# 발급: https://console.cloud.google.com/
# YOUTUBE_API_KEY=YOUR_YOUTUBE_KEY_HERE
# YOUTUBE_DEFAULT_REGION=KR
# YOUTUBE_DEFAULT_LANGUAGE=ko

# RAG Auto-Ingest (Google Drive 미러 사용 시)
# RAG_AUTO_INGEST_ENABLED=false
# RAG_AUTO_INGEST_PATH=/data/gdrive_mirror
# RAG_AUTO_INGEST_HOUR=3
# RAG_AUTO_INGEST_MINUTE=0

# SSE Stream (기본값 유지 권장)
STREAM_EVENT_KEEP=2000
STREAM_WORKLOG_KEEP=200

# ============================================
# 고급 설정 (로컬 실행 시 수정 불필요)
# ============================================

# DLQ Auto Triage
AUTO_REQUEUE_FAILURE_CODES=PROVIDER_TIMEOUT,PROVIDER_UPSTREAM_ERROR
AUTO_HOLD_FAILURE_CODES=SCHEMA_PARSE_ERROR,SCHEMA_VALIDATION_ERROR
AUTO_ALARM_FAILURE_CODES=PROVIDER_AUTH_ERROR

# Task Lock
TASK_LOCK_TTL_SECONDS=900

# FinOps (비용 추적)
# LLM_BUDGET_DAILY_USD=20
# LLM_AUDIT_ENABLED=true
```

### 검증 방법
```bash
# 환경 변수 파일 생성
cp .env.example .env

# 필수 변수 확인
grep -E "NEXUS_API_KEY|LLM_PRIMARY_PROVIDER|ANTHROPIC_API_KEY" .env

# 실행 테스트
docker compose -f docker/docker-compose.nexus.yml up -d
curl http://localhost:8000/health
```

---

## 🎯 PR-003: 202 Accepted 패턴 적용

### 목표
`/sidecar/command`, `/approvals/*`가 202 Accepted만 반환하도록 수정

### 배경
**불변 계약 #2**: 비동기 엔드포인트는 202 Accepted만 반환

### Definition of Done
- [ ] `/sidecar/command` → 202 반환
- [ ] `/approvals/{ask_id}/decide` → 202 반환
- [ ] 상태 변경은 후속 SSE report로만 전달
- [ ] smoke test 통과

### 구현 지시

#### 파일 1: `nexus_supervisor/routers/sidecar.py`

**현재 코드** (추정):
```python
@router.post("/command")
async def sidecar_command(command: SidecarCommand):
    result = await process_command(command)
    return {"status": "ok", "result": result}  # ❌ 200 OK
```

**수정 후**:
```python
from fastapi.responses import JSONResponse

@router.post("/command")
async def sidecar_command(
    command: SidecarCommand,
    org_id: str = Header(alias="x-org-id"),
    project_id: str = Header(alias="x-project-id"),
):
    # 1. Task를 큐에 넣기 (비동기)
    await enqueue_sidecar_task(
        command=command,
        org_id=org_id,
        project_id=project_id
    )
    
    # 2. 202 Accepted 반환
    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "correlation_id": command.correlation_id
        }
    )
```

#### 파일 2: `nexus_supervisor/routers/approvals.py`

**현재 코드** (추정):
```python
@router.post("/{ask_id}/decide")
async def decide_approval(ask_id: str, decision: ApprovalDecision):
    result = await execute_approval(ask_id, decision)
    return {"status": "ok", "result": result}  # ❌ 200 OK
```

**수정 후**:
```python
from fastapi.responses import JSONResponse

@router.post("/{ask_id}/decide")
async def decide_approval(
    ask_id: str,
    decision: ApprovalDecision,
    org_id: str = Header(alias="x-org-id"),
    project_id: str = Header(alias="x-project-id"),
):
    # 1. 승인/거부 처리 (비동기)
    await process_approval_decision(
        ask_id=ask_id,
        decision=decision,
        org_id=org_id,
        project_id=project_id
    )
    
    # 2. 202 Accepted 반환
    return JSONResponse(
        status_code=202,
        content={"status": "accepted"}
    )
```

### 검증 방법
```bash
# sidecar command 테스트
curl -i -X POST http://localhost:8000/sidecar/command \
  -H "Content-Type: application/json" \
  -H "x-org-id: default" \
  -H "x-project-id: nexus" \
  -H "x-api-key: dev-key-change-in-production" \
  -d '{"command_type": "echo.test", "params": {}, "correlation_id": "test-001"}'

# 예상 출력
# HTTP/1.1 202 Accepted
# {"status":"accepted","correlation_id":"test-001"}
```

### 주의사항
- 실제 처리 로직은 Worker에서 수행
- UI 업데이트는 SSE report로만 전달
- `correlation_id`를 반드시 포함하여 추적 가능하게 함

---

## 🎯 PR-004: SSE 스트림 구현

### 목표
`/agent/reports/stream` 엔드포인트에서 SSE 이벤트 전송

### 배경
**불변 계약 #1**: UI 갱신의 단일 소스는 SSE 스트림

### Definition of Done
- [ ] `/agent/reports/stream` 엔드포인트 구현
- [ ] `snapshot` 이벤트 전송 (초기 상태)
- [ ] `report` 이벤트 전송 (상태 변경)
- [ ] `Last-Event-ID` 리플레이 지원
- [ ] smoke test 통과

### 구현 지시

#### 파일: `nexus_supervisor/routers/agent_reports.py`

```python
from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import asyncio

router = APIRouter(prefix="/agent/reports", tags=["agent_reports"])

@router.get("/stream")
async def stream_reports(
    org_id: str = Header(alias="x-org-id"),
    project_id: str = Header(alias="x-project-id"),
    cursor: str = Header(default=None, alias="last-event-id"),
):
    """
    SSE 스트림 엔드포인트
    
    불변 계약 #1: UI 갱신의 단일 소스
    - snapshot: 초기 상태
    - report: 상태 변경 이벤트
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        # 1. Snapshot 전송 (초기 상태)
        snapshot = await get_current_state(org_id, project_id)
        yield format_sse_event("snapshot", snapshot)
        
        # 2. Report 스트림 (Redis Pub/Sub 또는 Queue)
        async for report in subscribe_reports(org_id, project_id, cursor):
            yield format_sse_event("report", report, report.get("report_id"))
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # nginx buffering 방지
        }
    )

def format_sse_event(event_type: str, data: dict, event_id: str = None) -> str:
    """
    SSE 이벤트 포맷
    
    event: <event_type>
    id: <event_id>
    data: <json_data>
    
    """
    lines = []
    
    if event_id:
        lines.append(f"id: {event_id}\n")
    
    lines.append(f"event: {event_type}\n")
    lines.append(f"data: {json.dumps(data)}\n\n")
    
    return "".join(lines)

async def get_current_state(org_id: str, project_id: str) -> dict:
    """
    현재 상태 스냅샷 생성
    """
    return {
        "autopilot": {"status": "idle"},
        "worklog": [],
        "asks": [],
        "memory": {},
        "sidecar": {},
        "org_id": org_id,
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat()
    }

async def subscribe_reports(org_id: str, project_id: str, cursor: str):
    """
    Report 스트림 구독
    
    Redis Pub/Sub 또는 내부 Queue 사용
    cursor: Last-Event-ID (리플레이용)
    """
    # TODO: Redis Pub/Sub 구현
    # 또는 shared/stream_store.py 사용
    
    # 임시 구현 (예시)
    channel = f"reports:{org_id}:{project_id}"
    
    async with redis_pubsub(channel) as pubsub:
        async for message in pubsub:
            report = json.loads(message)
            yield report
```

### 검증 방법
```bash
# SSE 스트림 연결
curl -N http://localhost:8000/agent/reports/stream \
  -H "x-org-id: default" \
  -H "x-project-id: nexus"

# 예상 출력
# event: snapshot
# data: {"autopilot":{"status":"idle"},...}
#
# event: report
# id: report-001
# data: {"report_type":"...","correlation_id":"..."}
```

### 브라우저 테스트
```javascript
const sse = new EventSource('/agent/reports/stream');

sse.addEventListener('snapshot', (event) => {
    console.log('Snapshot:', JSON.parse(event.data));
});

sse.addEventListener('report', (event) => {
    console.log('Report:', JSON.parse(event.data));
});
```

---

## 🎯 PR-005: correlation_id 전파

### 목표
요청→큐→워커→report까지 correlation_id 일관 전파

### 배경
correlation_id는 비동기 작업 추적의 핵심

### Definition of Done
- [ ] 모든 엔드포인트에서 correlation_id 수신
- [ ] 큐 메시지에 correlation_id 포함
- [ ] 워커에서 correlation_id 추출
- [ ] Report에 correlation_id 포함
- [ ] smoke test 통과

### 구현 지시

#### 파일 1: `shared/mq_utils.py`

```python
async def enqueue_task(
    task_type: str,
    params: dict,
    correlation_id: str,  # ✅ 추가
    org_id: str,
    project_id: str
):
    """
    Task를 큐에 넣기
    """
    message = {
        "task_id": generate_task_id(),
        "task_type": task_type,
        "params": params,
        "correlation_id": correlation_id,  # ✅ 전파
        "org_id": org_id,
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await publish_to_queue("nexus.tasks", message)
```

#### 파일 2: `agents/student/excel_kakao.py`

```python
async def process_task(message: dict):
    """
    Worker에서 Task 처리
    """
    task_id = message["task_id"]
    task_type = message["task_type"]
    params = message["params"]
    correlation_id = message.get("correlation_id")  # ✅ 추출
    org_id = message["org_id"]
    project_id = message["project_id"]
    
    # 작업 수행
    result = await do_work(params)
    
    # Report 전송
    await send_report({
        "report_id": generate_report_id(),
        "report_type": "task_completed",
        "correlation_id": correlation_id,  # ✅ 전파
        "task_id": task_id,
        "payload": result,
        "timestamp": datetime.utcnow().isoformat()
    }, org_id, project_id)
```

### 검증 방법
```bash
# 1. 요청 전송
CORRELATION_ID="test-$(date +%s)"
curl -X POST http://localhost:8000/sidecar/command \
  -H "Content-Type: application/json" \
  -H "x-org-id: default" \
  -H "x-project-id: nexus" \
  -H "x-api-key: dev-key" \
  -d "{\"command_type\":\"echo.test\",\"params\":{},\"correlation_id\":\"$CORRELATION_ID\"}"

# 2. SSE에서 correlation_id 확인
# event: report
# data: {"correlation_id":"test-1234567890",...}
```

---

## 🎯 PR-006: Two-Phase Commit 구현

### 목표
RED 작업에 대한 승인 프로세스 구현

### 배경
**불변 계약 #3**: RED 작업은 승인 없이 실행 불가

### Definition of Done
- [ ] 위험도(GREEN/YELLOW/RED) 분류
- [ ] RED 작업 시 Ask 생성
- [ ] 승인 전까지 실행 보류
- [ ] 승인 후 실행 및 Report 전송
- [ ] smoke test 통과

### 구현 지시

#### 파일 1: `shared/risk_policy.py` (신규)

```python
from enum import Enum

class RiskLevel(str, Enum):
    GREEN = "GREEN"  # 자동 실행
    YELLOW = "YELLOW"  # 경고만
    RED = "RED"  # 승인 필수

def get_risk_level(command_type: str) -> RiskLevel:
    """
    커맨드 타입별 위험도 반환
    """
    RED_COMMANDS = [
        "external_share.prepare",
        "email.send",
        "payment.execute",
    ]
    
    YELLOW_COMMANDS = [
        "file.delete",
        "data.export",
    ]
    
    if command_type in RED_COMMANDS:
        return RiskLevel.RED
    elif command_type in YELLOW_COMMANDS:
        return RiskLevel.YELLOW
    else:
        return RiskLevel.GREEN
```

#### 파일 2: `nexus_supervisor/services/approval_service.py` (신규)

```python
from uuid import uuid4

async def create_ask(
    command_id: str,
    command_type: str,
    description: str,
    correlation_id: str,
    org_id: str,
    project_id: str
) -> str:
    """
    Ask(승인 요청) 생성
    """
    ask_id = f"ask-{uuid4()}"
    
    ask = {
        "ask_id": ask_id,
        "command_id": command_id,
        "command_type": command_type,
        "description": description,
        "correlation_id": correlation_id,
        "risk_level": "RED",
        "options": ["approve", "deny"],
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Redis에 저장
    await redis.hset(f"asks:{org_id}:{project_id}", ask_id, json.dumps(ask))
    
    # SSE로 전송
    await send_report({
        "report_type": "ask_created",
        "correlation_id": correlation_id,
        "payload": ask
    }, org_id, project_id)
    
    return ask_id

async def process_approval(
    ask_id: str,
    decision: str,
    org_id: str,
    project_id: str
):
    """
    승인/거부 처리
    """
    # Ask 조회
    ask_json = await redis.hget(f"asks:{org_id}:{project_id}", ask_id)
    ask = json.loads(ask_json)
    
    if decision == "approve":
        # ✅ 승인 후 실행
        result = await execute_pending_command(ask["command_id"])
        
        # Report 전송
        await send_report({
            "report_type": "ask_resolved",
            "correlation_id": ask["correlation_id"],
            "payload": {
                "ask_id": ask_id,
                "decision": "approved",
                "result": result
            }
        }, org_id, project_id)
    else:
        # ❌ 거부
        await send_report({
            "report_type": "ask_resolved",
            "correlation_id": ask["correlation_id"],
            "payload": {
                "ask_id": ask_id,
                "decision": "denied"
            }
        }, org_id, project_id)
    
    # Ask 제거
    await redis.hdel(f"asks:{org_id}:{project_id}", ask_id)
```

### 검증 방법
```bash
# 1. RED 작업 요청
curl -X POST http://localhost:8000/sidecar/command \
  -H "Content-Type: application/json" \
  -H "x-org-id: default" \
  -H "x-project-id: nexus" \
  -H "x-api-key: dev-key" \
  -d '{
    "command_type": "external_share.prepare",
    "params": {"recipient": "test@example.com"},
    "correlation_id": "red-test-001"
  }'

# 2. SSE에서 ask_created 확인
# event: report
# data: {"report_type":"ask_created","payload":{"ask_id":"ask-...","risk_level":"RED"}}

# 3. 승인
ASK_ID="ask-..."  # 위에서 받은 ID
curl -X POST http://localhost:8000/approvals/$ASK_ID/decide \
  -H "Content-Type: application/json" \
  -H "x-org-id: default" \
  -H "x-project-id: nexus" \
  -H "x-api-key: dev-key" \
  -d '{"decision":"approve","reason":"Test"}'

# 4. SSE에서 ask_resolved 확인
# event: report
# data: {"report_type":"ask_resolved","payload":{"decision":"approved"}}
```

---

## 📊 전체 PR 체크리스트

### Phase 1: 환경 설정
- [ ] PR-001: Docker Compose 설정 수정 (healthcheck, depends_on)
- [ ] PR-002: 환경 변수 템플릿 정리

### Phase 2: 불변 계약 준수
- [ ] PR-003: 202 Accepted 패턴 적용
- [ ] PR-004: SSE 스트림 구현
- [ ] PR-005: correlation_id 전파
- [ ] PR-006: Two-Phase Commit 구현

### Phase 3: 안정성 개선 (선택)
- [ ] PR-007: 오류 처리 강화
- [ ] PR-008: 로깅 및 모니터링
- [ ] PR-009: SSE 재연결 로직

---

## 🎯 각 PR의 성공 기준

### 필수 조건
1. **코드 컴파일**: `python -m py_compile <파일>`
2. **Smoke Test**: `NEXUS_SMOKE_TEST_SCENARIOS.md` 해당 시나리오 통과
3. **불변 계약**: `NEXUS_WORK_CONTEXT.md` 계약 위반 없음
4. **로그 확인**: 오류 로그 없음

### 권장 사항
- 각 PR은 독립적으로 테스트 가능
- PR 크기는 500줄 이내 유지
- 변경 사항은 diff로 명확히 표시
- 커밋 메시지에 "불변 계약 #N 준수" 명시

---

**작성자**: Claude Code Agent  
**최종 검토**: 2026-02-03  
**대상 AI**: Claude Sonnet 4.5  
**참조**: 
- `NEXUS_WORK_CONTEXT.md` (불변 계약)
- `NEXUS_EXECUTION_CHECKLIST.md` (실행 방법)
- `NEXUS_SMOKE_TEST_SCENARIOS.md` (테스트)
- `NEXUS_ERROR_FIXES.md` (오류 수정)
