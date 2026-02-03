# NEXUS v2.1 “World-Best” 실행 베이스 (Gemini First + OpenAI Optional)

목표: **실제로 운영 가능한 수준**으로 끌어올린 v1.9. (v1.8 대비: 상태저장/재시도/DLQ/관측성/보안 강화)

핵심 원칙
- Gemini 기본, OpenAI 옵션(런타임 스위치)
- Agent 표준 계약 준수(Envelope/Callback/Status/Error)
- 실패는 “조용히”가 아니라 “관측 가능하게” 처리(메트릭/로그/재시도/DLQ)
- 키/PII는 로그로 흘리지 않음(마스킹 + 감사로그)

## What’s new (v1.8 → v1.9)
1) **Task Store: Redis 도입**
   - in-memory 제거 → 재시작/스케일아웃 내성 확보
   - `TASK_TTL_SECONDS` 기본 7일(설정 가능)

2) **Retry + DLQ(Dead Letter Queue) 표준 적용**
   - 실패 시: 5s → 30s → 5m 재시도(총 3회) 후 DLQ 이동
   - retry_count, last_error를 task state에 누적
   - DLQ에 떨어진 메시지는 운영자가 재처리/분석 가능

3) **관측성(Observability)**
   - Supervisor: Prometheus `/metrics` 제공
   - 핵심 카운터/히스토그램: task_create, task_status, callback, llm_generate, agent_fail, retries, dlq

4) **보안/무결성**
   - `X-API-Key` 기본 인증 유지
   - (옵션) Agent→Supervisor 콜백 HMAC 서명: `CALLBACK_SIGNATURE_SECRET`
   - 키/토큰 마스킹, 전화/메일 마스킹

5) **운영 설정 강화**
   - Pydantic Settings로 설정 검증
   - `LLM_REQUIRED=true`이면 키 미설정 시 요청 실패(운영 권장)
   - JSON 구조 로그(파싱/적재 용이)

## 빠른 실행
```bash
cp .env.example .env
# 운영 권장: GEMINI_API_KEY 설정, LLM_REQUIRED=true
bash deploy/nexus_deploy.sh
bash deploy/smoke_test.sh
```

### 접속
- Supervisor: http://localhost:8000/docs
- Metrics:   http://localhost:8000/metrics
- RabbitMQ:  http://localhost:15672 (guest/guest)
- Redis:     내부 사용(포트 6379 노출 옵션)

## 평가(자체 품질 게이트 v1.0)
- [x] 재시작 내성(상태 저장) — Redis
- [x] 실패 처리(재시도/백오프/DLQ) — 3단 retry + DLQ
- [x] 관측성 — Prometheus metrics + 구조 로그
- [x] 보안 — API Key + (옵션) 콜백 서명 + PII/Key 마스킹
- [x] 스키마 — OpenAPI + pydantic validation
- [ ] CI/테스트 — 다음 단계에서 pytest + GitHub Actions 포함 권장

## CI / 테스트 (v2.0 추가)
- 로컬: `bash deploy/ci_run.sh` (docker compose up → pytest → down)
- GitHub Actions: `.github/workflows/ci.yml` (PR/Push마다 동일 실행)

테스트 범위
- OpenAPI 계약 테스트: 필수 엔드포인트 존재 여부
- E2E: /health, /metrics, task 생성→폴링 완료


## 운영자 도구 (v2.1 추가)
- DLQ peek/requeue/purge 엔드포인트 추가(관리자 키 필요)
- CI에서 ruff + mypy + pytest 실행


## Claude Sonnet 4.5 (v2.2)
- 기본 LLM_PROVIDER를 anthropic로 설정 가능
- ANTHROPIC_API_KEY / ANTHROPIC_MODEL 필요
- 장애 대비: LLM_FALLBACKS=gemini,openai 권장


## GLM-4.7 (Z.ai) (v2.3)
- LLM_PROVIDER=zai 로 선택 가능(기본 모델: glm-4.7)
- ZAI_API_KEY 필요
- LLM_FALLBACKS로 Claude/Gemini/OpenAI fallback 체인 구성 가능


## v2.4: Structured Output(스키마) + Circuit Breaker + Provider Metrics
- /llm/generate에서 schema_name 지원(검증+1회 자동 수리)
- Redis 기반 provider circuit breaker (BREAKER_* env)
- Prometheus LLM provider latency/fail metrics 추가


