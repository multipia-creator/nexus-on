# NEXUS v6.0.0 Release Notes

This release consolidates the operator ergonomics and reliability path built from v5.0 -> v5.9 into a release-ready package.
Primary objective: ensure the operator can always detect/act on failures with minimal clicks, even under GitHub API failures.

Highlights
- PR comment ergonomics:
  - Typed transition summary (CONCLUSION/CHECKS/CONTEXT/GATE/NONE)
  - Top blocker one-liner (missing_contexts > failing checks > gate)
  - next_actions delta (added/removed; order-insensitive)
  - Quick links (PR/Checks/Run)
  - Top failing check (best-effort name+URL)
- Reliability:
  - Retry/backoff for comment post (429/5xx) with optional Retry-After respect
  - Issue fallback with "Latest snapshot" in issue body + optional history via issue comments
  - Webhook 2nd-channel fallback (text or slack_blocks) + repo routing

Config keys (most relevant)
- Comment ergonomics:
  AUTOFIX_COMMENT_TRANSITION_SUMMARY=true
  AUTOFIX_COMMENT_TOP_BLOCKER=true
  AUTOFIX_COMMENT_ACTION_DELTA=true
  AUTOFIX_COMMENT_QUICKLINKS=true
  AUTOFIX_COMMENT_TOP_CHECK=true

- Failure policy:
  AUTOFIX_COMMENT_FAIL_RETRY=true
  AUTOFIX_COMMENT_FAIL_RETRY_MAX=3
  AUTOFIX_COMMENT_FAIL_RETRY_BASE_MS=600
  AUTOFIX_COMMENT_RESPECT_RETRY_AFTER=true

- Issue fallback:
  AUTOFIX_COMMENT_ISSUE_FALLBACK=true
  AUTOFIX_COMMENT_ISSUE_UPDATE_BODY=true
  AUTOFIX_COMMENT_ISSUE_APPEND=true

- Webhook fallback:
  AUTOFIX_ALERT_WEBHOOK_ENABLED=false
  AUTOFIX_ALERT_WEBHOOK_URL=...
  AUTOFIX_ALERT_WEBHOOK_FORMAT=text|slack_blocks
  AUTOFIX_ALERT_WEBHOOK_ROUTE_MAP="repo:org/repo=url;default=url"

Compatibility
- Requires GitHub token with permission to:
  - create PR comments
  - search issues / create issues / create issue comments (for fallback)
- Check-runs query uses GitHub REST API; it is best-effort and gracefully degrades.

