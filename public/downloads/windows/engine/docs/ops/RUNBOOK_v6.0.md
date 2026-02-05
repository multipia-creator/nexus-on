# NEXUS AutoFix Operator Runbook (v6.0)

Goal
- Provide a single operational loop for PR auto-fix outcomes:
  Comment -> Checks/Run -> Apply/Retry -> (If comment fails) Issue -> (If issue fails) Webhook alert

1) Normal path (PR Comment)
- Open the PR and read the NEXUS comment.
- Use "Transition" to see what changed since last run.
- Read "Top blocker" to decide the next action.
- Click "Quick links" to jump to Checks or Workflow run.
- If checks failing, use "Top failing check" link (if present) to go straight to the failing job.

2) If PR comment is missing
- Check if a fallback issue exists:
  Title: "NEXUS AutoFix report for PR #<N>"
- The issue body top keeps the latest snapshot + summary table.
- If AUTOFIX_COMMENT_ISSUE_APPEND=true, history is appended as issue comments.

3) If both PR comment and issue fail
- Enable webhook fallback:
  AUTOFIX_ALERT_WEBHOOK_ENABLED=true
  AUTOFIX_ALERT_WEBHOOK_URL=...
- Optional: Slack blocks payload:
  AUTOFIX_ALERT_WEBHOOK_FORMAT=slack_blocks
- Optional: repo routing:
  AUTOFIX_ALERT_WEBHOOK_ROUTE_MAP="repo:org/repo=url;default=url"

4) Known failure modes and actions
- 401/403 on comment post:
  - Token lacks permission or is invalid.
  - Expect immediate issue fallback; fix token perms.
- 429 rate limit:
  - With RESPECT_RETRY_AFTER=true, system sleeps per Retry-After when present.
  - If still failing, issue fallback triggers.
- 5xx GitHub errors:
  - Retries then fallbacks.
- Issue creation failures:
  - Usually token lacks issue scope or org policy blocks issue creation.
  - Enable webhook as last resort; align org policy.

5) Minimal required GitHub token scopes
- For PR comments: repo (classic) / issues + pull_requests (fine-grained, depending on org)
- For issue fallback: issues (create/search/comment)
- For check-runs visibility: actions / checks read (typically included by repo scope)



## v6.1 additions
- Issue history can be kept inside issue body between markers (no reliance on issue comments).
- Webhook supports Microsoft Teams MessageCard (format=teams_adaptive).
- A dry-run smoke test GitHub workflow is provided at .github/workflows/nexus_smoke.yml.


## Baseline Governance (Character Rehearsal)

목표: 리허설 스코어(캐릭터 포함)가 100점인데도 운영 중 실수로 baseline을 덮어써서 회귀를 ‘정상’으로 만드는 사고를 방지한다.

원칙(2-step):
1) 후보 생성(candidate): 자동 생성, 승인 baseline 직접 덮어쓰기 금지
2) 승인(promote): 사람(승인자) + 감사(audit) + WORM archive

절차:
- 후보 생성
  - `python tools/character_rehearsal_autoscore.py --write_baseline`
  - 결과: `logs/character_rehearsal_baseline_candidate.json`

- 승인(프로모트)
  - `BASELINE_APPROVER=admin python tools/baseline_promote_character.py --candidate logs/character_rehearsal_baseline_candidate.json`
  - 승인 baseline: `tools/character_rehearsal_baseline.json`
  - 감사 로그(체인): `logs/baseline_audit.jsonl` (+ `.chain`)
  - 이전 baseline은 `WORM_ARCHIVE_DIR`(기본 `worm_archive/`)로 읽기전용 보관

운영 정책:
- `tools/baseline_governance.json`의 `approvers` allowlist로 승인자 제한
- 필요 시 `require_token=true` + `token_sha256`로 2차 인증(환경변수 `BASELINE_APPROVER_TOKEN`)

장애 대응 힌트:
- 회귀가 의심되면 `tools/character_rehearsal_baseline.json`의 `approved_at_utc/approved_by/sha256`를 확인
- baseline_audit.jsonl은 체인으로 tamper-evident이므로 삭제/변조 흔적이 드러남

