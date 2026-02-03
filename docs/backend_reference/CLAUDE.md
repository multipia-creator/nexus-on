# CLAUDE.md (NEXUS)

이 저장소는 **로컬 상주형(Always-on) 캐릭터 비서 + 자율 에이전트**를 목표로 하는 NEXUS P0 풀스택입니다.
Claude Sonnet 4.5(Anthropic)를 포함한 멀티 LLM 게이트웨이를 지원하며, UI는 SSE 스트림을 단일 소스로 사용합니다.

## 0) 불변 계약(절대 변경 금지)
1) UI 갱신의 단일 소스는 `/agent/reports/stream`(SSE)입니다.  
   - `/approvals/*`, `/sidecar/command`는 **202 Accepted**만 반환하며 UI 상태 전이는 반드시 SSE 후속 report로만 처리합니다.
2) RED(외부 공유/전송)는 Two-phase commit(승인 없이는 실행 불가)입니다.
3) 멀티테넌트 컨텍스트는 `x-org-id`, `x-project-id`로 분리하며, 키 주입/감사/비용 태깅은 tenant 범위로 적용합니다.
4) 위험도(GREEN/YELLOW/RED) 정책과 Ask/Approvals 흐름을 깨지 않습니다.
5) RAG(HWP 포함)는 **로컬 미러 폴더 → 인덱싱** 구조를 기본으로 하고, HWP는 외부 변환이 선행되어야 합니다.

## 1) 빠른 실행(로컬)
- `.env.example` → `.env`로 복사 후 키 설정
- `docker compose -f docker/docker-compose.nexus.yml up --build`
- 확인:
  - `GET http://localhost:8000/health`
  - `GET http://localhost:8000/ui` (단일 파일 UI)

## 2) Claude Sonnet 4.5 사용(LLM)
- `.env`에 다음을 설정:
  - `LLM_PRIMARY_PROVIDER=anthropic`
  - `ANTHROPIC_API_KEY=...`
  - `ANTHROPIC_MODEL=claude-sonnet-4-5-20250929`
- 실패 시 fallback은 `LLM_FALLBACK_PROVIDERS`로 제어합니다.

## 3) RAG(구글 드라이브) 운영 원칙
- 구글 드라이브 파일은 **로컬 폴더로 미러링**한 뒤, 컨테이너 `/data/gdrive_mirror`로 마운트하여 ingest 합니다.
- 자동 ingest 기본 시간: **03:00 KST**
- HWP는 외부 변환 후 같은 basename의 `.pdf` 또는 `.txt`를 sibling으로 두는 것을 권장합니다.

## 4) 병렬 개발 팁(Claude Code)
- 3~5개의 `git worktree`를 사용해 역할을 분리합니다.
  - `wt-ui`(UI), `wt-sse`(스트림/상태), `wt-rag`(ingest/검색), `wt-ops`(배포/관측)
- 복잡한 작업은 항상 **Plan Mode**로 시작하고, 구현 전 스펙(Definition of Done)을 고정합니다.
- 매 PR마다 이 문서를 업데이트하여 동일 실수를 반복하지 않도록 합니다.

## 5) 변경 시 반드시 통과해야 할 체크
- `python -m py_compile nexus_supervisor/app.py`
- `bash deploy/smoke_test.sh` (옵션)
- SSE 스트림에서 `report_id` dedupe / `correlation_id` 전파가 유지되는지 확인
