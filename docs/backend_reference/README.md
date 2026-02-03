# NEXUS (Local Always-on Assistant) — P0 Fullstack

이 패키지는 로컬 PC에 상주하는 **캐릭터 비서 UI + 자율 에이전트** 데모(P0)입니다.

- UI: `http://localhost:8000/ui`
- Backend: FastAPI + SSE + Approvals + Sidecar Commands
- LLM: Claude Sonnet 4.5(Anthropic) 포함 멀티 게이트웨이
- YouTube: 검색 + 큐 + 재생
- RAG: `/data/gdrive_mirror` 폴더 ingest + HWP 외부 변환 계약

## Quickstart
1) `.env.example` → `.env` 복사 후 키 설정
2) 실행:
   - macOS/Linux: `bash scripts/bootstrap_local.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File scripts\bootstrap_local.ps1`
3) 문서: `docs/RUNBOOK_LOCALSERVER_CLAUDE45.md`

## Claude Code 작업 규칙
- `CLAUDE.md`를 먼저 읽고, 변경 시 업데이트하세요.
