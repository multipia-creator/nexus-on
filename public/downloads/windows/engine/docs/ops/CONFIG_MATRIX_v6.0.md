# Config Matrix (v6.0)

| Area | Key | Default | Notes |
|---|---|---:|---|
| Comment | AUTOFIX_COMMENT_TRANSITION_SUMMARY | true | Typed transition line |
| Comment | AUTOFIX_COMMENT_TOP_BLOCKER | true | One-line blocker |
| Comment | AUTOFIX_COMMENT_ACTION_DELTA | true | next_actions delta |
| Comment | AUTOFIX_COMMENT_QUICKLINKS | true | PR/Checks/Run |
| Comment | AUTOFIX_COMMENT_TOP_CHECK | true | Best-effort top failing check |
| Fail policy | AUTOFIX_COMMENT_FAIL_RETRY | true | Retry on 429/5xx |
| Fail policy | AUTOFIX_COMMENT_FAIL_RETRY_MAX | 3 | Max tries |
| Fail policy | AUTOFIX_COMMENT_FAIL_RETRY_BASE_MS | 600 | Backoff base |
| Fail policy | AUTOFIX_COMMENT_RESPECT_RETRY_AFTER | true | Honor Retry-After |
| Issue | AUTOFIX_COMMENT_ISSUE_FALLBACK | true | Create issue if comment fails |
| Issue | AUTOFIX_COMMENT_ISSUE_UPDATE_BODY | true | Keep latest in body |
| Issue | AUTOFIX_COMMENT_ISSUE_APPEND | true | Append history as comments |
| Webhook | AUTOFIX_ALERT_WEBHOOK_ENABLED | false | Enable 2nd channel |
| Webhook | AUTOFIX_ALERT_WEBHOOK_URL | "" | Destination |
| Webhook | AUTOFIX_ALERT_WEBHOOK_FORMAT | text | text or slack_blocks |
| Webhook | AUTOFIX_ALERT_WEBHOOK_ROUTE_MAP | "" | repo routing |
