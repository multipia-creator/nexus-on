# WORM Archive (v6.14)

This release adds an optional file-based archive snapshot for:
- logs/llm_audit.jsonl
- logs/llm_cost_ledger.jsonl

## Config
- WORM_ARCHIVE_ENABLED=true
- WORM_ARCHIVE_DIR=/mnt/worm
- WORM_ARCHIVE_CHMOD_READONLY=true

When enabled, each append operation will best-effort copy the current file to the archive dir with a timestamp suffix,
and chmod it read-only (0444). This approximates WORM in single-node environments.

## True WORM (recommended in production)
Use a real WORM store such as:
- S3 Object Lock (compliance mode) + lifecycle rules
- Immutable storage volumes

This code intentionally avoids cloud dependencies; integrate your preferred sync/export pipeline.


## v6.15 cron snapshots + signed manifests
- Set WORM_ARCHIVE_MODE=cron and run tools/worm_snapshot.py via cron.
- Manifests can be HMAC-signed with WORM_MANIFEST_HMAC_KEY and verified using tools/worm_verify_manifest.py.
