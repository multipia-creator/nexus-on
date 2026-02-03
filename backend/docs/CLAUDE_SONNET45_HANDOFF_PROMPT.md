# Claude Sonnet 4.5 핸드오프 프롬프트 (NEXUS)

아래 지침을 Claude Sonnet 4.5(Claude Code/Claude Desktop)에 그대로 붙여넣고,
이 저장소를 열어서 “로컬 실행 + 기능 검증 + 남은 TODO 정리”까지 한 번에 진행한다.

---

## 역할
너는 스태프 엔지니어로서, NEXUS 로컬 상주형 AI 비서 시스템을 P0 품질로 실행 가능하게 만들고,
테스트/운영 가이드를 갱신하며, 남은 결함을 계획(Plan) → 구현 → 검증까지 닫아야 한다.

## 절대 규칙(깨면 안 됨)
- UI 갱신 단일 소스는 SSE(`/agent/reports/stream`)이다. 202 Accepted 응답은 상태 전이의 근거가 아니다.
- RED 작업은 승인 없이는 절대 실행하지 않는다(Ask 생성 → 승인 → SSE 후속 report).
- 멀티테넌트 헤더 `x-org-id/x-project-id`를 흐트러뜨리지 않는다.
- HWP는 외부 변환이 선행되어야 한다(변환 없이 내부에서 억지 파싱 금지).

## 지금 해야 할 일(Plan Mode로 시작)
1) 로컬에서 `docker compose up --build`로 실행
2) `/health`, `/ui`, `/agent/reports/stream` 연결 확인
3) YouTube: 검색(키 유무에 따라 graceful) + 큐 + 재생 확인
4) RAG: `/data/gdrive_mirror`를 마운트한 상태에서 folder ingest 확인
5) HWP pending 처리 확인(변환 파일 sibling이 있으면 인덱싱되는지)
6) `deploy/smoke_test.sh`를 실제로 통과시키고, 실패 시 원인과 수정사항을 PR로 묶기
7) 완료 기준(Definition of Done)과 남은 TODO를 `docs/ROADMAP_WORLDCLASS.md`에 업데이트

## 결과물
- 실행 재현 가능: 문서만 보고 15분 내 실행 가능해야 함
- smoke test + 최소 E2E(YouTube/RAG/SSE) 체크리스트 통과
- 수정사항이 있다면 커밋 단위로 정리
