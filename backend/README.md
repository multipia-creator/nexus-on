# Backend — Device API + AgentReport SSE (v1.2) for Web-first + Windows Companion

Improvements over v1.1:
- Device pairing is now **web-confirmed** without leaking device token to the web UI.
  - Device: `start` -> gets `pairing_code` + `pairing_id` + `device_nonce`
  - Web: `confirm_by_code(pairing_code)` -> returns `device_id` only (no token)
  - Device: `complete(pairing_id, device_nonce)` -> receives `device_id` + `device_token`

SSE:
- `/agent/reports/stream?session_id=...` emits SSE events (`snapshot|report|ping`)
- `data:` payload is a contract-aligned `AgentReport` object
- `meta.event_id` is monotonic per tenant (tenant = `x-org-id:x-project-id`)

## Run
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Optional:
- `CORS_ORIGINS=http://localhost:5173`

## Endpoints (core)
- Device pairing: `POST /devices/pairing/start`, `POST /devices/pairing/confirm_by_code`, `POST /devices/pairing/complete`
- Device sync: `POST /devices/{device_id}/heartbeat`, `GET /devices/{device_id}/commands`, `POST /devices/{device_id}/commands/{command_id}/ack`, `POST /devices/{device_id}/reports`
- SSE: `GET /agent/reports/stream?session_id=...`

## Devtools
- `GET /devtools/devices` (tenant-scoped list)
- `POST /devtools/emit_report` (push synthetic report to SSE)
