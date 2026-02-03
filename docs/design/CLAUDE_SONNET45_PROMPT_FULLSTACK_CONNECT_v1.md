# Claude Sonnet 4.5 코딩 프롬프트(FullStack 연결 구현)

목표
- UI(v1.1 LOCKED) 계약을 **변경하지 말고**, Backend(v7.3 코어) 위에 **Console/BFF API**를 추가하여 실제로 UI가 붙도록 만든다.
- UI 상태 단일 소스는 **SSE `/agent/reports/stream`** 이다. REST는 모두 202 Accepted(수락 확인)만, 확정은 stream의 후속 report로만 한다.

입력(레포 구조 가정)
- 기존 코어: `_nexus_v7_3_key03_backend/` (FastAPI 기반)
- 신규 BFF 서비스는 같은 레포 안에 `console_api/` (또는 `nexus_console_api/`)로 추가한다.

절대 규칙(LOCKED)
1) UI 상태 갱신 단일 소스: `GET /agent/reports/stream` (SSE)
2) `POST /sidecar/command` 는 202만 반환. 결과 확정은 후속 report 이벤트로만.
3) `POST /approvals/{ask_id}/decide` 도 202만 반환. 결과 확정은 후속 report 이벤트로만.
4) correlation_id 전파: request의 correlation_id가 후속 report(causality.correlation_id)에 포함되어야 함.
5) tenant ordered + at-least-once. 클라이언트는 report_id로 dedupe.

---

## 1) 구현할 엔드포인트(최소)

A. SSE
- `GET /agent/reports/stream`
  - Response: `text/event-stream`
  - 첫 이벤트: `event: snapshot` + `{ snapshot: {...}, report_id: <seq>, tenant, ts }`
  - 이후: `event: report` + `{ report: AgentReport, report_id: <seq>, causality, tenant, ts }`
  - heartbeat: `event: ping`
  - error: `event: error` + 표준 에러 payload
  - 복구: `Last-Event-ID` 헤더(또는 `?cursor=`) 지원

B. Command
- `POST /sidecar/command` → 202
  - req: `{ command_id, type, context{ref,title}, params, client_context{surface:"sidecar",correlation_id} }`
  - resp: `{ accepted:true, command_id, first_followup_report_id?:string, correlation_id }`
  - 동작: command를 큐에 enqueue → 실행 → AgentReport 발행

C. Approvals
- `POST /approvals/{ask_id}/decide` → 202
  - req: `{ decision:"approve"|"reject", correlation_id, note? }`
  - resp: `{ accepted:true, first_followup_report_id?:string, correlation_id }`
  - 동작: Ask 상태 변경(수락) → 필요한 실행 enqueue → AgentReport 발행

D. (옵션/초기 최소) Settings/Profile
- `PATCH /profile`, `POST /profile/photo`
- `PATCH /assistant/persona`, `PATCH /assistant/skin`
- `PATCH /compliance/settings`

---

## 2) 데이터 모델(최소) + 저장소

권장: Postgres(영속) + Redis(optional queue)

1) EventLog (SSE 소스)
- 테이블: `agent_report_events`
  - `id BIGSERIAL` (report_id)
  - `tenant_org TEXT`, `tenant_project TEXT`
  - `event_type TEXT` (snapshot|report|ping|error)
  - `payload JSONB`
  - `created_at TIMESTAMPTZ`
  - 인덱스: `(tenant_org, tenant_project, id)`

2) Ask/Approval
- 테이블: `asks`
  - `ask_id UUID PK`
  - `risk_level ENUM(GREEN,YELLOW,RED)`
  - `status ENUM(open, decided, executing, done, failed)`
  - `payload JSONB` (external_share 준비정보 등)
  - `created_at/updated_at`

3) Command
- 테이블: `sidecar_commands`
  - `command_id UUID PK`
  - `type TEXT`
  - `status ENUM(accepted,running,done,failed)`
  - `correlation_id TEXT`
  - `payload JSONB`

---

## 3) 실행 파이프라인(Perceive-Plan-Execute-Report 최소)

- `POST /sidecar/command` 수락 → `command_worker`가 실행
  - `draft_email.create`: 코어 `/llm/generate` 호출(또는 내부 함수) → 초안 생성 → report 발행
  - `prep_pack.create`: params 기반 체크리스트/요약 생성 → report 발행
  - `doc.summary.create`: 문서 텍스트 입력을 받아 요약 → report 발행
  - `calendar.options.create`: 후보 3개 생성(충돌 계산은 stub 가능) → report 발행
  - `external_share.prepare`: RED ask 생성 + report(ask) 발행

- `POST /approvals/{ask_id}/decide` 수락 → `approval_worker`가 실행
  - approve: 실행 단계 진행(최초는 stub로 “executed” 처리 가능) → report(done) 발행
  - reject: 취소 report 발행

주의
- UI 확정은 오직 report 이벤트로만. REST 응답은 절대로 “완료” 의미를 가지면 안 됨.

---

## 4) 멀티테넌트/인증 정리(최소)

- 모든 요청은 아래 중 1안으로 tenant를 결정한다.
  - 1안(권장): JWT에 `org_id`, `project_id` claim 포함
  - 2안(호환): 헤더 `x-org-id`, `x-project-id`를 필수로 강제
- 이 구현에서는 2안을 우선 적용하고(기존 E2E 스크립트 호환), JWT claim 방식은 추후 확장.

---

## 5) 테스트(필수)

1) SSE
- snapshot 1회 이후 report 순서 보장
- Last-Event-ID 재연결 시 누락 이벤트 리플레이
- tenant 분리(다른 tenant 이벤트 섞이지 않음)

2) correlation_id
- command/approval 요청의 correlation_id가 후속 report payload(causality.correlation_id)에 포함

3) UI fixtures 호환
- UI zip의 fixtures(JSON) 1~2개를 서버가 발행하는 payload와 형태가 최대한 일치하도록 맞춘다.

---

## 6) 산출물

- 신규 서비스 코드: `console_api/` (FastAPI)
- 마이그레이션: Alembic 또는 간단 SQL
- docker-compose: postgres + console_api + (optional) redis
- 문서: `console_api/README.md` (로컬 실행, curl 예제)

---

## 7) 시작을 위한 구체 작업 지시(Claude에게)

1) `console_api` FastAPI 앱 생성
2) 위 엔드포인트 3개(SSE/command/approvals)부터 구현
3) EventLog 저장/조회 + SSE 구현
4) Command worker(간단한 in-process background task로 시작 가능) 구현
5) `/llm/generate` 연동은 HTTP 호출로 연결(코어가 동일 레포면 import로 연결 가능)
6) 최소 통합 테스트 작성(pytest)

반드시 지켜야 할 것
- UI 계약(경로/202 semantics/stream-only confirmation)을 변경하지 말 것
- stream payload에 `report_id`(seq)와 `causality.correlation_id`를 넣을 것

