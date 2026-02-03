# Callback Secret Rotation Runbook (v6.14)

## Goal
Rotate callback signature secrets without downtime by supporting overlapping secrets and optional key-id selection.

## Recommended configuration (file-backed)
1) Store secrets in a file (mounted secret, configmap, etc.)
- CALLBACK_SECRET_ROTATION_SOURCE=file
- CALLBACK_SIGNATURE_SECRETS_PATH=/etc/nexus/callback_secrets.json

2) Configure the secrets file as:
[
  {"id":"k1","secret":"S1","active":true},
  {"id":"k2","secret":"S2","active":false}
]

3) Activate the new key:
POST /ops/rotate_callback_secret
Body: {"active_id":"k2"}

4) Update senders to emit:
- X-Key-Id: k2
- X-Timestamp, X-Nonce, X-Signature (v6.12+ format)

5) After grace window:
- Set old keys active=false and/or revoke externally.

## Env-backed mode
- CALLBACK_SECRET_ROTATION_SOURCE=env
- Server will return updated JSON but cannot persist env vars. You must update deployment config yourself.


## v6.15 auto-deactivate
- Old active keys are tagged with deactivate_at=now+grace_seconds.
- /ops/reconcile_callback_secrets can be called (or rotation called again) to deactivate expired keys automatically.
