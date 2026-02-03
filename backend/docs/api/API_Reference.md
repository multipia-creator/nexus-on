# API Reference (Supervisor) — v1.8

권장: Swagger UI
- http://localhost:8000/docs

OpenAPI 스키마
- `openapi.yaml`

핵심 엔드포인트
- GET /health
- POST /excel-kakao
- GET /tasks/{task_id}
- POST /agent/callback (Agent → Supervisor)
- POST /llm/generate (LLM 단독 점검)

인증
- 모든 요청에 `X-API-Key` 헤더 필요

DLQ 운영 엔드포인트(관리자 전용)
- GET /dlq/peek?limit=10  (헤더: X-Admin-Key)
- POST /dlq/requeue?limit=10 (헤더: X-Admin-Key)
- POST /dlq/purge?limit=1000 (헤더: X-Admin-Key)


LLM Provider (v2.2)
- LLM_PROVIDER=anthropic|gemini|openai
- Claude Sonnet 4.5 권장: ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
- Fallback: LLM_FALLBACKS=gemini,openai (comma-separated)


GLM-4.7 (Z.ai) Provider (v2.3)
- LLM_PROVIDER=zai (또는 glm/gml)
- 환경변수: ZAI_API_KEY, ZAI_MODEL=glm-4.7, (옵션) ZAI_BASE_URL
- fallback 예: LLM_FALLBACKS=anthropic,gemini,openai


LLM 스키마 모드 (v2.4)
- POST /llm/generate
  - input_text: string (required)
  - schema_name: string (optional; 예: "excel_kakao_output")
  - allow_repair: bool (default true)
- schema_name이 있으면, 응답은 text가 아니라 data(JSON object)로 반환되며 JSON Schema 검증을 통과해야 합니다.


v2.5: 에이전트 스키마 강제
- excel_kakao 워커는 Supervisor /llm/generate의 schema_name 모드만 사용합니다.
- LLM 비활성(LLM_REQUIRED=false)인 경우, Supervisor가 스키마 모드에서 deterministic JSON(noop)을 반환하여 파이프라인이 깨지지 않습니다.


DLQ 필터 (v2.6)
- /dlq/peek, /dlq/requeue, /dlq/purge 에서 아래 쿼리 파라미터 지원:
  - failure_code: headers.failure_code 기준
  - task_type: message.task_type 또는 message.type 기준


DLQ 통계 (v2.7)
- GET /dlq/stats?sample=200
  - DLQ 메시지를 sample 개수만큼 비파괴적으로 스캔하여 failure_code/task_type 분포를 반환합니다.
  - 운영 대시보드/트리아지에 사용합니다.


DLQ 자동 트리아지 (v2.8)
- GET /dlq/triage?sample=200
  - 정책(AUTO_*_FAILURE_CODES + 기본 휴리스틱)으로 DLQ를 분류하여 requeue/hold/alarm/ignore 카운트를 반환합니다.

DLQ 재처리 dry-run (v2.8)
- POST /dlq/requeue?limit=10&failure_code=...&task_type=...&dry_run=true
- POST /dlq/requeue?limit=10&mode=auto&dry_run=true
  - mode=auto 인 경우 failure_code를 기준으로 정책상 requeue 대상만 선택합니다.
  - dry_run=true 인 경우 실제 이동 없이 “매칭 수”만 증가시켜 결과를 확인합니다.

DLQ purge dry-run (v2.8)
- POST /dlq/purge?limit=100&failure_code=...&dry_run=true


v2.9: Hold queue + Alerts + Anti-infinite retry lock
- HOLD queue:
  - GET /hold/peek
  - POST /hold/purge
  - POST /dlq/route?mode=auto (hold 대상 메시지를 HOLD 큐로 이동)
- Alerts:
  - POST /alerts/test (ALERT_WEBHOOK_URL 필요)
- Task lock:
  - 워커는 max_retries 초과로 DLQ로 보낼 때 task_id를 Redis에 잠그고(TASK_LOCK_TTL_SECONDS) 재처리 폭주를 방지합니다.