### Two-person rule (PR-07)
기본값: `tools/baseline_governance.json`에서 `require_two_person=true`.

승인 시 환경변수:
- `BASELINE_APPROVER` (1차 승인자)
- `BASELINE_APPROVER2` (2차 승인자, 반드시 1차와 달라야 함)

예시:
- `BASELINE_APPROVER=admin BASELINE_APPROVER2=ops-lead python tools/baseline_promote_character.py --candidate logs/character_rehearsal_baseline_candidate.json`

주의:
- GitHub Actions 워크플로우는 candidate 생성 및 artifact 업로드까지만 수행한다.
- approve/promote는 로컬 또는 보안된 운영 환경에서 수동 수행한다(감사로그/WORM archive 포함).

### WORM Snapshot: default set (PR-07)
리허설/베이스라인 거버넌스 증적을 WORM에 주기적으로 적재한다.

권장(기본 세트):
- `python tools/worm_snapshot.py --archive-dir /mnt/worm --default-set`

참고:
- `--default-set`는 `DEFAULT_INCLUDE` 목록(감사로그/리허설 증적/베이스라인/승인 설정)을 스냅샷한다.
- 파일이 없으면 자동 skip된다(운영 환경별 편차 허용).

### Baseline Promote 실패 알림/증적 (PR-08)
`tools/baseline_promote_character.py`는 실패(guard/policy 위반 또는 예외) 시 아래를 best-effort로 수행한다.
- `logs/baseline_promote_error.json` 기록(에러 envelope)
- Slack/Teams 웹훅이 설정된 경우 `shared.notify.notify()`로 알림 전송

운영 권장:
- 웹훅 URL은 환경변수/설정으로 주입한다(SLACK_WEBHOOK_URL 또는 TEAMS_WEBHOOK_URL).
- 승인 실패 시 error envelope를 GitHub Issue/티켓에 그대로 첨부한다.

### 스코어카드 반영 (PR-08)
`tools/rehearsal_autoscore.py` 스코어카드에 `0. Baseline Governance` 섹션이 추가된다.
- 2인 승인 on/off, baseline/candidate 존재, 마지막 승인(audit tail) 메타를 표시한다.

### 알림 라우팅(Alarm Queue/GitHub Fallback) (PR-09)
`shared.notify.notify()`는 다음 순서로 알림을 시도한다.
1) Unified Alert Webhook (`shared.alerter.send_webhook`)
2) Slack/Teams (legacy)
3) RabbitMQ Alarm Queue(`ALARM_QUEUE`, 기본 `nexus.alarm`) publish
4) GitHub Issue 생성(옵션: `GITHUB_REPO`, `GITHUB_TOKEN` 필요)

권장:
- 운영 환경에서는 (1)+(3)을 기본 경로로 두고, (4)는 웹훅/큐 장애 시 최후 수단으로 사용한다.


## Alarm Queue Worker

Purpose: consume `ALARM_QUEUE` and route alerts to webhook/Slack/Teams/GitHub without loops.

Required env:
- RABBITMQ_URL
- ALARM_QUEUE (default: nexus.alarm)
- ALARM_RETRY_QUEUE_PREFIX (default: nexus.alarm.retry)
- ALARM_DLQ_QUEUE (default: nexus.alarm.dlq)
- ALARM_MAX_RETRIES (default: 2)

Start (local):
- `python -m shared.alarm_worker`

Notes:
- The worker never `requeue=True`. Failures are republished to retry queues (TTL) or the alarm DLQ.
- If `dedupe_key` is present and Redis is available, repeated alerts are suppressed within `ALERT_DEDUPE_TTL_SECONDS`.


### Alarm loop hard-guard

- `shared.notify._alarm_publish_allowed()` blocks publishing to the alarm queue when `payload.origin` indicates it already came from the alarm worker or `routed_via` includes `alarm_queue`.
- This protects against accidental infinite loops even if a caller misconfigures `allow_alarm_queue`.


### GitHub token source

- GitHub REST wrapper reads `GITHUB_TOKEN` from environment; if absent it falls back to `settings.github_token`.
