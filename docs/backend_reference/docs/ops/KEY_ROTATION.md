# Key Rotation Runbook (v6.12)

This system supports key rotation for LLM providers without code changes.

## Supported providers
- Gemini
- OpenAI
- Anthropic
- GLM (glm-4.7)

## Config options

### Option A: Single key (legacy)
Set one env var:
- GEMINI_API_KEY
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GLM_API_KEY

### Option B: Multi-key rotation (recommended)
Provide a JSON list of keys and select the active one by ID.

Example (Gemini):
- GEMINI_API_KEYS_JSON='[
  {"id":"k1","key":"<KEY1>","created_at":"2026-01-31","active":true},
  {"id":"k2","key":"<KEY2>","created_at":"2026-02-15","active":false}
]'
- GEMINI_ACTIVE_KEY_ID='k1'

If *_ACTIVE_KEY_ID is empty, the first active=true key is selected.

Equivalent variables exist:
- OPENAI_API_KEYS_JSON / OPENAI_ACTIVE_KEY_ID
- ANTHROPIC_API_KEYS_JSON / ANTHROPIC_ACTIVE_KEY_ID
- GLM_API_KEYS_JSON / GLM_ACTIVE_KEY_ID

## Rotation procedure (safe)
1) Add new key to *_API_KEYS_JSON with `active: false`.
2) Deploy the config change.
3) Flip *_ACTIVE_KEY_ID to the new key ID.
4) Observe: health endpoint, audit log, and provider error rates for 10–30 minutes.
5) If stable, disable the old key in JSON (`active:false`) and revoke it at the provider.

## Evidence / auditability
- LLM audit events include `key_id` and `key_fp` (SHA-256 prefix) to support incident forensics without exposing secrets.
- Append-only hash chains are enabled for audit and cost ledger JSONL files (see `tools/verify_append_only_chain.py`).

## Callback secret rotation
Callback signature uses CALLBACK_SIGNATURE_SECRET.
- Use a maintenance window to rotate; if you must support overlap, deploy with the new secret and keep legacy acceptance enabled:
  CALLBACK_SIGNATURE_ALLOW_LEGACY_BODY_ONLY=true

(Overlapping secrets can be added later if required; current implementation supports one secret at a time.)