v3.0: Triage Apply + Alarm Queue
- ALARM queue:
  - GET /alarm/peek
  - POST /alarm/purge
- DLQ routing:
  - POST /dlq/alarm?mode=auto&limit=100&dry_run=true|false&send_alert=true|false
  - POST /dlq/apply?sample=500&dry_run=true|false&send_alert=true|false
    - 정책에 따라 DLQ를 자동 분류/조치: requeue/hold/alarm/ignore
- ENFORCE_ALARM_NO_REQUEUE=true 인 경우, alarm failure_code는 수동 requeue를 차단합니다.


v3.1: HOLD PR Template + Alert Runbook Enrichment
- GET /hold/pr?limit=1
  - HOLD 큐 메시지를 기반으로 스키마/프롬프트 수정용 PR 템플릿을 생성합니다(비파괴).
- /dlq/alarm, /dlq/apply의 webhook payload에 runbook 힌트를 포함합니다.


v3.2: GitHub Issue Generator + Alert Dedupe + Safe Apply Caps
- POST /hold/github_issue?limit=1&dry_run=true|false
  - HOLD 메시지로부터 PR 템플릿을 만들고 GitHub Issue를 생성합니다(GITHUB_REPO/GITHUB_TOKEN 필요).
- Alerts dedupe:
  - 동일 (task_type, failure_code) 조합은 ALERT_DEDUPE_TTL_SECONDS 동안 알림을 억제합니다.
- /dlq/apply 안전 상한:
  - max_requeue/max_hold/max_alarm 파라미터로 한 번에 이동 가능한 최대치를 제한합니다.


v3.3: Ops Gold (Fix Suggestor + Alert Routing + DLQ Apply Age Window + Settings Fix)
- GET /hold/suggest_fix?limit=1&provider=anthropic|zai|gemini|openai
  - HOLD 메시지에서 원인/수정안(prompt/schema/code) 제안을 생성(JSON schema enforced: fix_suggestion).
- Alerts routing:
  - ALERT_WEBHOOK_URL_ALARM / ALERT_WEBHOOK_URL_HOLD (event 기반 라우팅)
- DLQ apply age window:
  - DLQ_APPLY_MAX_AGE_SECONDS (기본 2h) 초과 메시지는 /dlq/apply에서 자동 skip
- Settings 정합성:
  - anthropic_model/llm_fallbacks 인덴트 버그 수정
  - zai_model/zai_base_url 설정 추가


v3.4: SuggestFix → GitHub Issue + Real Runbook URLs
- GET_RUNBOOK now prefers RUNBOOK_BASE_URL/{FAILURE_CODE}
- POST /hold/fix_issue?limit=1&provider=anthropic|zai|gemini|openai&dry_run=true|false
  - HOLD 메시지에서 fix_suggestion(JSON schema enforced)을 생성한 뒤 GitHub Issue로 등록합니다.


v3.5: AutoFix PR Generator (HOLD → fix suggestion → PR)
- POST /hold/fix_pr?limit=1&provider=anthropic|zai|gemini|openai&dry_run=true|false
  - HOLD 메시지에서 fix_suggestion(JSON schema enforced)을 생성한 뒤,
    GitHub 브랜치를 만들고 `.nexus/autofix/*.md` 파일을 커밋하여 PR을 생성합니다.
  - proposed_changes의 diff는 자동 적용하지 않고, PR에 파일로 포함합니다(안전 우선).
ENV:
- GITHUB_REPO, GITHUB_TOKEN required
- (optional) GITHUB_DEFAULT_BRANCH, GITHUB_AUTOFIX_DIR


v3.6: Optional Patch Apply (AutoFix PR with actual file edits)
- POST /hold/fix_pr?apply_patches=true&allowlist=shared/,nexus_supervisor/&max_files=5&max_lines=400
  - fix_suggestion의 unified diff를 allowlist 범위 내 파일에 한해 적용 후 커밋합니다.
  - 기본값: apply_patches=false (안전)
