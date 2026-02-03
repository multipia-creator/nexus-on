# Agent Standard Contract v1.0

NEXUS는 Supervisor가 작업을 생성하고, Agent들이 메시지 큐(RabbitMQ)를 통해 작업을 소비·처리하며,
결과를 Supervisor로 콜백하는 구조를 기본으로 한다.

## 1. Message Envelope (Supervisor → Queue)
```json
{
  "task_id": "uuid",
  "task_type": "excel_kakao",
  "requested_by": "user_id_or_role",
  "requested_at": "2026-01-31T12:34:56Z",
  "idempotency_key": "string (optional)",
  "payload": { "..." : "task specific" }
}
```

필수 규칙
- `task_id`는 Supervisor가 생성(권장: UUIDv4)하며 전 구간 추적 키로 사용한다.
- `task_type`은 enum으로 관리한다(예: excel_kakao, paper_crawl, meeting_forward ...).
- `payload`는 task_type 별 JSON schema로 고정한다.
- Agent는 **at-least-once** 소비를 기본 가정한다(중복 처리 가능).
- 중복 방지 필요 시 `idempotency_key`를 사용한다(Agent는 결과 캐시 or Supervisor 조회로 보정).

## 2. Result Callback (Agent → Supervisor)
Agent는 처리 결과를 Supervisor의 콜백 엔드포인트로 전달한다.

```json
{
  "task_id": "uuid",
  "status": "succeeded | failed",
  "finished_at": "2026-01-31T12:35:30Z",
  "result": { "..." : "task output" },
  "error": {
    "code": "STRING_ENUM",
    "message": "human readable",
    "detail": { "..." : "optional debug context" }
  },
  "metrics": {
    "duration_ms": 1234,
    "retries": 0
  }
}
```

## 3. Status Model (Supervisor)
Supervisor는 아래 상태를 최소 지원한다.
- queued: 큐에 투입됨
- running: worker가 수신하여 처리 중
- succeeded: 성공
- failed: 실패(에러 코드 포함)

## 4. Failure Semantics (표준)
에러 코드는 task_type 별로 추가하되, 공통 prefix를 권장한다.

공통 예시
- VALIDATION_ERROR: 입력 스키마 위반
- AUTH_ERROR: 외부 API 인증 실패
- RATE_LIMIT: 외부 API 레이트리밋
- TEMPORARY_UPSTREAM: 일시 장애(재시도 가능)
- PERMANENT_UPSTREAM: 영구 장애(재시도 무의미)
- INTERNAL_ERROR: 처리 로직 예외

## 5. Retry / DLQ (권장 기본값)
- retry: 3회 (exponential backoff: 1s, 3s, 10s)
- 실패가 지속되면 DLQ로 이동하고 Supervisor에는 failed로 보고한다.
- poison message는 DLQ로 강제 이동하고 알림 트리거를 발생시킨다(후속 단계).

## 6. Logging & Audit (최소)
Supervisor는 모든 task 생성 시 아래 필드를 감사로그로 남긴다.
- task_id, task_type, requested_by, requested_at, client_ip, payload_hash(민감정보 제외)
Agent는 처리 시 아래를 남긴다.
- task_id, status, duration_ms, error_code(있다면)

민감정보(전화번호/메일/토큰)는 반드시 마스킹한다.
