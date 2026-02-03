# 운영 리허설 체크리스트 (v6.10)

목적
- 배포 직전/직후에 "운영 루프"가 끝까지 닫히는지 확인한다.
- 확인 범위: LLM 호출 → 보호장치(백오프/브레이커/디듀프) → 관측(메트릭/로그) → 통지(Slack/Teams) → 리포트(집계).

준비물
- 실행 환경에 v6.10 코드 배포
- Prometheus 스크레이프(선택)
- Slack 또는 Teams Incoming Webhook 1개
- Redis(멀티노드면 권장/사실상 필수), 단일 노드면 파일 폴백도 가능

필수 환경변수(요약)
- Provider 키/URL: Gemini-first + 옵션(OpenAI/Claude/GLM) 구성에 맞게
- FinOps/Logs:
  - LLM_COST_LEDGER_PATH=logs/llm_cost_ledger.jsonl
  - LLM_AUDIT_LOG_PATH=logs/llm_audit.jsonl
- Notifications:
  - SLACK_WEBHOOK_URL=...
  - TEAMS_WEBHOOK_URL=...
  - NOTIFY_PREFER=slack|teams
- Tagging defaults:
  - LLM_DEFAULT_TEAM=default
  - LLM_DEFAULT_PROJECT=nexus
- Anomaly thresholds:
  - ANOMALY_WINDOW_MIN=15
  - ANOMALY_COST_USD_RATE_THRESHOLD=2.0
  - ANOMALY_429_BURST_THRESHOLD=20
  - ANOMALY_BREAKER_OPEN_MIN=5

실행(권장 순서)

A. 30분 스모크(최소 합격)
1) 기본 호출 + 로그/ledger 생성
- python tools/rehearsal_harness.py smoke --prompt "hello" --purpose ops
OK:
- logs/llm_audit.jsonl에 llm_success 1줄 이상
- logs/llm_cost_ledger.jsonl에 1줄 이상(actual_cost_usd > 0 or approx_tokens=true)
NG:
- 로그 파일이 생성되지 않음
- 예외로 종료

2) 리포트 생성
- python tools/rehearsal_harness.py report --from 2026-01-01 --to 2026-01-31 --out logs/finops_rehearsal.md
OK: out 파일 생성, total cost 표시
NG: out 파일 미생성 또는 파싱 실패

3) 알림 배선(드라이런 → 실발송)
- python tools/rehearsal_harness.py anomaly --dry-run
OK: 종료코드 0
- (실발송) 임계값을 낮춰 cost spike 알림 1회 발생 확인
NG: 웹훅 오류(401/404) 또는 타임아웃

B. 2시간 리허설(운영 합격)
4) Dedupe 효과 확인
- python tools/rehearsal_harness.py dedupe --prompt "same prompt" --n 5 --purpose ops
OK:
- llm_dedupe_hit 로그/메트릭 증가
NG:
- 매번 provider 호출로 비용 누적(디듀프 TTL/키/목적/태그를 점검)

5) 태깅(team/project) 분리 확인
- python tools/rehearsal_harness.py tagging --prompt "tag test" --team ops --project finops --purpose ops
OK: ledger에 team/project 기록, 비용 메트릭 라벨 분리
NG: team/project가 default만 찍힘(환경변수/컨텍스트 전달 점검)

6) 부하(저강도) 테스트
- python tools/rehearsal_load_test.py --prompt "ping" --n 50 --concurrency 5 --purpose ops --team ops --project rehearsal
OK: p95가 폭주하지 않음(환경 기준), fail율 0~소수
NG: fail율 상승(429/timeout), 백오프/쿨다운 동작 점검

C. 1일 리허설(출시 합격)
7) 크론 스케줄러 적용(예시)
- anomaly watch: */5 * * * *
- monthly report: 0 9 1 * *
OK: 알림/리포트 누락 없음
NG: 로그/경로/권한 문제로 누락

8) 장애–복구 라운드트립
- 의도적 장애(키 오류/네트워크 차단) → breaker/알림
- 복구 → 정상화 확인
OK: 5분 내 원인 파악 + 조치 가능, 알림 과다 발송 없음
NG: 중복 알림 폭탄/복구 후에도 breaker open 지속

결과 기록
- templates/REHEARSAL_SCORECARD.md 양식으로 결과를 남긴다.


## v6.11 자동 채점(스코어카드 자동 생성)
- 실행:
  python tools/rehearsal_autoscore.py --topology "single+redis" --providers "gemini-first (openai/anthropic/glm optional)"
- 산출물:
  templates/REHEARSAL_SCORECARD_FILLED.md
- 자동 판정 범위:
  - 최근 2~4시간 로그 기반으로: llm_success, ledger 기록, llm_dedupe_hit, 태깅(team/project) 확인
  - 웹훅 수신/크론/장애 유도 등은 MANUAL로 남김(환경 의존)