Safety:
- allowlist prefix match
- max_files / max_lines caps
- strict context match (fails if mismatch)


v3.7: CI Dispatch + PR Comment (AutoFix end-to-end)
- POST /hold/fix_pr_ci?provider=anthropic|zai|gemini|openai&apply_patches=true|false
  - PR 생성(옵션: patch 적용) → GitHub Actions workflow_dispatch → 결과를 PR 코멘트로 남김
ENV:
- GITHUB_WORKFLOW required (workflow id or file name)
- GITHUB_ACTIONS_WAIT_SECONDS / GITHUB_ACTIONS_POLL_SECONDS controls synchronous wait
Notes:
- workflow run id는 dispatch 후 최근 실행을 조회해 추적합니다.


v3.8: CI Policy Automation (label/assign/retry/optional merge)
- /hold/fix_pr_ci now:
  - sets assignees (AUTOFIX_ASSIGNEES)
  - retries CI once on failure (AUTOFIX_CI_RETRY_ONCE)
  - labels PR as ready/failed (AUTOFIX_LABEL_READY / AUTOFIX_LABEL_FAILED)
  - optional auto-merge when CI succeeds (AUTOFIX_AUTO_MERGE + AUTOFIX_MERGE_METHOD)


v3.9: Merge hardening (mergeable_state + required checks)
- Auto-merge now gated by:
  - PR mergeable == true (mergeable_state acceptable)
  - optional required check names (AUTOFIX_REQUIRED_CHECKS) must be success in check-runs summary
- If gating fails, auto-merge is skipped and a PR comment is posted with the reason.


v4.0: Stability tuning (mergeable backoff + robust required-check matching + conflict policy)
- Auto-merge gating improves:
  - Poll mergeable/mergeable_state briefly to avoid GitHub's transient null mergeable.
  - Required checks matching modes: exact|contains|regex (AUTOFIX_CHECK_MATCH_MODE)
  - On conflict (mergeable_state=dirty): add conflict label and optional @mention comment.
ENV:
- AUTOFIX_MERGEABLE_POLL_SECONDS / AUTOFIX_MERGEABLE_MAX_WAIT_SECONDS
- AUTOFIX_LABEL_CONFLICT / AUTOFIX_MENTION_ON_CONFLICT


v4.1: SRE-style PR comments + mergeable backoff curve + improved next-actions
- Mergeable polling uses backoff curve: AUTOFIX_MERGEABLE_BACKOFF_CURVE (e.g. 2,6,12)
- PR comments standardized to SRE template (fields: failure_code, run_url, status, conclusion, merge_gate, next_actions)
- When auto-merge is skipped, comment includes actionable next steps.


v4.2: Dual-source required checks + neutral/skipped policy + change summary in comments
- Required checks evaluation supports:
  - check-runs (default)
  - fallback to combined status contexts when check-runs are missing (AUTOFIX_CHECK_DUAL_SOURCE=true)
- Policy toggles:
  - AUTOFIX_CHECK_ACCEPT_NEUTRAL
  - AUTOFIX_CHECK_ACCEPT_SKIPPED
- PR comments include change summary: apply_patches, changed files, approx line delta.


v4.3: Per-check policy + unified matching across check-runs/status-contexts + header comments
- Per-check allow policy via JSON: AUTOFIX_REQUIRED_CHECKS_POLICY
  - Example: {"unit-tests":{"allow":["success"]},"lint":{"allow":["success","skipped"]}}
- Required checks evaluation uses the same matching mode for:
  - check-runs
  - status contexts detail (name:state)
- PR comments include a 1-line header: conclusion|gate for quick scanning.


v4.4: Branch protection + review gate (approvals/changes-requested)
- Optional: fetch branch protection from base branch and adopt required status checks / approvals count
  - AUTOFIX_USE_BRANCH_PROTECTION=true
