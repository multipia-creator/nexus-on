# Claude Sonnet 4.5 작업 프롬프트 (v2) — Single-file Harness 기반 FullStack 연결

목표
- NEXUS UI v1.1(LOCKED) 계약(스트림 단일 소스, 202 Accepted, replay)대로 **프론트/백엔드가 자연스럽게 연결**되도록 실제 코드를 구현한다.
- 로컬에서 즉시 실행 가능한 “증거 코드”를 우선하고, 이후 모듈화/서비스 분리로 확장한다.

입력(참고 아티팩트)
- `NEXUS_FullStack_SingleFile_Demo_v1.zip` : 단일 파일(FastAPI)로 UI+API 동작을 검증한 harness.
- 기존 설계 문서: UI v1.1(LOCKED), /agent/reports/stream, /sidecar/command, approvals 계약.

성공 조건(반드시 만족)
1) **UI 갱신의 단일 소스**는 `/agent/reports/stream`의 `snapshot` 및 `report` 이벤트이다.
2) `/sidecar/command`, `/approvals/{ask_id}/decide`는 **202 Accepted만 반환**하고, 실제 상태 변화는 후속 `report`로만 확정한다.
3) SSE는 `Last-Event-ID` 또는 `cursor`로 **리플레이** 가능해야 한다(네트워크 단절 복구).
4) correlation_id가 요청→후속 report까지 **일관 전파**되어 UI가 버튼 잠금 해제/상태 전이를 매칭할 수 있다.

구현 지침(추천 아키텍처)
- 1단계(증거 코드):
  - Backend: FastAPI(또는 Node) + Postgres(권장) + event log 테이블(tenant_id, seq, type, payload).
  - Frontend: Next.js(권장) + client store(reducer) + **fetch 기반 SSE**(ReadableStream)로 헤더 첨부.
  - Live2D는 placeholder로 두고, Stage/Dock/Dashboard 레이아웃과 데이터 바인딩부터 완성.

- 2단계(분리):
  - UI ↔ BFF 분리 (BFF가 tenant 헤더/토큰 주입, SSE 프록시 담당)
  - Backend는 Agent 실행/Worklog/Approvals/Memory 커넥터를 실제로 연결

브라우저 SSE 주의점(중요)
- `EventSource`는 헤더를 설정할 수 없으므로 멀티테넌트( x-org-id / x-project-id )에서는 부적합.
- 따라서 **fetch + ReadableStream**으로 SSE를 파싱하여 헤더와 Last-Event-ID를 넣어라.
  - harness 안의 `header_capable_sse_snippet.js`를 참고.

테스트 시나리오(필수)
1) UI에서 SSE Connect → snapshot 수신 → 화면 초기 렌더
2) sidecar command 1회 호출 → 202 수락 → report 수신 → worklog/sidecar 카드 갱신
3) `external_share.prepare` 호출 → Ask(RED) 생성 → Autopilot blocked 전환
4) Approval approve → Ask 제거 → Autopilot idle 복귀
5) SSE 연결 강제 종료 후 재연결(Last-Event-ID) → 누락 report replay 확인

금지 사항
- 202 응답으로 UI 상태를 확정하면 안 된다(반드시 후속 report 기반).
- report 이벤트 순서가 tenant 내에서 역전되면 안 된다.

산출물
- 실행 가능한 코드(backend + frontend 또는 최소한 backend+bff+ui stub)
- DB migration/DDL
- e2e smoke script(가능하면)
- README(실행/테스트 절차)
