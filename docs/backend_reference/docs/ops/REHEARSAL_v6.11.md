# 운영 리허설 자동 채점 (v6.11)

목적
- 리허설 실행 후, 로그/ledger 증적을 기반으로 스코어카드를 자동 생성한다.
- 운영팀은 MANUAL 항목(웹훅 수신, 크론, 장애-복구)만 추가로 체크하면 된다.

실행
- python tools/rehearsal_autoscore.py --topology "single+redis" --providers "gemini-first (openai/anthropic/glm optional)"

출력
- templates/REHEARSAL_SCORECARD_FILLED.md

자동 판정 근거(보수적)
- llm_success(최근 2시간) 존재 → LLM 호출 OK
- cost ledger 기록(최근 2시간) 존재 → FinOps 기록 OK
- llm_dedupe_hit(최근 4시간) 존재 → Dedupe OK
- ledger에 team/project가 default/nexus 외 값 존재(최근 4시간) → 태깅 분리 OK
