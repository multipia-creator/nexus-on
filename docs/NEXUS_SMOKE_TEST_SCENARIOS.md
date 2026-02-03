# NEXUS 스모크 테스트 시나리오

**작성일**: 2026-02-03  
**목적**: NEXUS 로컬 실행 환경의 핵심 기능 검증  
**소요 시간**: 약 15-20분

---

## 🎯 테스트 목표

NEXUS 시스템의 **불변 계약 5가지**를 검증:
1. SSE 스트림 = UI 갱신의 단일 소스
2. 202 Accepted 패턴
3. Two-Phase Commit (RED 작업)
4. 멀티테넌트 컨텍스트
5. RAG 로컬 미러 구조

---

## 📋 사전 조건

- [ ] NEXUS 실행 완료 (`NEXUS_EXECUTION_CHECKLIST.md` 완료)
- [ ] UI 접속 가능: http://localhost:8000/ui
- [ ] 브라우저 개발자 도구 열기 (F12)
  - Console 탭과 Network 탭 확인 준비

---

## 🧪 테스트 시나리오

### 시나리오 1: 헬스체크 및 기본 연결 (5분)

#### 1.1 API 헬스체크

**목적**: 모든 서비스가 정상 작동하는지 확인

**실행**:
```bash
curl http://localhost:8000/health
```

**예상 결과**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T...",
  "services": {
    "redis": "ok",
    "rabbitmq": "ok"
  }
}
```

**검증 포인트**:
- [ ] HTTP 200 응답
- [ ] `status: "healthy"`
- [ ] Redis, RabbitMQ 모두 `ok`

**실패 시 조치**:
```bash
# 컨테이너 상태 확인
docker compose -f docker/docker-compose.nexus.yml ps

# 로그 확인
docker compose -f docker/docker-compose.nexus.yml logs nexus-supervisor
```

---

#### 1.2 RabbitMQ 큐 확인

**목적**: 메시지 큐가 정상 생성되었는지 확인

**실행**:
1. 브라우저에서 http://localhost:15672 접속
2. Username: `guest`, Password: `guest`
3. Queues 탭 클릭

**예상 결과**:
- [ ] `nexus.tasks` 큐 존재
- [ ] `nexus.dlq` 큐 존재
- [ ] `nexus.retry.short` 큐 존재 (있는 경우)

**실패 시 조치**:
```bash
# RabbitMQ 재시작
docker restart nexus-rabbitmq-1
```

---

#### 1.3 Redis 연결 확인

**목적**: Redis 캐시가 정상 작동하는지 확인

**실행**:
```bash
docker exec -it nexus-redis-1 redis-cli ping
docker exec -it nexus-redis-1 redis-cli info server
```

**예상 결과**:
```
PONG
# Server
redis_version:7.x.x
...
```

**검증 포인트**:
- [ ] `PONG` 응답
- [ ] Redis 버전 정보 표시

---

### 시나리오 2: SSE 스트림 연결 (5분)

#### 2.1 UI SSE 연결 확인

**목적**: UI와 백엔드 간 SSE 스트림 연결 검증 (불변 계약 #1)

**실행**:
1. 브라우저에서 http://localhost:8000/ui 접속
2. F12 개발자 도구 → Network 탭
3. `stream` 항목 확인 (Type: eventsource)

**예상 결과**:
- [ ] Network 탭에 `/agent/reports/stream` 요청 존재
- [ ] Status: `200` (또는 `pending` 상태 유지)
- [ ] EventStream 타입

**Console에서 확인**:
```javascript
// Console에서 SSE 이벤트 수신 확인
// "SSE connected" 또는 유사한 로그 메시지
```

**검증 포인트**:
- [ ] SSE 연결 성공
- [ ] `snapshot` 이벤트 수신 (초기 상태)
- [ ] Console에 오류 없음

**실패 시 조치**:
```bash
# Supervisor 로그 확인
docker logs nexus-supervisor-1 | grep -i "sse\|stream"
```

---

#### 2.2 Snapshot 이벤트 검증

**목적**: 초기 상태 스냅샷 수신 확인

**실행**:
1. UI 로드 후 Console 확인
2. Network 탭 → `stream` → EventStream 탭

**예상 결과**:
```json
event: snapshot
data: {
  "autopilot": {"status": "idle", ...},
  "worklog": [...],
  "asks": [],
  "memory": {...},
  "sidecar": {...}
}
```

**검증 포인트**:
- [ ] `snapshot` 이벤트 수신
- [ ] `autopilot.status` 존재
- [ ] `worklog`, `asks` 배열 존재

---

### 시나리오 3: 202 Accepted 패턴 (5분)

#### 3.1 사이드카 명령 전송 (비동기)

**목적**: 202 Accepted 패턴 및 후속 SSE report 검증 (불변 계약 #2)

**실행**:
```bash
curl -X POST http://localhost:8000/sidecar/command \
  -H "Content-Type: application/json" \
  -H "x-org-id: default" \
  -H "x-project-id: nexus" \
  -H "x-api-key: dev-key-change-me-in-production" \
  -d '{
    "command_type": "echo.test",
    "params": {"message": "Hello NEXUS"},
    "correlation_id": "test-001"
  }'
