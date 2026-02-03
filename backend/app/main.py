from __future__ import annotations

import os, time
from typing import Optional, Dict, Any

from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    PairingStartReq, PairingStartResp,
    PairingConfirmByCodeReq, PairingConfirmByCodeResp,
    PairingCompleteReq, PairingCompleteResp,
    HeartbeatReq, CommandsResp, AckReq,
    ReportsPushReq, AgentReport, EmitReportReq,
    DeviceCommand, DevicePolicy, ClientContext
)
from .store import device_store, event_store
from .sse import broadcaster

app = FastAPI(title="NEXUS v2 Backend", version="1.2.0")


# Health check endpoint for Docker
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker healthcheck and monitoring."""
    return {
        "status": "healthy",
        "service": "NEXUS v2 Backend",
        "version": "1.2.0"
    }


def get_tenant(x_org_id: Optional[str], x_project_id: Optional[str]) -> str:
    org = x_org_id or "o"
    proj = x_project_id or "p"
    return f"{org}:{proj}"


cors_origins = os.getenv("CORS_ORIGINS", "")
if cors_origins.strip():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
        allow_credentials=False,
        allow_methods=["*"] ,
        allow_headers=["*"]
    )


def bearer_token(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    return authorization.split(" ", 1)[1].strip()


def device_auth(device_id: str, token: str = Depends(bearer_token)):
    dev = device_store.get_device_by_token(device_id, token)
    if not dev:
        raise HTTPException(status_code=401, detail="invalid device token")
    return dev


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())


def make_empty_snapshot(tenant: str, session_id: str) -> Dict[str, Any]:
    rid = f"snapshot_{tenant}_{session_id}".replace(":", "_")
    return {
        "meta": {
            "mode": "focused",
            "approval_level": "green",
            "confidence": 0.7,
            "report_id": rid,
            "created_at": now_iso(),
            "event_id": 0,
            "tenant": tenant,
            "session_id": session_id,
            "user_id": "u",
            "json_repaired": False,
            "causality": {"correlation_id": "", "command_id": None, "ask_id": None, "type": "snapshot"},
        },
        "done": [],
        "next": [],
        "blocked": [],
        "ask": [],
        "risk": [],
        "rationale": "",
        "undo": [],
        "ui_hint": {"surface": "dashboard", "cards": [], "actions": []},
        "persona_id": "seria.istj",
        "skin_id": "seria.default",
    }


# ---------------- Pairing ----------------

@app.post("/devices/pairing/start", response_model=PairingStartResp)
def pairing_start(req: PairingStartReq, x_org_id: Optional[str] = Header(default=None), x_project_id: Optional[str] = Header(default=None)):
    tenant = get_tenant(x_org_id, x_project_id)
    pairing_id, code, nonce, expires = device_store.start_pairing(tenant, req.device_type, req.device_name, req.capabilities, ttl_sec=300)
    expires_at = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(expires))
    return PairingStartResp(pairing_id=pairing_id, pairing_code=code, device_nonce=nonce, expires_at=expires_at)


@app.post("/devices/pairing/confirm_by_code", response_model=PairingConfirmByCodeResp)
def pairing_confirm_by_code(req: PairingConfirmByCodeReq):
    rec = device_store.confirm_by_code(req.pairing_code)
    if not rec or not rec.device_id:
        raise HTTPException(status_code=400, detail="pairing invalid/expired")
    return PairingConfirmByCodeResp(device_id=rec.device_id)


@app.post("/devices/pairing/complete", response_model=PairingCompleteResp)
def pairing_complete(req: PairingCompleteReq):
    dev = device_store.complete(req.pairing_id, req.device_nonce)
    if not dev:
        raise HTTPException(status_code=404, detail="not confirmed yet or invalid")
    return PairingCompleteResp(device_id=dev.device_id, device_token=dev.device_token)


# ---------------- Device Sync ----------------

@app.post("/devices/{device_id}/heartbeat")
def heartbeat(device_id: str, req: HeartbeatReq, dev=Depends(device_auth)):
    device_store.heartbeat(device_id, req.status)
    return {"ok": True}


@app.get("/devices/{device_id}/commands", response_model=CommandsResp)
def pull_commands(device_id: str, cursor: Optional[str] = None, dev=Depends(device_auth)):
    commands, next_cursor = device_store.list_commands_since(device_id, cursor)
    return CommandsResp(commands=[DeviceCommand(**c) for c in commands], next_cursor=next_cursor)


@app.post("/devices/{device_id}/commands/{command_id}/ack")
def ack_command(device_id: str, command_id: str, req: AckReq, dev=Depends(device_auth)):
    ok = device_store.ack_command(device_id, command_id, req.received_at)
    return {"ok": ok}


@app.post("/devices/{device_id}/reports")
async def push_reports(device_id: str, req: ReportsPushReq, dev=Depends(device_auth)):
    tenant = dev.tenant
    published = []
    for r in req.reports:
        obj = r.model_dump()
        obj.setdefault("meta", {})["tenant"] = tenant
        session_id = obj.get("meta", {}).get("session_id") or "s1"
        obj["meta"]["created_at"] = obj.get("meta", {}).get("created_at") or now_iso()
        ev = event_store.append(tenant, session_id, "report", obj)
        await broadcaster.publish(tenant, session_id, ev)
        published.append(ev.event_id)
    return {"accepted": True, "count": len(published), "event_ids": published}


# ---------------- SSE ----------------

@app.get("/agent/reports/stream")
async def agent_reports_stream(
    request: Request,
    session_id: str,
    x_org_id: Optional[str] = Header(default=None),
    x_project_id: Optional[str] = Header(default=None),
    last_event_id: Optional[str] = Header(default=None, alias="Last-Event-ID"),
):
    tenant = get_tenant(x_org_id, x_project_id)
    try:
        last_id = int(last_event_id) if last_event_id else 0
    except Exception:
        last_id = 0

    # ensure snapshot exists
    snap_obj = make_empty_snapshot(tenant, session_id)
    snap = event_store.ensure_snapshot(tenant, session_id, snap_obj)

    async def gen():
        # If client has no cursor, snapshot should be the first thing they see.
        # Replay is based on event_id > last_id.
        async for chunk in broadcaster.stream(tenant, session_id, last_event_id=last_id):
            if await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(gen(), media_type="text/event-stream")


# ---------------- Devtools ----------------

@app.get("/devtools/devices")
def dev_list_devices(x_org_id: Optional[str] = Header(default=None), x_project_id: Optional[str] = Header(default=None)):
    tenant = get_tenant(x_org_id, x_project_id)
    return {"tenant": tenant, "devices": device_store.list_devices(tenant)}


@app.post("/devtools/emit_report")
async def dev_emit_report(req: EmitReportReq, x_org_id: Optional[str] = Header(default=None), x_project_id: Optional[str] = Header(default=None)):
    tenant = get_tenant(x_org_id, x_project_id)
    report = {
        "meta": {
            "mode": "focused",
            "approval_level": req.approval_level,
            "confidence": 0.8,
            "report_id": f"r_{int(time.time()*1000)}",
            "created_at": now_iso(),
            "event_id": 0,
            "tenant": tenant,
            "session_id": req.session_id,
            "user_id": "u",
            "json_repaired": False,
            "causality": {"correlation_id": "corr-dev", "command_id": None, "ask_id": None, "type": "devtools.emit"},
        },
        "done": [{"title": "devtools", "detail": req.text}] if req.approval_level == "green" else [],
        "next": [{"title": "Next", "detail": "continue", "owner": "Seria", "eta": "now"}],
        "blocked": [],
        "ask": [{"question": "Confirm?", "type": "confirm", "severity": "yellow", "options": ["yes","no"], "default": "yes"}] if req.approval_level == "yellow" else [],
        "risk": [],
        "rationale": "",
        "undo": [],
        "ui_hint": {"surface": "dashboard", "cards": [{"type":"note","title":"devtools","body": req.text}], "actions": []},
        "persona_id": "seria.istj",
        "skin_id": "seria.default",
    }
    ev = event_store.append(tenant, req.session_id, "report", report)
    await broadcaster.publish(tenant, req.session_id, ev)
    return {"accepted": True, "event_id": ev.event_id}