- Review gating:
  - require N approvals (AUTOFIX_REQUIRE_APPROVALS) or from branch protection
  - block auto-merge if CHANGES_REQUESTED exists
  - add AUTOFIX_LABEL_NEEDS_REVIEW label and include next actions in PR comment


v4.5: Merge strategy (direct vs auto-merge) + merge queue compatibility + merge error classification
- AUTOFIX_MERGE_STRATEGY:
  - direct: REST merge endpoint
  - auto: enable GitHub Auto-merge via GraphQL (merge queue compatible)
- AUTOFIX_AUTO_MERGE_FALLBACK:
  - when direct merge fails with merge queue required, try enabling auto-merge
- Merge failure is classified and appended into Next actions (permission/queue/conflict/etc).
- On successful auto-merge enablement, label AUTOFIX_LABEL_QUEUED is attached.


v4.6: Failure cooldown + label routing (anti-flap)
- Process-local cooldown to prevent repeated merge attempts on same PR after failure
  - AUTOFIX_FAILURE_COOLDOWN_MINUTES (default 30)
- Merge failure classification routes labels:
  - permission_denied -> AUTOFIX_LABEL_NEED_PERMISSION
  - merge_conflict -> AUTOFIX_LABEL_NEED_REBASE
  - required_checks_missing -> AUTOFIX_LABEL_NEED_CHECKS
  - merge_queue_required -> AUTOFIX_LABEL_NEED_MERGE_QUEUE


v4.7: Persistent cooldown store (file-based) for multi-worker/restarts
- Cooldown state is persisted to a JSON file with an advisory file lock:
  - AUTOFIX_COOLDOWN_STORE_PATH (default /tmp/nexus_cooldown_store.json)
- Prevents flapping even across process restarts and across multiple workers sharing the same filesystem.


v4.8: Comment dedupe + update-in-place; cooldown key granularity
- PR comment is updated in-place instead of posting duplicates (detects existing NEXUS AutoFix comment)
- Comment dedupe: if body hash unchanged, skip API call and return last comment url
- Cooldown key mode:
  - AUTOFIX_COOLDOWN_KEY_MODE=pr|repo_pr|repo_pr_class (default repo_pr_class)


v4.9: Strict PR comment targeting + workflow-scoped dedupe/cooldown keys
- PR comment updates only comments containing AUTOFIX_COMMENT_MARKER (hidden HTML marker).
- Optional strict author filter with AUTOFIX_GITHUB_BOT_LOGIN.
- Comment dedupe keys are scoped by workflow id (GITHUB_WORKFLOW).
- Cooldown keys include workflow id to avoid collisions across workflows.


v5.0: Operator-grade PR comment (table + diff) + strict marker v2
- Comment body begins with a strict hidden marker v2 embedding repo/workflow/pr.
- Comment content is standardized as a Status table + Next actions.
- Optional diff injection from previous report (stored per repo/workflow/pr):
  - AUTOFIX_COMMENT_STORE_BODY=true
  - AUTOFIX_COMMENT_DIFF_MAX_LINES=24


v5.1: Changelog summary (field delta) above diff
- Parses stable fields from Status table and emits a short changelog list.
- Stores previous field snapshot alongside comment body (per repo/workflow/pr).
  - AUTOFIX_COMMENT_CHANGELOG=true


v5.2: Transition summary + next_actions delta in changelog
- Adds a short "Transition" header (e.g., success->failure, checks improved/worsened).
- Changelog now includes required_contexts and next_actions deltas (order-insensitive).
  - AUTOFIX_COMMENT_TRANSITION_SUMMARY=true


v5.3: Action delta + Top blocker + typed Transition
- Transition summary now includes a type label (CONCLUSION/CHECKS/CONTEXT/GATE/NONE).
- Adds "Top blocker" one-liner for operator focus.
- Adds action delta (added/removed) for next_actions instead of raw string change.
  - AUTOFIX_COMMENT_ACTION_DELTA=true
  - AUTOFIX_COMMENT_TOP_BLOCKER=true