```

**예상 결과**:
```json
{
  "status": "accepted",
  "correlation_id": "test-001"
}
```

**검증 포인트**:
- [ ] HTTP **202** 응답 (200이 아님!)
- [ ] `status: "accepted"`
- [ ] `correlation_id` 반환

**실패 시**:
- HTTP 200 반환 → ❌ 계약 위반! `NEXUS_ERROR_FIXES.md` 참조

---

#### 3.2 후속 SSE Report 확인

**목적**: 비동기 작업 결과가 SSE로만 전달되는지 확인

**실행**:
1. UI Console 또는 Network → EventStream 탭 확인
2. `report` 이벤트 대기 (수 초 내)

**예상 결과**:
```json
event: report
data: {
  "report_id": "...",
  "correlation_id": "test-001",
  "report_type": "sidecar_result",
  "timestamp": "...",
  "payload": {
    "status": "completed",
    "result": "..."
  }
}
```

**검증 포인트**:
- [ ] `report` 이벤트 수신
- [ ] `correlation_id` 일치 (`test-001`)
- [ ] `report_type: "sidecar_result"`
- [ ] UI가 자동 업데이트됨 (Worklog 또는 Sidecar 섹션)

**실패 시 조치**:
```bash
# Worker 로그 확인
docker logs nexus-student-worker-1 | tail -50
```

---

### 시나리오 4: LLM 통합 테스트 (5분)

#### 4.1 LLM 생성 요청

**목적**: 멀티 LLM 게이트웨이 정상 작동 확인

**실행**:
```bash
curl -X POST http://localhost:8000/llm/generate \
  -H "Content-Type: application/json" \
  -H "x-api-key: dev-key-change-me-in-production" \
  -d '{
    "prompt": "Say hello in Korean",
    "max_tokens": 100
  }'
```

**예상 결과**:
```json
{
  "text": "안녕하세요!",
  "provider": "anthropic",
  "model": "claude-sonnet-4-5-20250929",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```

**검증 포인트**:
- [ ] HTTP 200 응답
- [ ] `text` 필드에 한국어 응답
- [ ] `provider` 필드 존재 (anthropic/gemini/openai)
- [ ] `usage` 통계 존재

**실패 시 조치**:
```bash
# .env 파일에서 LLM 설정 확인
grep -E "LLM_PRIMARY_PROVIDER|ANTHROPIC_API_KEY|OPENAI_API_KEY" .env

# Supervisor 로그 확인
docker logs nexus-supervisor-1 | grep -i "llm\|provider"
```

---

#### 4.2 Fallback 체인 테스트 (선택)

**목적**: Primary provider 실패 시 fallback 작동 확인

**실행**:
1. .env에서 PRIMARY_PROVIDER 키를 잠시 제거 또는 잘못된 값으로 변경
2. 컨테이너 재시작
3. LLM 요청 재실행

**예상 결과**:
- [ ] 요청 성공 (fallback provider 사용)
- [ ] `provider` 필드가 fallback provider 이름

**원복**:
```bash
# .env 원복 후 재시작
docker compose -f docker/docker-compose.nexus.yml restart nexus-supervisor
```

---

### 시나리오 5: Two-Phase Commit (RED 작업) (선택, 10분)

#### 5.1 RED 작업 승인 요청

**목적**: Two-Phase Commit 흐름 검증 (불변 계약 #3)

**실행**:
```bash
curl -X POST http://localhost:8000/sidecar/command \
  -H "Content-Type: application/json" \
  -H "x-org-id: default" \
  -H "x-project-id: nexus" \
  -H "x-api-key: dev-key-change-me-in-production" \
  -d '{
    "command_type": "external_share.prepare",
    "params": {
      "recipient": "test@example.com",
      "content": "Test message"
    },
    "correlation_id": "red-test-001"
  }'