## v2.5: Agent-level Structured Output enforcement
- excel_kakao 워커는 LLM 호출을 직접 하지 않고 Supervisor의 /llm/generate(schema_name)만 사용
- LLM 비활성 환경에서도 스키마 모드가 깨지지 않도록 Supervisor에 noop fallback 추가


## v2.6: Error taxonomy + DLQ filters + 2-stage schema repair
- shared/errors.py: 표준 failure_code
- /dlq/*: failure_code/task_type 필터 지원
- schema repair: parse 중심 1차 + validation 중심 2차
- 워커가 retry/DLQ headers에 failure_code를 기록


## v2.7: DLQ envelope standardization + stats
- 실패 시 task body에 failure envelope(failure_code/error/failed_at)를 표준 부착
- DLQ 필터는 headers 뿐 아니라 body envelope에서도 failure_code/task_type 추출
- /dlq/stats 추가(비파괴 샘플 스캔)


## v2.8: Auto triage policy + DLQ dry-run
- shared/policy.py: failure_code 기반 triage(requeue/hold/alarm/ignore)
- /dlq/triage 추가(비파괴 샘플 스캔)
- /dlq/requeue: mode=auto + dry_run 지원
- /dlq/purge: dry_run 지원


## v2.9: Hold queue + Alerts webhook + Task lock(backoff)
- HOLD_QUEUE 추가 및 /hold/* 운영 API 제공
- /dlq/route(mode=auto)로 hold 대상 메시지를 HOLD 큐로 분리
- ALERT_WEBHOOK_URL 기반 웹훅 알림(/alerts/test)
- TASK_LOCK_TTL_SECONDS 기반 task_id 잠금으로 재처리 폭주 방지


## v3.0: One-shot triage apply + Alarm queue enforcement
- ALARM_QUEUE 및 /alarm/* 운영 API
- /dlq/alarm, /dlq/apply 로 정책 기반 자동 조치(requeue/hold/alarm)
- alarm failure_code 수동 requeue 차단(ENFORCE_ALARM_NO_REQUEUE)


## v3.1: HOLD PR template generator + runbook-enriched alerts
- shared/runbooks.py: failure_code → runbook 힌트
- shared/pr_template.py: HOLD 메시지 기반 PR 템플릿 생성
- /hold/pr 추가(비파괴)
- 알림 payload에 runbook 포함


## v3.2: GitHub issue from HOLD + alert dedupe + safe caps + ops script
- /hold/github_issue: HOLD 메시지 → GitHub Issue 생성(옵션)
- AlertDedupe: Redis 기반 알림 중복 억제(ALERT_DEDUPE_TTL_SECONDS)
- /dlq/apply: max_requeue/max_hold/max_alarm 안전 상한
- ops/run_dlq_apply.py: 크론 실행용 스크립트


## v3.3: Ops Gold hardening
- HOLD fix suggestion generator(/hold/suggest_fix) with enforced JSON schema
- Alert routing by event (ALARM/HOLD)
- DLQ apply age window safety (DLQ_APPLY_MAX_AGE_SECONDS)
- Settings bugfix + ZAI(GLM) settings added


## v3.4: One-click HOLD → fix suggestion → GitHub issue
- shared/fix_issue.py: suggest_fix output을 이슈로 변환
- /hold/fix_issue 추가
- RUNBOOK_BASE_URL 기반 runbook URL 실전화


## v3.5: AutoFix PR (safe scaffold)
- /hold/fix_pr: HOLD → suggest_fix → PR 생성 (markdown 파일 커밋)
- shared/github_pr.py: branch/file/PR 생성 헬퍼
- shared/fix_pr.py: 오케스트레이션
- 자동 diff 적용은 v3.6 옵션(위험도 고려)


## v3.7: End-to-end AutoFix (PR + CI dispatch + PR comment)
- /hold/fix_pr_ci: PR 생성 후 workflow_dispatch 실행, 결과를 PR 코멘트로 남김
- shared/github_actions.py, shared/github_comments.py
- 기본은 동기 wait(60s)이며 timeout 시 run url만 남김


## v3.8: CI policy automation
- CI 실패 시 1회 재시도(옵션) + 실패 라벨
- CI 성공 시 ready 라벨 + 옵션 auto-merge
- assignees 자동 지정


## v3.9: Auto-merge hardening
- PR mergeability(mergeable/mergeable_state) 확인 후만 auto-merge
- AUTOFIX_REQUIRED_CHECKS 지정 시 해당 체크 success 확인
- 조건 불충족 시 auto-merge 스킵 + 코멘트


## v4.0: Stability tuning
- mergeable null/unknown 상태를 짧게 폴링(backoff)하여 auto-merge 오판을 감소
- required checks 매칭 모드(exact/contains/regex)
- conflict(dirty) 감지 시 conflict 라벨 + 옵션 @mention 코멘트


## v4.1: SRE comments + backoff curve
- auto-merge 스킵 사유를 SRE 템플릿으로 표준화
- mergeable 폴링을 2→6→12s backoff 곡선으로 개선
- next actions 자동 추천


## v4.2: Checks compatibility + policy
- required checks를 check-runs + status contexts(dual source)로 모두 평가
- neutral/skipped 허용 정책(ENV)
- PR 코멘트에 변경 요약(apply_patches/files/lines) 포함


## v4.3: Per-check policy + unified matching
- 체크별 allow 정책(JSON) 지원
- check-runs/status-contexts 경로 모두 동일 매칭(exact/contains/regex) + 동일 정책 적용
- PR 코멘트 1줄 헤더 추가(스캔 최적화)


## v4.4: Branch protection + review gate
- (옵션) base 브랜치 보호 규칙에서 required checks/approvals를 자동 반영
- 승인 수/changes requested를 반영하여 auto-merge를 안전하게 차단
- needs-review 라벨 + next actions 코멘트


## v4.5: Merge queue compatibility
- merge 전략 선택(direct REST merge vs auto-merge GraphQL)
- merge queue 요구로 direct merge 실패 시 auto-merge로 자동 전환(옵션)
- merge 실패 원인 분류를 Next actions에 기록
- auto-merge 성공 시 queued 라벨 부착


## v4.6: Anti-flap cooldown + labels
- 머지 실패 반복 시 cooldown으로 재시도 폭주를 차단(프로세스 로컬)
- 실패 원인 분류에 따라 상황별 라벨 부착(권한/리베이스/체크/머지큐)


## v4.7: Persistent cooldown
- cooldown 상태를 파일(JSON)로 영속화하여 재시작/멀티워커에서도 플래핑 방지
- 파일락(fcntl) 기반 best-effort 동기화


## v4.8: Comment dedupe + update-in-place
- 동일 내용 코멘트는 중복 게시하지 않고 기존 NEXUS 코멘트를 업데이트
- 코멘트 본문 해시가 동일하면 API 호출 자체를 스킵(스팸/레이트리밋 방지)
- cooldown 키를 repo/pr/class 단위로 세분화하여 다른 실패원인 변화는 즉시 재평가 허용


## v4.9: Strict comment targeting + workflow scoping
- hidden marker 기반으로 NEXUS 코멘트만 정확히 찾아 업데이트(다른 봇/사람 코멘트 오염 방지)
- (옵션) bot login으로 작성자까지 엄격 필터링
- 코멘트 dedupe/쿨다운 키를 workflow 단위로 분리하여 충돌 방지


## v5.0: Operator-grade PR comment
- 상태를 표/액션 리스트로 표준화하여 가독성 극대화
- 이전 리포트 대비 diff를 자동 삽입(옵션)하여 변화점만 즉시 확인
- strict marker v2(repo/workflow/pr 내장)로 업데이트 대상 100% 정합


## v5.1: Changelog summary
- diff 전에 핵심 필드 변화(conclusion/gate/checks/missing_contexts)를 요약 리스트로 출력
- 이전 필드 스냅샷을 store에 함께 저장해 운영자가 변화점을 즉시 인지


## v5.2: Transition summary + actions delta
- ChangeLog 상단에 상태 전이(성공/실패 전환, 체크 악화/개선 등) 1줄 요약 추가
- next_actions 변화도 델타로 감지(순서 무관)하여 운영 판단 속도 향상


## v5.3: Action delta + Top blocker
- Transition을 타입 라벨로 표준화(CONCLUSION/CHECKS/CONTEXT/GATE/NONE)
- 운영자가 즉시 보는 Top blocker 1줄 요약 추가
- next_actions는 순서무관 델타(추가/제거)로 표시하여 변화가 읽히게 함


## v5.4: Quick links + runbook matched top blocker
- 코멘트에 PR/Checks/Workflow run Quick links 추가(운영 클릭-해결 루프 단축)
- missing_contexts 기반 Top blocker에 해당 runbook URL을 자동 매칭해 함께 표기(옵션)


## v5.5: Top failing check + issue fallback
- checks failing 상황에서 가장 최근 실패 check 1개를 이름+링크로 하이라이트(가능한 경우)
- PR 코멘트 게시 실패 시 이슈로 fallback 생성(라벨 nexus-autofix)하여 알림 누락 방지


## v5.6: Retry/backoff + issue append
- 429/5xx에서 코멘트 생성은 exponential backoff + jitter로 재시도(설정 가능)
- 코멘트 실패 시 이슈 fallback은 기존 이슈가 있으면 스냅샷 코멘트 append(옵션)로 최신 상태 유지


## v5.7: Issue body latest snapshot + Retry-After
- fallback issue 본문에 최신 스냅샷을 항상 유지(최신 1장)하고, 히스토리는 코멘트로 누적(옵션)
- 429에서 Retry-After 헤더를 존중하여 불필요한 재시도/레이트리밋 악화 방지


## v5.8: Issue summary box + webhook fallback
- fallback issue 본문 상단에 Summary 표를 고정(transition/top blocker/top failing check 포함)
- 코멘트+이슈까지 실패하는 극단 상황에서 webhook 알림(슬랙/디스코드/Teams 호환 JSON)으로 2차 채널 제공


## v5.9: Webhook blocks + routing
- webhook 페이로드를 Slack blocks로 확장 가능(버튼 링크 포함)
- PR/Checks/Run 링크 및 top failing check 링크를 webhook에도 포함
- repo별 webhook URL 라우팅(선택) 지원


## v6.0 Release package
- RELEASE_NOTES_v6.0.md
- docs/ops/RUNBOOK_v6.0.md
- docs/ops/CONFIG_MATRIX_v6.0.md
- docs/ops/examples/
- scripts/smoke_test.py


## v6.1
- Issue history in-body: AUTOFIX_ISSUE_HISTORY_IN_BODY/AUTOFIX_ISSUE_HISTORY_MAX
- Webhook format teams_adaptive 추가
- .github/workflows/nexus_smoke.yml 추가(드라이런 스모크 테스트)


## v6.2
- GitHub API wrapper(shared/github_api.py)로 호출부 표준화(429/5xx retry 정책 통합)
- ruff/mypy/pytest 설정 및 기본 유닛테스트 추가, CI에서 lint+test 실행


## v6.3
- API 관리 레이어(키/라우팅/예산/레이트리밋/감사로그) 추가: docs/ops/API_MANAGEMENT_v6.3.md
- shared/api_management.py, shared/llm_router.py


## v6.5
- API 거버넌스 100점 마감: provider별 RPM/Retry-After 기반 쿨다운/soft budget degrade/Redis 미가용 시 breaker 파일 영속화
- docs/ops/API_MANAGEMENT_v6.5.md


## v6.6
- FinOps 마감: 실제 usage 기반 비용 ledger + 예산 정산(settlement), 요청 dedupe, 표준 backoff
- docs/ops/FINOPS_v6.6.md


## v6.7
- FinOps 고도화: 모델별 단가(JSON), usage 없는 경우 토큰 근사, 목적별 dedupe TTL 정책
- docs/ops/FINOPS_v6.7.md


## v6.8
- Observability/FinOps 운영 마감: 비용/브레이커/디듀프 메트릭 + 태깅(team/project) + 리포트 생성기(tools/finops_report.py)
- docs/ops/OBSERVABILITY_v6.8.md


## v6.9
- Slack/Teams 웹훅 알림 + 이상치 탐지 도구(tools/anomaly_watch.py) + 운영 문서(docs/ops/NOTIFICATIONS_v6.9.md)


## v6.10
- 운영 리허설 하네스/부하 도구 + 스코어카드 템플릿
- docs/ops/REHEARSAL_v6.10.md
- tools/rehearsal_harness.py, tools/rehearsal_load_test.py


## v6.11
- 리허설 스코어카드 자동 생성/자동 판정(tools/rehearsal_autoscore.py)
- docs/ops/REHEARSAL_v6.11.md