v5.4: Quick links + top-blocker runbook match
- Adds Quick links section (PR/Checks/Workflow run) for operator loop.
  - AUTOFIX_COMMENT_QUICKLINKS=true
- Top blocker tries to attach a matching runbook URL when missing_contexts is present.
  - AUTOFIX_COMMENT_TOP_BLOCKER_LINK=true


v5.5: Top failing check highlight + issue fallback
- When checks are failing, attempts to fetch the top failing check name + html_url (best-effort) and prints it in Top blocker.
  - AUTOFIX_COMMENT_TOP_CHECK=true
- If PR comment fails to post/update, creates an issue fallback labeled 'nexus-autofix'.
  - AUTOFIX_COMMENT_ISSUE_FALLBACK=true


v5.6: Failure policy (retry/backoff) + issue append
- Comment create uses retry/backoff on 429/5xx (configurable).
  - AUTOFIX_COMMENT_FAIL_RETRY=true
  - AUTOFIX_COMMENT_FAIL_RETRY_MAX=3
  - AUTOFIX_COMMENT_FAIL_RETRY_BASE_MS=600
- Issue fallback now appends a snapshot comment when the issue already exists (optional).
  - AUTOFIX_COMMENT_ISSUE_APPEND=true


v5.7: Issue body update + respect Retry-After
- Issue fallback keeps "Latest snapshot" in the issue body, and optionally appends history as issue comments.
  - AUTOFIX_COMMENT_ISSUE_UPDATE_BODY=true
  - AUTOFIX_COMMENT_ISSUE_APPEND=true
- Retry/backoff respects Retry-After on 429/5xx when enabled.
  - AUTOFIX_COMMENT_RESPECT_RETRY_AFTER=true


v5.8: Issue summary box + webhook fallback
- Issue fallback body includes a compact Summary table (transition/top blocker/top failing check + key fields).
- If both PR comment and issue fallback fail, sends a webhook alert (generic JSON with {text}).
  - AUTOFIX_ALERT_WEBHOOK_ENABLED=false
  - AUTOFIX_ALERT_WEBHOOK_URL=...


v5.9: Webhook blocks + routing + check links
- Webhook supports 'text' or 'slack_blocks' payload formats and includes PR/Checks/Run links and top failing check link when available.
  - AUTOFIX_ALERT_WEBHOOK_FORMAT=text|slack_blocks
- Optional routing map can send different repos to different webhook URLs.
  - AUTOFIX_ALERT_WEBHOOK_ROUTE_MAP="repo:org/repo=url;default=url"


v6.0: Release packaging
- Adds operator runbook, config matrix, example snapshots, and a dry-run smoke test script.


v6.1: Issue body history + Teams webhook + CI smoke workflow
- Optionally keeps history inside issue body between markers (AUTOFIX_ISSUE_HISTORY_IN_BODY, AUTOFIX_ISSUE_HISTORY_MAX).
- Adds Teams MessageCard webhook format (teams_adaptive).
- Adds GitHub Actions dry-run smoke workflow (.github/workflows/nexus_smoke.yml).


v6.2: Quality hardening
- Adds GitHub API wrapper, ruff/mypy configs, and unit tests. CI runs lint+tests.


v6.3: API management
- Adds API governance layer (keys, provider routing, budgets, rate limiting, audit logs).


v6.5: API governance 100
- Per-provider/global rate limits, Retry-After cooldown, soft budget degrade, breaker file fallback.


v6.6: FinOps
- Cost ledger + estimate settlement, request dedupe, standardized backoff.


v6.7: FinOps++
- Model-specific pricing JSON, usage fallback token estimation, purpose-based dedupe TTL.


v6.8: Observability
- Cost/dedupe/breaker metrics, team/project tagging, FinOps report generator.


v6.9: Notifications
- Slack/Teams webhook notifier, anomaly watch CLI, monthly report cron guidance.


v6.10: Ops rehearsal
- Rehearsal harness + load test + scorecard templates.


v6.11: Rehearsal autoscore
- Auto-generate rehearsal scorecard from audit + ledger evidence.
