# Notifications (v6.9)

Webhook support
- Slack Incoming Webhook: SLACK_WEBHOOK_URL
- Teams Incoming Webhook: TEAMS_WEBHOOK_URL
- Preference: NOTIFY_PREFER=slack|teams

Anomaly watch (CLI)
- Detects:
  1) Cost spike over window
  2) 429 burst over window
  3) Circuit breaker open too long (file-backed state)
- Run:
  python tools/anomaly_watch.py

Suggested cron (example)
- Every 5 minutes anomaly detection:
  */5 * * * *  cd /path/to/NEXUS && . .venv/bin/activate && python tools/anomaly_watch.py

Monthly report (example)
- First day of month, last month window:
  0 9 1 * *  cd /path/to/NEXUS && . .venv/bin/activate && python tools/finops_report.py --from 2026-01-01 --to 2026-01-31 --out logs/finops_prev_month.md
