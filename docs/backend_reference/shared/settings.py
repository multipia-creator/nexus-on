from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # -----------------
    # Auth / admin
    # -----------------
    nexus_api_key: str = Field(default="dev-key", alias="NEXUS_API_KEY")
    admin_api_key: str = Field(default="admin-key", alias="ADMIN_API_KEY")

    # -----------------
    # Redis / MQ
    # -----------------
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    task_ttl_seconds: int = Field(default=604800, alias="TASK_TTL_SECONDS")

    rabbitmq_url: str = Field(default="amqp://guest:guest@rabbitmq:5672/", alias="RABBITMQ_URL")
    task_queue: str = Field(default="nexus.tasks", alias="TASK_QUEUE")
    retry_queue_prefix: str = Field(default="nexus.retry", alias="RETRY_QUEUE_PREFIX")
    dlq_queue: str = Field(default="nexus.dlq", alias="DLQ_QUEUE")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")

    # -----------------
    # Legacy LLM routing (kept for backward compatibility)
    # -----------------
    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    llm_required: bool = Field(default=False, alias="LLM_REQUIRED")
    llm_fallbacks: str = Field(default="", alias="LLM_FALLBACKS")

    gemini_model: str = Field(default="gemini-3-flash-preview", alias="GEMINI_MODEL")
    openai_model: str = Field(default="gpt-5.2", alias="OPENAI_MODEL")
    anthropic_model: str = Field(default="claude-sonnet-4-5-20250929", alias="ANTHROPIC_MODEL")

    # Legacy GLM naming (previously 'zai')
    zai_model: str = Field(default="glm-4.7", alias="ZAI_MODEL")
    zai_base_url: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4/chat/completions",
        alias="ZAI_BASE_URL",
    )
    # -----------------
    # Character chatbot defaults
    # -----------------
    character_sexy_threshold: int = Field(default=51, alias="CHARACTER_SEXY_THRESHOLD")


    # -----------------
    # Provider health (circuit breaker)
    # -----------------
    breaker_window_seconds: int = Field(default=300, alias="BREAKER_WINDOW_SECONDS")
    breaker_fail_threshold: int = Field(default=5, alias="BREAKER_FAIL_THRESHOLD")
    breaker_cooldown_seconds: int = Field(default=120, alias="BREAKER_COOLDOWN_SECONDS")

    # -----------------
    # DLQ triage policies
    # -----------------
    auto_requeue_failure_codes: str = Field(
        default="PROVIDER_TIMEOUT,PROVIDER_UPSTREAM_ERROR,PROVIDER_RATE_LIMIT",
        alias="AUTO_REQUEUE_FAILURE_CODES",
    )
    auto_hold_failure_codes: str = Field(
        default="SCHEMA_PARSE_ERROR,SCHEMA_VALIDATION_ERROR,SCHEMA_REPAIR_FAILED",
        alias="AUTO_HOLD_FAILURE_CODES",
    )
    auto_alarm_failure_codes: str = Field(
        default="PROVIDER_AUTH_ERROR,PROVIDER_DISABLED",
        alias="AUTO_ALARM_FAILURE_CODES",
    )

    dlq_apply_max_age_seconds: int = Field(default=7200, alias="DLQ_APPLY_MAX_AGE_SECONDS")

    # -----------------
    # Alerts
    # -----------------
    alert_webhook_url: str = Field(default="", alias="ALERT_WEBHOOK_URL")
    alert_webhook_url_alarm: str = Field(default="", alias="ALERT_WEBHOOK_URL_ALARM")
    alert_webhook_url_hold: str = Field(default="", alias="ALERT_WEBHOOK_URL_HOLD")
    alert_dedupe_ttl_seconds: int = Field(default=900, alias="ALERT_DEDUPE_TTL_SECONDS")

    hold_queue: str = Field(default="nexus.hold", alias="HOLD_QUEUE")
    alarm_queue: str = Field(default="nexus.alarm", alias="ALARM_QUEUE")
    enforce_alarm_no_requeue: bool = Field(default=True, alias="ENFORCE_ALARM_NO_REQUEUE")

    alarm_retry_queue_prefix: str = Field(default="nexus.alarm.retry", alias="ALARM_RETRY_QUEUE_PREFIX")
    alarm_dlq_queue: str = Field(default="nexus.alarm.dlq", alias="ALARM_DLQ_QUEUE")
    alarm_max_retries: int = Field(default=2, alias="ALARM_MAX_RETRIES")
    runbook_base_url: str = Field(default="", alias="RUNBOOK_BASE_URL")

    # -----------------
    # GitHub integration (optional)
    # -----------------
    github_api_base: str = Field(default="https://api.github.com", alias="GITHUB_API_BASE")
    github_repo: str = Field(default="", alias="GITHUB_REPO")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_default_branch: str = Field(default="", alias="GITHUB_DEFAULT_BRANCH")
    github_autofix_dir: str = Field(default=".nexus/autofix", alias="GITHUB_AUTOFIX_DIR")
    github_workflow: str = Field(default="", alias="GITHUB_WORKFLOW")
    github_workflow_ref: str = Field(default="", alias="GITHUB_WORKFLOW_REF")
    github_actions_wait_seconds: int = Field(default=60, alias="GITHUB_ACTIONS_WAIT_SECONDS")
    github_actions_poll_seconds: int = Field(default=3, alias="GITHUB_ACTIONS_POLL_SECONDS")

    # (A long list of existing autofix controls lives in this project; keep them as-is.)
    autofix_ci_retry_once: bool = Field(default=True, alias="AUTOFIX_CI_RETRY_ONCE")
    autofix_label_ready: str = Field(default="autofix-ready", alias="AUTOFIX_LABEL_READY")
    autofix_label_failed: str = Field(default="autofix-failed", alias="AUTOFIX_LABEL_FAILED")
    autofix_auto_merge: bool = Field(default=False, alias="AUTOFIX_AUTO_MERGE")
    autofix_merge_method: str = Field(default="squash", alias="AUTOFIX_MERGE_METHOD")
    autofix_assignees: str = Field(default="", alias="AUTOFIX_ASSIGNEES")
    autofix_required_checks: str = Field(default="", alias="AUTOFIX_REQUIRED_CHECKS")
    autofix_check_match_mode: str = Field(default="contains", alias="AUTOFIX_CHECK_MATCH_MODE")
    autofix_mergeable_poll_seconds: int = Field(default=6, alias="AUTOFIX_MERGEABLE_POLL_SECONDS")
    autofix_mergeable_backoff_curve: str = Field(default="2,6,12", alias="AUTOFIX_MERGEABLE_BACKOFF_CURVE")
    autofix_check_accept_neutral: bool = Field(default=False, alias="AUTOFIX_CHECK_ACCEPT_NEUTRAL")
    autofix_check_accept_skipped: bool = Field(default=False, alias="AUTOFIX_CHECK_ACCEPT_SKIPPED")
    autofix_check_dual_source: bool = Field(default=True, alias="AUTOFIX_CHECK_DUAL_SOURCE")
    autofix_required_checks_policy: str = Field(default="", alias="AUTOFIX_REQUIRED_CHECKS_POLICY")
    autofix_use_branch_protection: bool = Field(default=False, alias="AUTOFIX_USE_BRANCH_PROTECTION")
    autofix_require_approvals: int = Field(default=0, alias="AUTOFIX_REQUIRE_APPROVALS")
    autofix_label_needs_review: str = Field(default="autofix-needs-review", alias="AUTOFIX_LABEL_NEEDS_REVIEW")
    autofix_merge_strategy: str = Field(default="direct", alias="AUTOFIX_MERGE_STRATEGY")
    autofix_auto_merge_fallback: bool = Field(default=True, alias="AUTOFIX_AUTO_MERGE_FALLBACK")
    autofix_label_queued: str = Field(default="autofix-queued", alias="AUTOFIX_LABEL_QUEUED")
    autofix_failure_cooldown_minutes: int = Field(default=30, alias="AUTOFIX_FAILURE_COOLDOWN_MINUTES")
    autofix_label_need_permission: str = Field(default="autofix-need-permission", alias="AUTOFIX_LABEL_NEED_PERMISSION")
    autofix_label_need_rebase: str = Field(default="autofix-need-rebase", alias="AUTOFIX_LABEL_NEED_REBASE")
    autofix_label_need_checks: str = Field(default="autofix-need-checks", alias="AUTOFIX_LABEL_NEED_CHECKS")
    autofix_label_need_merge_queue: str = Field(default="autofix-need-merge-queue", alias="AUTOFIX_LABEL_NEED_MERGE_QUEUE")

    autofix_cooldown_store_path: str = Field(default="/tmp/nexus_cooldown_store.json", alias="AUTOFIX_COOLDOWN_STORE_PATH")
    autofix_cooldown_key_mode: str = Field(default="repo_pr_class", alias="AUTOFIX_COOLDOWN_KEY_MODE")
    autofix_comment_dedupe: bool = Field(default=True, alias="AUTOFIX_COMMENT_DEDUPE")
    autofix_github_bot_login: str = Field(default="", alias="AUTOFIX_GITHUB_BOT_LOGIN")
    autofix_comment_marker: str = Field(default="<!-- NEXUS_AUTOFIX_MARKER:v2 -->", alias="AUTOFIX_COMMENT_MARKER")
    autofix_comment_diff_max_lines: int = Field(default=24, alias="AUTOFIX_COMMENT_DIFF_MAX_LINES")
    autofix_comment_store_body: bool = Field(default=True, alias="AUTOFIX_COMMENT_STORE_BODY")
    autofix_comment_changelog: bool = Field(default=True, alias="AUTOFIX_COMMENT_CHANGELOG")
    autofix_comment_transition_summary: bool = Field(default=True, alias="AUTOFIX_COMMENT_TRANSITION_SUMMARY")
    autofix_comment_action_delta: bool = Field(default=True, alias="AUTOFIX_COMMENT_ACTION_DELTA")
    autofix_comment_top_blocker: bool = Field(default=True, alias="AUTOFIX_COMMENT_TOP_BLOCKER")
    autofix_comment_top_blocker_link: bool = Field(default=True, alias="AUTOFIX_COMMENT_TOP_BLOCKER_LINK")
    autofix_comment_quicklinks: bool = Field(default=True, alias="AUTOFIX_COMMENT_QUICKLINKS")
    autofix_comment_top_check: bool = Field(default=True, alias="AUTOFIX_COMMENT_TOP_CHECK")
    autofix_comment_issue_fallback: bool = Field(default=True, alias="AUTOFIX_COMMENT_ISSUE_FALLBACK")
    autofix_comment_issue_append: bool = Field(default=True, alias="AUTOFIX_COMMENT_ISSUE_APPEND")
    autofix_comment_fail_retry: bool = Field(default=True, alias="AUTOFIX_COMMENT_FAIL_RETRY")
    autofix_comment_fail_retry_max: int = Field(default=3, alias="AUTOFIX_COMMENT_FAIL_RETRY_MAX")
    autofix_comment_fail_retry_base_ms: int = Field(default=600, alias="AUTOFIX_COMMENT_FAIL_RETRY_BASE_MS")
    autofix_comment_issue_update_body: bool = Field(default=True, alias="AUTOFIX_COMMENT_ISSUE_UPDATE_BODY")
    autofix_comment_respect_retry_after: bool = Field(default=True, alias="AUTOFIX_COMMENT_RESPECT_RETRY_AFTER")
    autofix_alert_webhook_url: str = Field(default="", alias="AUTOFIX_ALERT_WEBHOOK_URL")
    autofix_alert_webhook_enabled: bool = Field(default=False, alias="AUTOFIX_ALERT_WEBHOOK_ENABLED")
    autofix_alert_webhook_format: str = Field(default="text", alias="AUTOFIX_ALERT_WEBHOOK_FORMAT")
    autofix_alert_webhook_route_map: str = Field(default="", alias="AUTOFIX_ALERT_WEBHOOK_ROUTE_MAP")

    autofix_issue_history_max: int = Field(default=10, alias="AUTOFIX_ISSUE_HISTORY_MAX")
    autofix_issue_history_in_body: bool = Field(default=True, alias="AUTOFIX_ISSUE_HISTORY_IN_BODY")
    autofix_mergeable_max_wait_seconds: int = Field(default=18, alias="AUTOFIX_MERGEABLE_MAX_WAIT_SECONDS")
    autofix_label_conflict: str = Field(default="autofix-conflict", alias="AUTOFIX_LABEL_CONFLICT")
    autofix_mention_on_conflict: str = Field(default="", alias="AUTOFIX_MENTION_ON_CONFLICT")
    autofix_apply_patches: bool = Field(default=False, alias="AUTOFIX_APPLY_PATCHES")
    autofix_patch_allowlist: str = Field(default="shared/,nexus_supervisor/,docs/,openapi.yaml", alias="AUTOFIX_PATCH_ALLOWLIST")
    autofix_patch_max_files: int = Field(default=5, alias="AUTOFIX_PATCH_MAX_FILES")
    autofix_patch_max_lines: int = Field(default=400, alias="AUTOFIX_PATCH_MAX_LINES")

    task_lock_ttl_seconds: int = Field(default=900, alias="TASK_LOCK_TTL_SECONDS")
    callback_signature_secret: str | None = Field(default=None, alias="CALLBACK_SIGNATURE_SECRET")
    callback_signature_secrets_json: str = Field(default="", alias="CALLBACK_SIGNATURE_SECRETS_JSON")
    # v6.14 rotation automation (optional)
    callback_secret_rotation_enabled: bool = Field(default=False, alias="CALLBACK_SECRET_ROTATION_ENABLED")
    callback_secret_rotation_grace_seconds: int = Field(default=3600, alias="CALLBACK_SECRET_ROTATION_GRACE_SECONDS")
    callback_secret_rotation_source: str = Field(default="env", alias="CALLBACK_SECRET_ROTATION_SOURCE")  # env|file
    callback_signature_secrets_path: str = Field(default="", alias="CALLBACK_SIGNATURE_SECRETS_PATH")  # if source=file
    # v6.14 WORM archive sink (optional, file-based)
    worm_archive_enabled: bool = Field(default=False, alias="WORM_ARCHIVE_ENABLED")
    worm_archive_dir: str = Field(default="", alias="WORM_ARCHIVE_DIR")  # e.g., /mnt/worm
    worm_archive_mode: str = Field(default="on_write", alias="WORM_ARCHIVE_MODE")  # on_write|cron
    worm_manifest_hmac_key: str = Field(default="", alias="WORM_MANIFEST_HMAC_KEY")
    worm_snapshot_gzip: bool = Field(default=True, alias="WORM_SNAPSHOT_GZIP")
    worm_archive_chmod_readonly: bool = Field(default=True, alias="WORM_ARCHIVE_CHMOD_READONLY")
    callback_signature_key_id_header: str = Field(default="x-key-id", alias="CALLBACK_SIGNATURE_KEY_ID_HEADER")
    callback_replay_protection_enabled: bool = Field(default=True, alias="CALLBACK_REPLAY_PROTECTION_ENABLED")
    callback_max_skew_seconds: int = Field(default=300, alias="CALLBACK_MAX_SKEW_SECONDS")
    callback_nonce_ttl_seconds: int = Field(default=900, alias="CALLBACK_NONCE_TTL_SECONDS")
    callback_nonce_store_path: str = Field(default="/tmp/nexus_nonce_store.json", alias="CALLBACK_NONCE_STORE_PATH")
    callback_signature_allow_legacy_body_only: bool = Field(default=True, alias="CALLBACK_SIGNATURE_ALLOW_LEGACY_BODY_ONLY")

    # -----------------
    # v6.3 API management for LLMs (governance)
    # -----------------
    llm_primary_provider: str = Field(default="gemini", alias="LLM_PRIMARY_PROVIDER")
    llm_fallback_providers: str = Field(default="openai,anthropic,glm", alias="LLM_FALLBACK_PROVIDERS")
    llm_request_timeout_s: int = Field(default=60, alias="LLM_REQUEST_TIMEOUT_S")
    llm_max_retries: int = Field(default=2, alias="LLM_MAX_RETRIES")
    llm_rate_limit_rpm: int = Field(default=60, alias="LLM_RATE_LIMIT_RPM")
    llm_rate_limit_rpm_global: int = Field(default=60, alias="LLM_RATE_LIMIT_RPM_GLOBAL")
    llm_rate_limit_rpm_map: str = Field(default="", alias="LLM_RATE_LIMIT_RPM_MAP")
    llm_soft_degrade_max_output_tokens: int = Field(default=256, alias="LLM_SOFT_DEGRADE_MAX_OUTPUT_TOKENS")
    llm_soft_degrade_prefer_cheapest: bool = Field(default=True, alias="LLM_SOFT_DEGRADE_PREFER_CHEAPEST")

    llm_budget_daily_usd: float = Field(default=20.0, alias="LLM_BUDGET_DAILY_USD")
    llm_budget_soft_pct: float = Field(default=0.8, alias="LLM_BUDGET_SOFT_PCT")
    llm_budget_hard_pct: float = Field(default=1.0, alias="LLM_BUDGET_HARD_PCT")

    llm_audit_enabled: bool = Field(default=True, alias="LLM_AUDIT_ENABLED")
    llm_audit_log_path: str = Field(default="logs/llm_audit.jsonl", alias="LLM_AUDIT_LOG_PATH")
    llm_cost_ledger_path: str = Field(default="logs/llm_cost_ledger.jsonl", alias="LLM_COST_LEDGER_PATH")
    llm_pricing_json: str = Field(default="", alias="LLM_PRICING_JSON")
    llm_dedupe_ttl_map: str = Field(default="", alias="LLM_DEDUPE_TTL_MAP")
    llm_default_team: str = Field(default="default", alias="LLM_DEFAULT_TEAM")
    llm_default_project: str = Field(default="nexus", alias="LLM_DEFAULT_PROJECT")
    slack_webhook_url: str = Field(default="", alias="SLACK_WEBHOOK_URL")
    teams_webhook_url: str = Field(default="", alias="TEAMS_WEBHOOK_URL")
    notify_prefer: str = Field(default="slack", alias="NOTIFY_PREFER")
    anomaly_window_min: int = Field(default=15, alias="ANOMALY_WINDOW_MIN")
    anomaly_cost_usd_rate_threshold: float = Field(default=2.0, alias="ANOMALY_COST_USD_RATE_THRESHOLD")
    anomaly_breaker_open_min: int = Field(default=5, alias="ANOMALY_BREAKER_OPEN_MIN")
    anomaly_429_burst_threshold: int = Field(default=20, alias="ANOMALY_429_BURST_THRESHOLD")
    llm_dedupe_enabled: bool = Field(default=True, alias="LLM_DEDUPE_ENABLED")
    llm_dedupe_ttl_s: int = Field(default=30, alias="LLM_DEDUPE_TTL_S")

    # API keys (set via env; never commit)
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    glm_api_key: str = Field(default="", alias="GLM_API_KEY")

    # YouTube Data API (optional; used by youtube.search/play tools)
    youtube_api_key: str = Field(default="", alias="YOUTUBE_API_KEY")
    youtube_default_region: str = Field(default="KR", alias="YOUTUBE_DEFAULT_REGION")
    youtube_default_language: str = Field(default="ko", alias="YOUTUBE_DEFAULT_LANGUAGE")
    youtube_default_risk: str = Field(default="GREEN", alias="YOUTUBE_DEFAULT_RISK")  # GREEN|YELLOW

    # UI stream settings
    stream_event_keep: int = Field(default=2000, alias="STREAM_EVENT_KEEP")
    stream_worklog_keep: int = Field(default=200, alias="STREAM_WORKLOG_KEEP")

    # RAG folder ingest / scheduler (optional)
    rag_auto_ingest_enabled: bool = Field(default=False, alias="RAG_AUTO_INGEST_ENABLED")
    rag_auto_ingest_path: str = Field(default="/data/gdrive_mirror", alias="RAG_AUTO_INGEST_PATH")
    rag_auto_ingest_extensions: str = Field(default="pdf,docx,pptx,xlsx,txt,md,hwp", alias="RAG_AUTO_INGEST_EXTENSIONS")
    rag_auto_ingest_org_id: str = Field(default="default", alias="RAG_AUTO_INGEST_ORG_ID")
    rag_auto_ingest_project_id: str = Field(default="nexus", alias="RAG_AUTO_INGEST_PROJECT_ID")
    rag_auto_ingest_hour: int = Field(default=3, alias="RAG_AUTO_INGEST_HOUR")  # KST
    rag_auto_ingest_minute: int = Field(default=0, alias="RAG_AUTO_INGEST_MINUTE")  # KST
    rag_auto_ingest_max_files: int = Field(default=5000, alias="RAG_AUTO_INGEST_MAX_FILES")
    rag_auto_ingest_max_file_mb: int = Field(default=50, alias="RAG_AUTO_INGEST_MAX_FILE_MB")


    # Optional multi-key rotation (JSON list). If set, overrides single *_API_KEY.
    gemini_api_keys_json: str = Field(default="", alias="GEMINI_API_KEYS_JSON")
    gemini_active_key_id: str = Field(default="", alias="GEMINI_ACTIVE_KEY_ID")
    openai_api_keys_json: str = Field(default="", alias="OPENAI_API_KEYS_JSON")
    openai_active_key_id: str = Field(default="", alias="OPENAI_ACTIVE_KEY_ID")
    anthropic_api_keys_json: str = Field(default="", alias="ANTHROPIC_API_KEYS_JSON")
    anthropic_active_key_id: str = Field(default="", alias="ANTHROPIC_ACTIVE_KEY_ID")
    glm_api_keys_json: str = Field(default="", alias="GLM_API_KEYS_JSON")
    glm_active_key_id: str = Field(default="", alias="GLM_ACTIVE_KEY_ID")

    # Optional endpoint overrides
    gemini_api_base: str = Field(default="https://generativelanguage.googleapis.com/v1beta", alias="GEMINI_API_BASE")
    openai_api_base: str = Field(default="https://api.openai.com/v1", alias="OPENAI_API_BASE")
    anthropic_api_base: str = Field(default="https://api.anthropic.com/v1", alias="ANTHROPIC_API_BASE")
    glm_api_base: str = Field(default="https://open.bigmodel.cn/api/paas/v4", alias="GLM_API_BASE")
    glm_model: str = Field(default="glm-4.7", alias="GLM_MODEL")
    # Anthropic version header (required)
    anthropic_version: str = Field(default="2023-06-01", alias="ANTHROPIC_VERSION")

    # Tenant-scoped credential vault (for SaaS runtime key injection)
    credentials_enabled: bool = Field(default=False, alias="CREDENTIALS_ENABLED")
    credentials_store: str = Field(default="sqlite", alias="CREDENTIALS_STORE")  # sqlite|postgres
    credentials_db_path: str = Field(default="data/credentials.db", alias="CREDENTIALS_DB_PATH")
    credentials_pg_dsn: str = Field(default="", alias="CREDENTIALS_PG_DSN")
    credentials_master_key: str = Field(default="", alias="CREDENTIALS_MASTER_KEY")
    credentials_master_keys_json: str = Field(default="", alias="CREDENTIALS_MASTER_KEYS_JSON")
    credentials_cache_ttl_s: int = Field(default=30, alias="CREDENTIALS_CACHE_TTL_S")

    model_config = {"extra": "ignore"}


settings = Settings()
