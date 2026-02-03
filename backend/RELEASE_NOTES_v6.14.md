## v6.14.0 Rotation automation + WORM archive option

Security/Ops:
- Adds /ops/rotate_callback_secret to activate a callback signing key id.
- Adds file-backed secret rotation mode (CALLBACK_SECRET_ROTATION_SOURCE=file + CALLBACK_SIGNATURE_SECRETS_PATH).
- Adds optional WORM archive snapshots for audit/cost ledgers (file-based).

Notes:
- This is a dependency-free WORM approximation. For production compliance, use real WORM storage (e.g., S3 Object Lock).
