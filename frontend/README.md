# NEXUS UI Skeleton (Assistant Stage → Dock → Dashboard + Sidecar)

## Run
1) Mock server
```bash
cd ../mock_server
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

2) Frontend
```bash
cd ../frontend
npm install
npm run dev
```

## What this pack proves
- UI state is updated **only** by `/agent/reports/stream` (single source of truth).
- `/sidecar/command` and `/approvals/*/decide` return 202 only (acceptance), with follow-up report via stream.
- `ping` event has **no id** and does not advance cursor.
- Replay works via `Last-Event-ID` header (fetch-based SSE, cursor stored in localStorage).