```

**예상 결과**:
```json
{
  "status": "accepted",
  "correlation_id": "red-test-001"
}
```

**검증 포인트**:
- [ ] HTTP 202 응답
- [ ] `status: "accepted"`

---

#### 5.2 Ask 생성 확인

**목적**: 승인 요청(Ask)이 생성되고 SSE로 전달되는지 확인

**실행**:
1. UI 확인 또는 Network → EventStream 탭
2. `report` 이벤트 대기

**예상 결과**:
```json
event: report
data: {
  "report_type": "ask_created",
  "correlation_id": "red-test-001",
  "payload": {
    "ask_id": "ask-...",
    "risk_level": "RED",
    "description": "외부 공유 승인 요청",
    "options": ["approve", "deny"]
  }
}
```

**검증 포인트**:
- [ ] `report_type: "ask_created"`
- [ ] `risk_level: "RED"`
- [ ] `ask_id` 생성됨
- [ ] UI의 Asks 섹션에 표시됨

---

#### 5.3 승인 처리

**목적**: 승인 후 실행 완료가 SSE로만 전달되는지 확인

**실행**:
```bash
ASK_ID="ask-..."  # 위에서 받은 ask_id

curl -X POST http://localhost:8000/approvals/$ASK_ID/decide \
  -H "Content-Type: application/json" \
  -H "x-org-id: default" \
  -H "x-project-id: nexus" \
  -H "x-api-key: dev-key-change-me-in-production" \
  -d '{
    "decision": "approve",
    "reason": "Test approval"
  }'
```

**예상 결과**:
```json
{
  "status": "accepted"
}
```

**검증 포인트**:
- [ ] HTTP 202 응답 (200이 아님!)
- [ ] `status: "accepted"`

---

#### 5.4 실행 완료 Report 확인

**실행**:
1. EventStream 또는 UI Console 확인
2. 후속 `report` 이벤트 대기

**예상 결과**:
```json
event: report
data: {
  "report_type": "ask_resolved",
  "correlation_id": "red-test-001",
  "payload": {
    "ask_id": "ask-...",
    "decision": "approved",
    "result": "completed"
  }
}
```

**검증 포인트**:
- [ ] `report_type: "ask_resolved"`
- [ ] `decision: "approved"`
- [ ] UI의 Asks 섹션에서 제거됨
- [ ] Worklog에 결과 기록됨

---

### 시나리오 6: 멀티테넌트 컨텍스트 (선택)

#### 6.1 다른 조직/프로젝트 요청

**목적**: 멀티테넌트 격리 확인 (불변 계약 #4)

**실행**:
```bash
# 조직 A
curl -X POST http://localhost:8000/sidecar/command \
  -H "x-org-id: org-a" \
  -H "x-project-id: project-1" \
  -H "x-api-key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"command_type": "echo.test", "params": {"msg": "Org A"}}'

# 조직 B
curl -X POST http://localhost:8000/sidecar/command \
  -H "x-org-id: org-b" \
  -H "x-project-id: project-2" \
  -H "x-api-key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"command_type": "echo.test", "params": {"msg": "Org B"}}'
```

**검증 포인트**:
- [ ] 각 요청이 독립적으로 처리됨
- [ ] SSE 스트림이 조직별로 분리됨 (다른 UI 세션에서 확인)

---

## 📊 테스트 결과 요약

### 성공 기준

모든 시나리오에서 다음을 확인:
- [ ] **시나리오 1**: 헬스체크 및 기본 연결 ✅
- [ ] **시나리오 2**: SSE 스트림 연결 ✅
- [ ] **시나리오 3**: 202 Accepted 패턴 ✅
- [ ] **시나리오 4**: LLM 통합 ✅
- [ ] **시나리오 5**: Two-Phase Commit ✅ (선택)
- [ ] **시나리오 6**: 멀티테넌트 ✅ (선택)

### 불변 계약 검증

- [ ] **계약 #1**: SSE 스트림 = UI 갱신의 단일 소스 ✅
  - 모든 상태 변경이 SSE report로만 전달됨
  
- [ ] **계약 #2**: 202 Accepted 패턴 ✅
  - `/sidecar/command`, `/approvals/*`가 202만 반환
  
- [ ] **계약 #3**: Two-Phase Commit ✅
  - RED 작업이 승인 없이 실행되지 않음
  
- [ ] **계약 #4**: 멀티테넌트 컨텍스트 ✅
  - `x-org-id`, `x-project-id` 헤더가 올바르게 작동
  
- [ ] **계약 #5**: RAG 로컬 미러 구조 ✅
  - (별도 RAG 테스트에서 검증)

---

## 🐛 실패 시 다음 단계

테스트 실패 시:
1. **로그 확인**: `docker compose logs -f`
2. **오류 수정 가이드**: `NEXUS_ERROR_FIXES.md` 참조
3. **재시작**: `docker compose down && docker compose up --build`

---

**작성자**: Claude Code Agent  
**최종 검토**: 2026-02-03  
**소요 시간**: 15-20분 (선택 시나리오 포함 시 30분)
