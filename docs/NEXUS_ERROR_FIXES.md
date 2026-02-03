# NEXUS 오류 가능 지점 및 수정 가이드

**작성일**: 2026-02-03  
**목적**: 로컬 실행 시 발생 가능한 오류와 수정 방법

---

## 🔍 오류 분류

### 카테고리
1. **환경 설정 오류** - .env, Docker 설정
2. **네트워크 오류** - 포트 충돌, 연결 실패
3. **계약 위반 오류** - 불변 계약 위반
4. **LLM 오류** - API 키, 쿼터 초과
5. **데이터 오류** - Redis, RabbitMQ

---

## 🚨 오류 1: 포트 충돌

### 증상
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

### 원인
8000, 5672, 15672, 6379 포트가 이미 사용 중

### 진단
```bash
# Windows
netstat -ano | findstr "8000"

# macOS/Linux
lsof -ti:8000
```

### 수정 방법

#### 옵션 A: 프로세스 종료
```bash
# Windows
netstat -ano | findstr "8000"
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

#### 옵션 B: Docker Compose 포트 변경

**파일**: `docker/docker-compose.nexus.yml`

```diff
services:
  nexus-supervisor:
    ports:
-     - "8000:8000"
+     - "8001:8000"  # 외부 포트를 8001로 변경
```

**적용**:
```bash
docker compose -f docker/docker-compose.nexus.yml up --build
```

**접속**: http://localhost:8001/ui

---

## 🚨 오류 2: HTTP 200 대신 202를 반환해야 함 (계약 위반)

### 증상
```bash
curl -X POST http://localhost:8000/sidecar/command ...
# HTTP 200 OK 반환
```

### 원인
`/sidecar/command`가 동기적으로 처리되어 200 반환

### 계약 위반
**불변 계약 #2**: `/approvals/*`, `/sidecar/command`는 **202 Accepted만** 반환

### 수정 Diff

**파일**: `nexus_supervisor/routers/sidecar.py`

```diff
@router.post("/command")
async def sidecar_command(
    command: SidecarCommand,
    org_id: str = Header(alias="x-org-id"),
    project_id: str = Header(alias="x-project-id"),
):
    # 작업을 큐에 넣기
    await enqueue_task(command)
    
    # ❌ 잘못된 응답
-   return {"status": "ok", "result": result}
    
    # ✅ 올바른 응답 (202 Accepted)
+   return JSONResponse(
+       status_code=202,
+       content={"status": "accepted", "correlation_id": command.correlation_id}
+   )
```

**확인**:
```bash
curl -I -X POST http://localhost:8000/sidecar/command ...
# HTTP/1.1 202 Accepted
```

---

## 🚨 오류 3: SSE 스트림 없이 직접 UI 업데이트 (계약 위반)

### 증상
UI가 API 응답으로 직접 업데이트됨 (SSE report 없이)

### 원인
프론트엔드가 API 응답 body를 직접 사용

### 계약 위반
**불변 계약 #1**: UI 갱신의 단일 소스는 `/agent/reports/stream` (SSE)

### 수정 Diff

**파일**: `templates/ui.html` 또는 `public/app.js`

```diff
// ❌ 잘못된 구현
async function sendCommand(command) {
    const response = await fetch('/sidecar/command', {
        method: 'POST',
        body: JSON.stringify(command)
    });
    const data = await response.json();
    
-   // 응답으로 직접 UI 업데이트 (금지!)
-   updateUI(data.result);
}

// ✅ 올바른 구현
async function sendCommand(command) {
    // 1. 요청만 전송 (202 Accepted)
    const response = await fetch('/sidecar/command', {
        method: 'POST',
        body: JSON.stringify(command)
    });
    
+   if (response.status !== 202) {
+       console.error('Expected 202 Accepted');
+       return;
+   }
    
    const data = await response.json();
    
+   // 2. correlation_id로 tracking만 (UI 업데이트는 SSE에서)
+   trackRequest(data.correlation_id);
    
-   // UI 업데이트 제거
-   updateUI(data.result);
}

// SSE 이벤트 핸들러에서만 UI 업데이트
sseSource.addEventListener('report', (event) => {
    const report = JSON.parse(event.data);
+   updateUI(report);  // ✅ SSE로만 UI 업데이트
});
```

---

## 🚨 오류 4: LLM API 키 없음

### 증상
```
RuntimeError: LLM_REQUIRED=true but no provider configured
```

### 원인
`.env` 파일에 LLM API 키 미설정

### 진단
```bash
grep -E "ANTHROPIC_API_KEY|OPENAI_API_KEY|GEMINI_API_KEY" .env
# 모두 비어있거나 "YOUR_KEY_HERE" 상태
```

### 수정 방법

#### 옵션 A: API 키 설정 (권장)

**파일**: `.env`

```bash
# 최소 1개 설정 필요
LLM_PRIMARY_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-실제키입력
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
LLM_REQUIRED=true
```

**재시작**:
```bash
docker compose -f docker/docker-compose.nexus.yml restart nexus-supervisor
```

#### 옵션 B: LLM 비활성화 (개발 전용)

**파일**: `.env`

```diff
- LLM_REQUIRED=true
+ LLM_REQUIRED=false
```

**주의**: LLM 기능이 비활성화되므로 제한적 테스트만 가능

---

## 🚨 오류 5: Redis 연결 실패

### 증상
```
redis.exceptions.ConnectionError: Error 111 connecting to redis:6379. Connection refused.
```

### 원인
Redis 컨테이너가 시작되지 않았거나 네트워크 문제

### 진단
```bash
docker compose -f docker/docker-compose.nexus.yml ps
# redis 컨테이너 상태 확인
```

### 수정 방법

#### 방법 A: 컨테이너 재시작
```bash
docker restart nexus-redis-1
# 또는
docker compose -f docker/docker-compose.nexus.yml restart redis
```

#### 방법 B: 완전 재빌드
```bash
docker compose -f docker/docker-compose.nexus.yml down
docker compose -f docker/docker-compose.nexus.yml up --build
```

#### 방법 C: Redis 연결 URL 확인

**파일**: `.env`

```bash
# 올바른 설정
REDIS_URL=redis://redis:6379/0

# ❌ 잘못된 예시
# REDIS_URL=redis://localhost:6379/0  # Docker 네트워크에서는 localhost 사용 불가
```

---

## 🚨 오류 6: RabbitMQ 연결 실패

### 증상
```
pika.exceptions.AMQPConnectionError: Connection to rabbitmq:5672 failed
```

### 원인
RabbitMQ가 준비되기 전에 Supervisor가 시작됨

### 진단
```bash
docker logs nexus-rabbitmq-1 | grep "Server startup complete"
# 위 메시지가 있어야 준비 완료
```

### 수정 방법

#### 방법 A: Supervisor 재시작 (대기 후)
```bash
# RabbitMQ 준비 대기 (약 10-15초)
docker logs -f nexus-rabbitmq-1

# "Server startup complete" 확인 후
docker restart nexus-supervisor-1
```

#### 방법 B: Docker Compose depends_on 추가

**파일**: `docker/docker-compose.nexus.yml`

```diff
services:
  nexus-supervisor:
    depends_on:
-     - redis
+     - redis
+     - rabbitmq
+   healthcheck:
+     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
+     interval: 10s
+     timeout: 5s
+     retries: 5

  rabbitmq:
+   healthcheck:
+     test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
+     interval: 10s
+     timeout: 5s
+     retries: 5
```

---

## 🚨 오류 7: SSE 연결 끊김 (브라우저)

### 증상
UI에서 "SSE connection lost" 메시지 또는 Network 탭에서 연결 중단

### 원인
1. 브라우저 EventSource 제한 (동시 연결 6개)
2. 네트워크 프록시/방화벽
3. Supervisor 재시작

### 진단
```javascript
// 브라우저 Console에서
sseSource.readyState
// 0: CONNECTING, 1: OPEN, 2: CLOSED
```

### 수정 방법

#### 방법 A: 자동 재연결 구현

**파일**: `public/app.js`

```diff
let sseSource;

function connectSSE() {
    sseSource = new EventSource('/agent/reports/stream');
    
    sseSource.onopen = () => {
        console.log('SSE connected');
    };
    
+   sseSource.onerror = (error) => {
+       console.error('SSE error, reconnecting...', error);
+       sseSource.close();
+       
+       // 5초 후 재연결
+       setTimeout(() => {
+           connectSSE();
+       }, 5000);
+   };
    
    sseSource.addEventListener('report', (event) => {
        // ...
    });
}

connectSSE();
```

#### 방법 B: Last-Event-ID 리플레이

```diff
function connectSSE(lastEventId) {
+   const url = lastEventId 
+       ? `/agent/reports/stream?cursor=${lastEventId}`
+       : '/agent/reports/stream';
        
-   sseSource = new EventSource('/agent/reports/stream');
+   sseSource = new EventSource(url);
}
```

---

## 🚨 오류 8: correlation_id 불일치

### 증상
요청한 `correlation_id`와 SSE report의 `correlation_id`가 다름

### 원인
백엔드에서 correlation_id를 전파하지 않음

### 계약 위반
correlation_id는 요청→report까지 일관 전파되어야 함

### 수정 Diff

**파일**: `shared/mq_utils.py`

```diff
async def enqueue_task(task: Task):
    message_body = {
        "task_id": task.task_id,
        "task_type": task.task_type,
        "params": task.params,
+       "correlation_id": task.correlation_id,  # ✅ 추가
        "org_id": task.org_id,
        "project_id": task.project_id,
    }
    
    await publish_message("nexus.tasks", message_body)
```

**파일**: `agents/student/excel_kakao.py`

```diff
async def process_task(message):
    task = parse_message(message)
    
    result = await do_work(task)
    
    # Report 전송
    report = {
        "report_type": "task_completed",
+       "correlation_id": task.get("correlation_id"),  # ✅ 전파
        "payload": result
    }
    
    await send_report(report)
```

---

## 🚨 오류 9: Ask가 자동 실행됨 (계약 위반)

### 증상
RED 작업이 승인 없이 바로 실행됨

### 원인
Two-Phase Commit 로직 누락

### 계약 위반
**불변 계약 #3**: RED 작업은 승인 없이 실행 불가

### 수정 Diff

**파일**: `nexus_supervisor/services/sidecar_service.py`

```diff
async def handle_external_share(command: SidecarCommand):
+   # ✅ 위험도 체크
+   if command.risk_level == "RED":
+       # Ask 생성
+       ask_id = await create_ask(
+           command_id=command.command_id,
+           description="외부 공유 승인 필요",
+           options=["approve", "deny"]
+       )
+       
+       # SSE로 Ask 전송
+       await send_report({
+           "report_type": "ask_created",
+           "correlation_id": command.correlation_id,
+           "payload": {"ask_id": ask_id, "risk_level": "RED"}
+       })
+       
+       # 승인 대기 (실행하지 않음!)
+       return {"status": "waiting_approval"}
    
-   # ❌ 바로 실행 (금지!)
-   result = await execute_share(command.params)
-   return result
```

**파일**: `nexus_supervisor/routers/approvals.py`

```diff
@router.post("/{ask_id}/decide")
async def decide_approval(ask_id: str, decision: ApprovalDecision):
    ask = await get_ask(ask_id)
    
    if decision.decision == "approve":
+       # ✅ 승인 후에만 실행
+       result = await execute_pending_task(ask.command_id)
        
+       # SSE로 완료 알림
+       await send_report({
+           "report_type": "ask_resolved",
+           "correlation_id": ask.correlation_id,
+           "payload": {"decision": "approved", "result": result}
+       })
    
-   return {"status": "ok", "result": result}  # ❌ 200 금지
+   return JSONResponse(status_code=202, content={"status": "accepted"})
```

---

## 🚨 오류 10: Docker 메모리 부족

### 증상
```
Container killed due to memory usage
```

### 원인
Docker Desktop에 할당된 메모리 부족

### 진단
```bash
docker stats
# MEM USAGE / LIMIT 확인
```

### 수정 방법

#### Windows/macOS: Docker Desktop 설정
1. Docker Desktop → Settings
2. Resources → Memory
3. 메모리를 최소 4GB로 증가
4. Apply & Restart

#### Linux: Docker Compose 메모리 제한
**파일**: `docker/docker-compose.nexus.yml`

```diff
services:
  nexus-supervisor:
+   mem_limit: 2g
+   mem_reservation: 1g
```

---

## 📊 오류 우선순위

### 즉시 수정 필요 (계약 위반)
1. **오류 2**: HTTP 200 대신 202 반환 - 불변 계약 #2 위반
2. **오류 3**: SSE 없이 직접 UI 업데이트 - 불변 계약 #1 위반
3. **오류 8**: correlation_id 불일치
4. **오류 9**: Ask 자동 실행 - 불변 계약 #3 위반

### 환경 설정 (실행 전 해결)
5. **오류 1**: 포트 충돌
6. **오류 4**: LLM API 키 없음
7. **오류 5**: Redis 연결 실패
8. **오류 6**: RabbitMQ 연결 실패

### 운영 안정성 (점진적 개선)
9. **오류 7**: SSE 연결 끊김
10. **오류 10**: Docker 메모리 부족

---

## 🔧 디버깅 도구

### 로그 확인
```bash
# 모든 컨테이너 로그
docker compose -f docker/docker-compose.nexus.yml logs -f

# 특정 컨테이너
docker logs -f nexus-supervisor-1
docker logs -f nexus-redis-1
docker logs -f nexus-rabbitmq-1
```

### 컨테이너 접속
```bash
# Supervisor 접속
docker exec -it nexus-supervisor-1 bash

# Redis 접속
docker exec -it nexus-redis-1 redis-cli

# RabbitMQ 접속
docker exec -it nexus-rabbitmq-1 bash
```

### 네트워크 확인
```bash
# 컨테이너 간 통신 테스트
docker exec nexus-supervisor-1 ping redis
docker exec nexus-supervisor-1 curl http://rabbitmq:15672
```

---

**작성자**: Claude Code Agent  
**최종 검토**: 2026-02-03  
**참조**: `NEXUS_WORK_CONTEXT.md` (불변 계약)
