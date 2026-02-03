# Webhook Replay Protection (v6.12)

The `/agent/callback` endpoint supports optional HMAC signature verification and replay protection.

## Required headers (recommended)
- X-Signature: hex HMAC-SHA256 signature
- X-Timestamp: unix epoch seconds (string)
- X-Nonce: random unique token (8–128 chars)

## Signature construction (v6.12)
Signature is computed over:

    message = f"{timestamp}.{nonce}.".encode("utf-8") + raw_body_bytes
    signature = hmac_sha256_hex(secret, message)

## Server controls (env)
- CALLBACK_SIGNATURE_SECRET: enable signature verification
- CALLBACK_REPLAY_PROTECTION_ENABLED=true|false
- CALLBACK_MAX_SKEW_SECONDS (default 300)
- CALLBACK_NONCE_TTL_SECONDS (default 900)
- CALLBACK_NONCE_STORE_PATH (file fallback path)
- CALLBACK_SIGNATURE_ALLOW_LEGACY_BODY_ONLY (default true)

If `CALLBACK_SIGNATURE_ALLOW_LEGACY_BODY_ONLY=true`, the server will accept legacy signatures computed over `raw_body_bytes` only. This is intended for migration; turn it off once senders are updated.

## Replay behavior
- Requests with timestamp skew > max skew are rejected (`BAD_TIMESTAMP`).
- Nonce replays within TTL are rejected (`REPLAY_DETECTED`, HTTP 409).
- Nonces are stored in Redis if available, otherwise in a local JSON file (best-effort).
