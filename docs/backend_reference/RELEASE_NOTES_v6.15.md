## v6.15.0 Rotation auto-deactivate + WORM cron snapshots

Callback rotation:
- Secrets support deactivate_at timestamps and automatic expiry reconciliation.
- Adds /ops/reconcile_callback_secrets endpoint.

WORM:
- Adds WORM_ARCHIVE_MODE (on_write|cron)
- Adds tools/worm_snapshot.py and tools/worm_verify_manifest.py for gzip snapshots + signed manifest (HMAC).
