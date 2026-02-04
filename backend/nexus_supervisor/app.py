import json
import time
import uuid
import os
import logging
import threading
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Dict, Optional, List, Literal

import pika
from fastapi import FastAPI, Header, HTTPException, Request, Body, Response, Query
from fastapi.responses import PlainTextResponse, StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from shared.settings import settings
from shared.logging_utils import setup_logging
from shared.credential_vault import CredentialVault
from shared.tenant_ctx import TenantCtx

# Import TTS service (with fallback to API Key method)
TTS_ENABLED = False
generate_tts = None

# Try service account method first (recommended)
try:
    from shared.tts_service import generate_tts, tts_service
    if tts_service.enabled:
        TTS_ENABLED = True
        logger.info("✅ TTS service enabled (Google Cloud TTS - Service Account)")
except ImportError:
    logger.warning("⚠️ google-cloud-texttospeech not installed")

# Fallback to API Key method (logger not yet defined, use print)
if not TTS_ENABLED:
    try:
        from shared.tts_service_apikey import generate_tts_with_apikey
        generate_tts = generate_tts_with_apikey
        # Check if API key is available
        if os.getenv("GOOGLE_CLOUD_API_KEY"):
            TTS_ENABLED = True
            print("✅ TTS service enabled (Google Cloud TTS - API Key)")
        else:
            print("⚠️ GOOGLE_CLOUD_API_KEY not set - TTS disabled")
    except Exception as e:
        print(f"⚠️ TTS service fallback failed: {e}")
from shared.pii_mask import mask_sensitive
from shared.llm_client import LLMClient
from shared.task_store import TaskStore
from shared.stream_store import StreamStore
from shared.youtube_client import YouTubeClient
from shared.rag_naive import NaiveRAG
from shared.rag_folder_ingest import RagFolderIngestor
from shared.youtube_queue import YouTubeQueueStore
from shared.play_games import PlayEngine
from shared.security import verify_callback_signature, verify_callback_signature_multi, parse_callback_secrets_json
from shared.callback_rotation import load_callback_secrets, load_rotatable_secrets, rotate_activate_rotatable, dump_rotatable_secrets_json, reconcile_expired, persist_if_file
from shared.nonce_store import NonceStore
# from shared.metrics import TASK_CREATE, TASK_GET, CALLBACK, LLM_GEN, QUEUE_PUBLISH_FAIL, TASK_DURATION  # Disabled for minimal deployment
from shared.mq_utils import declare_queues, publish_json
from shared.node_store import NodeStore
from nexus_supervisor.public_pages_i18n import (
    landing_page as render_landing_page_i18n,
    intro_page as render_intro_page_i18n,
    pricing_page as render_pricing_page_i18n,
    dashboard_preview_page as render_dashboard_page_i18n,
    canvas_preview_page as render_canvas_page_i18n,
    login_page as render_login_page_i18n,
    modules_page as render_modules_page_i18n,
    load_modules_data,
    load_benchmark_data
)

setup_logging()
logger = logging.getLogger("nexus_supervisor")

app = FastAPI(title="NEXUS Supervisor", version="1.13.0")

store = TaskStore(settings.redis_url, settings.task_ttl_seconds)
nonce_store = NonceStore(settings.redis_url, settings.callback_nonce_ttl_seconds, settings.callback_nonce_store_path)
stream_store = StreamStore(settings.redis_url, event_keep=settings.stream_event_keep, worklog_keep=settings.stream_worklog_keep)
youtube_client = YouTubeClient(settings.redis_url, api_key=settings.youtube_api_key)
rag_engine = NaiveRAG(settings.redis_url)
rag_folder_ingestor = RagFolderIngestor(settings.redis_url, rag_engine)
youtube_queue_store = YouTubeQueueStore(settings.redis_url)
play_engine = PlayEngine(settings.redis_url, ttl_seconds=int(os.getenv('PLAY_SESSION_TTL_SECONDS', '86400')))
node_store = NodeStore(settings.redis_url)
callback_secrets = load_callback_secrets(getattr(settings, 'callback_secret_rotation_source', 'env'), getattr(settings, 'callback_signature_secrets_json', '') or '', getattr(settings, 'callback_signature_secrets_path', '') or '')

# Tenant-scoped credential vault + LLM client (KEY03)
vault = CredentialVault.from_settings(settings)
llm_client = LLMClient(vault=vault)

def _utc_now():
    return datetime.now(timezone.utc).isoformat()

def require_admin_key(x_admin_key: Optional[str]):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid admin key"}})

def declare_hold_queue(ch):
    try:
        ch.queue_declare(queue=settings.hold_queue, durable=True)
    except Exception:
        # best-effort
        pass

def declare_alarm_queue(ch):
    try:
        ch.queue_declare(queue=settings.alarm_queue, durable=True)
    except Exception:
        pass



def require_api_key(x_api_key: Optional[str], authorization: Optional[str] = None):
    """Accept either X-API-Key or Authorization: Bearer <token>."""
    token = x_api_key
    if (not token) and authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()
    if token != settings.nexus_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")


class AgentCallbackRequest(BaseModel):
    task_id: str
    status: str = Field(..., pattern="^(running|succeeded|failed)$")
    finished_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None

class TaskCreateRequest(BaseModel):
    requested_by: str = "system"
    params: Optional[Dict[str, Any]] = None

class TaskCreateResponse(BaseModel):
    task_id: str
    task_type: str
    status: str

class LLMGenerateRequest(BaseModel):
    input: str = Field(..., min_length=1)


# ---- BFF / UI contracts (SSE, Sidecar commands, Approvals) ----
CommandType = Literal[
    "draft_email.create",
    "calendar.options.create",
    "calendar.event.book",
    "prep_pack.create",
    "doc.summary.create",
    "external_share.prepare",
    "youtube.search",
    "youtube.play",
    "youtube.queue.add",
    "youtube.queue.next",
    "youtube.queue.list",
    "youtube.queue.clear",
    "rag.ingest",
    "rag.query",
    "rag.folder.ingest",
    "rag.folder.status",
]



class SidecarCommandRequest(BaseModel):
    command_id: str
    type: CommandType
    context: Dict[str, Any] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)
    client_context: Dict[str, Any] = Field(default_factory=dict)


class SidecarCommandAccepted(BaseModel):
    accepted: bool = True
    command_id: str
    first_followup_report_id: Optional[str] = None
    correlation_id: str


DecisionType = Literal["approve", "reject", "revise"]


class ApprovalDecisionRequest(BaseModel):
    decision: DecisionType
    comment: Optional[str] = None
    correlation_id: str


class ApprovalDecisionAccepted(BaseModel):
    accepted: bool = True
    first_followup_report_id: Optional[str] = None
    correlation_id: str

def _rabbit_channel():
    params = pika.URLParameters(settings.rabbitmq_url)
    connection = pika.BlockingConnection(params)
    ch = connection.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    return connection, ch

def publish_task(envelope: Dict[str, Any]) -> None:
    conn, ch = _rabbit_channel()
    try:
        publish_json(ch, settings.task_queue, envelope, correlation_id=envelope["task_id"], headers={"x-retry-count": 0})
    finally:
        conn.close()

@app.get("/health")
def health():
    # hard checks: redis ping, provider, queues declare attempt
    redis_ok = False
    rabbit_ok = False
    try:
        redis_ok = store.ping()
    except Exception:
        redis_ok = False

    try:
        conn, ch = _rabbit_channel()
        conn.close()
        rabbit_ok = True
    except Exception:
        rabbit_ok = False

    return {
        "status": "ok" if (redis_ok and rabbit_ok) else "degraded",
        "time": _utc_now(),
        "llm_provider": settings.llm_provider,
        "redis_ok": redis_ok,
        "rabbit_ok": rabbit_ok,
    }

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ---- Tenant-scoped credentials (SaaS) ----
class CredentialUpsertRequest(BaseModel):
    kind: str = Field(..., description="Credential kind (e.g. llm_gemini_api_key)")
    api_key: str = Field(..., min_length=8)
    label: Optional[str] = Field(default=None, max_length=80)

class CredentialItem(BaseModel):
    kind: str
    label: Optional[str] = None
    last4: str
    fingerprint: str
    updated_at: str

class CredentialListResponse(BaseModel):
    items: List[CredentialItem]

def _tenant_from_headers(x_org_id: Optional[str], x_project_id: Optional[str]) -> TenantCtx:
    return TenantCtx.from_headers(x_org_id, x_project_id)

def _session_id_from_context(context: Dict[str, Any], request_id: str) -> str:
    sid = (context or {}).get("session_id") or ""
    sid = str(sid).strip()
    return sid or (request_id or "default")


def _run_character_chat_core(tenant_id: str, user_input: str, context: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    """
    Shared chat core used by:
      - /character/chat (direct call)
      - /chat/send (UI-driven; emits SSE reports)

    If decision.mode == 'play', bypass LLM and delegate to PlayEngine for deterministic '놀아주기'.
    """
    from shared.character.state_engine import CharacterContext, decide_state
    from shared.character.presence import presence_to_live2d
    from shared.json_guard import validate, repair

    c = context or {}
    ctx = CharacterContext(
        intimacy=int(c.get("intimacy", 0) or 0),
        jealousy_level=int(c.get("jealousy_level", 0) or 0),
        sexy_blocked=bool(c.get("sexy_blocked", False)),
        sexy_cooldown_seconds=int(c.get("sexy_cooldown_seconds", 0) or 0),
        user_opt_out_sexy=bool(c.get("user_opt_out_sexy", False)),
        task_busy=bool(c.get("task_busy", False)),
        tool_allowlist_active=bool(c.get("tool_allowlist_active", True)),
    )

    decision = decide_state(user_input, ctx)
    rid = request_id or str(uuid.uuid4())
    presence = presence_to_live2d(rid, decision, ctx)

    # If tools requested, we downgrade to confirm (no auto execution here)
    confirm_card = None
    if decision.requires_confirm:
        confirm_card = {
            "title": "승인 필요",
            "summary": "도구 실행/외부 변경이 포함될 수 있어 사용자 승인이 필요합니다.",
            "action": "confirm_tool_execution",
            "requires_user_confirm": True,
        }

    # PLAY MODE: deterministic "놀아주기"
    if decision.mode == "play":
        sid = _session_id_from_context(c, rid)
        pr = play_engine.handle(tenant_id, sid, user_input)
        payload = {
            "mode": "play",
            "text": pr.text,
            "confirm_card": confirm_card,
            "presence_packet": presence,
        }
        validate("chat_response", payload)
        return payload

    # Prompt model to output chat_response JSON only.
    prompt = f"""You MUST output ONLY valid JSON object. No markdown. No code fences. No explanation.
Schema name: chat_response
Constraints:
- mode must be one of friendly|focused|sexy|jealous|busy|play
- presence_packet must be an object and MUST include keys: version,state,timing,gaze,breath,blink,params
- text must be Korean and concise. Be polite.
- If confirm_card is present, keep it unchanged.
- Use the provided presence_packet as-is.

Input:
user_input: {user_input}
decision_mode: {decision.mode}
presence_packet: {json.dumps(presence, ensure_ascii=False)}
confirm_card: {json.dumps(confirm_card, ensure_ascii=False)}

Output: """

    model_key = vault.get_llm_key(tenant_id)
    llm = llm_client.for_tenant(tenant_id, model_key=model_key)
    raw = llm.generate(prompt, max_tokens=700)
    repaired = repair(raw)
    obj = validate("chat_response", repaired, return_obj=True)

    # enforce presence + confirm_card from local decisions
    obj["presence_packet"] = presence
    if confirm_card:
        obj["confirm_card"] = confirm_card

    return obj


@app.post("/ops/credentials/upsert")
def ops_credentials_upsert(
    body: CredentialUpsertRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)

    tenant = _tenant_from_headers(x_org_id, x_project_id)
    tenant = _tenant_from_headers(x_org_id, x_project_id)
    if not vault.enabled:
        raise HTTPException(status_code=503, detail="Credential vault disabled (set CREDENTIALS_ENABLED=true and provide CREDENTIALS_MASTER_KEY(S)).")
    rec = vault.upsert(org_id=tenant.org_id, project_id=tenant.project_id, kind=body.kind, plaintext=body.api_key, label=body.label)
    return {**rec.to_public(), "org_id": tenant.org_id, "project_id": tenant.project_id}

@app.get("/ops/credentials/list", response_model=CredentialListResponse)
def ops_credentials_list(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)
    tenant = _tenant_from_headers(x_org_id, x_project_id)
    if not vault.enabled:
        return {"items": []}
    items = [CredentialItem(**r.to_public()) for r in vault.list(org_id=tenant.org_id, project_id=tenant.project_id)]
    return {"items": items}

@app.delete("/ops/credentials/delete")
def ops_credentials_delete(
    kind: str,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)
    tenant = _tenant_from_headers(x_org_id, x_project_id)
    if not vault.enabled:
        return {"deleted": False, "kind": kind}
    deleted = vault.delete(org_id=tenant.org_id, project_id=tenant.project_id, kind=kind)
    return {"deleted": bool(deleted), "kind": kind}

@app.post("/ops/credentials/test")
def ops_credentials_test(
    payload: Dict[str, Any] = Body(default_factory=dict),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)
    tenant = _tenant_from_headers(x_org_id, x_project_id)
    provider = str(payload.get("provider") or "").strip().lower()
    kind = str(payload.get("kind") or "").strip()
    # Infer provider from kind if not provided
    if not provider and kind:
        if kind.endswith("gemini_api_key"):
            provider = "gemini"
        elif kind.endswith("openai_api_key"):
            provider = "openai"
        elif kind.endswith("anthropic_api_key"):
            provider = "anthropic"
        elif kind.endswith("glm_api_key"):
            provider = "glm"
    if not provider:
        raise HTTPException(status_code=400, detail="provider (or kind) is required")
    # This call uses the tenant-scoped vault key via runtime injection.
    res = llm_client.generate(
        "ping",
        provider_override=provider,
        purpose="credential_test",
        max_tokens=1,
        timeout_s=10,
        cache_ttl_s=0,
        tenant=tenant,
    )
    return {"ok": bool(res.ok), "provider": provider, "latency_ms": int(res.latency_ms or 0), "error": res.error}


@app.post("/excel-kakao", response_model=TaskCreateResponse)
def create_excel_kakao(req: TaskCreateRequest, request: Request, x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    require_api_key(x_api_key, authorization)

    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "task_type": "excel_kakao",
        "status": "queued",
        "requested_by": req.requested_by,
        "requested_at": _utc_now(),
        "finished_at": None,
        "result": None,
        "error": None,
        "retry_count": 0,
        "last_error": None,
    }
    store.put(task_id, task)

    envelope = {
        "task_id": task_id,
        "task_type": "excel_kakao",
        "requested_by": req.requested_by,
        "requested_at": task["requested_at"],
        "payload": req.payload,
    }

    TASK_CREATE.labels(task_type="excel_kakao").inc()

    masked = mask_sensitive(envelope)
    client_ip = request.client.host if request.client else "unknown"
    logger.info(json.dumps({"event":"TASK_CREATE","ip":client_ip,"task_id":task_id,"task_type":"excel_kakao","payload":masked}, ensure_ascii=False))

    try:
        publish_task(envelope)
    except Exception as e:
        QUEUE_PUBLISH_FAIL.labels(task_type="excel_kakao").inc()
        store.update(task_id, {"status": "failed", "error": {"code": "QUEUE_PUBLISH_FAIL", "message": str(e)}})
        raise HTTPException(status_code=500, detail={"error": {"code": "QUEUE_PUBLISH_FAIL", "message": "Failed to publish task"}})

    return TaskCreateResponse(task_id=task_id, status="queued")

@app.get("/tasks/{task_id}")
def get_task(task_id: str, x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    require_api_key(x_api_key, authorization)
    task = store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Task not found"}})
    TASK_GET.labels(task_type=task.get("task_type","unknown")).inc()
    return task

@app.post("/agent/callback")
async def agent_callback(request: Request, x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None), x_signature: Optional[str] = Header(None)):
    require_api_key(x_api_key, authorization)
    body = await request.body()

    # optional HMAC signature verify (+ replay protection)
    if settings.callback_signature_secret or callback_secrets:
        # Replay protection headers (recommended):
        #  - X-Timestamp: unix epoch seconds (string)
        #  - X-Nonce: random unique token per request
        #  - X-Key-Id: optional selector for secret rotation
        x_timestamp = request.headers.get("x-timestamp")
        x_nonce = request.headers.get("x-nonce")

        if bool(getattr(settings, "callback_replay_protection_enabled", True)):
            # timestamp skew check
            try:
                ts = int(str(x_timestamp or "0"))
            except Exception:
                ts = 0
            now = int(time.time())
            skew = abs(now - ts)
            max_skew = int(getattr(settings, "callback_max_skew_seconds", 300) or 300)
            if ts <= 0 or skew > max_skew:
                raise HTTPException(status_code=401, detail={"error": {"code": "BAD_TIMESTAMP", "message": "Callback timestamp invalid or skew too large"}})

            # nonce replay check
            nonce = (x_nonce or "").strip()
            if len(nonce) < 8 or len(nonce) > 128:
                raise HTTPException(status_code=401, detail={"error": {"code": "BAD_NONCE", "message": "Callback nonce missing/invalid"}})
            if nonce_store.seen_or_mark(nonce):
                raise HTTPException(status_code=409, detail={"error": {"code": "REPLAY_DETECTED", "message": "Callback replay detected"}})

        allow_legacy = bool(getattr(settings, "callback_signature_allow_legacy_body_only", True))
        key_id_header = str(getattr(settings, "callback_signature_key_id_header", "x-key-id") or "x-key-id").lower()
        x_key_id = request.headers.get(key_id_header)

        # Prefer multi-secret verification if CALLBACK_SIGNATURE_SECRETS_JSON is configured.
        if callback_secrets:
            ok, matched = verify_callback_signature_multi(
                secrets=callback_secrets,
                body_bytes=body,
                provided=x_signature,
                timestamp=x_timestamp,
                nonce=x_nonce,
                key_id=x_key_id,
                allow_legacy_body_only=allow_legacy,
            )
            if not ok:
                raise HTTPException(status_code=401, detail={"error": {"code": "BAD_SIGNATURE", "message": "Invalid callback signature"}})
        else:
            if not verify_callback_signature(settings.callback_signature_secret, body, x_signature, timestamp=x_timestamp, nonce=x_nonce, allow_legacy_body_only=allow_legacy):
                raise HTTPException(status_code=401, detail={"error": {"code": "BAD_SIGNATURE", "message": "Invalid callback signature"}})

    cb = AgentCallbackRequest(**json.loads(body.decode("utf-8")))

    task = store.get(cb.task_id)
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Task not found"}})

    patch: Dict[str, Any] = {"status": "running" if cb.status == "running" else cb.status}
    if cb.status in ("succeeded", "failed"):
        patch["finished_at"] = cb.finished_at or _utc_now()
    if cb.result is not None:
        patch["result"] = cb.result
    if cb.error is not None:
        patch["error"] = cb.error
        patch["last_error"] = cb.error

    # metrics: duration if present
    if cb.metrics and isinstance(cb.metrics, dict):
        dur_ms = cb.metrics.get("duration_ms")
        if isinstance(dur_ms, int) and dur_ms >= 0:
            TASK_DURATION.labels(task_type=task.get("task_type","unknown")).observe(dur_ms / 1000.0)

    updated = store.update(cb.task_id, patch)
    CALLBACK.labels(status=cb.status).inc()

    masked = mask_sensitive({"task_id": cb.task_id, "status": cb.status, "result": cb.result, "error": cb.error, "metrics": cb.metrics})
    logger.info(json.dumps({"event":"TASK_UPDATE", **masked}, ensure_ascii=False))
    return {"ok": True, "task_id": cb.task_id, "status": updated["status"] if updated else cb.status}

@app.post("/ops/rotate_callback_secret")
async def rotate_callback_secret(req: Request, x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    """Rotate callback secret by activating a key id.

    Body: {"active_id":"k2"}
    - If rotation_source=file, updates the secrets file at CALLBACK_SIGNATURE_SECRETS_PATH.
    - Also reconciles expired keys on each call (auto-deactivate after grace).
    """
    require_api_key(x_api_key, authorization)
    body = await req.json()
    active_id = str(body.get("active_id") or "").strip()
    if not active_id:
        raise HTTPException(status_code=400, detail={"error":{"code":"BAD_REQUEST","message":"active_id required"}})

    src = str(getattr(settings, "callback_secret_rotation_source", "env") or "env")
    path = str(getattr(settings, "callback_signature_secrets_path", "") or "")

    secrets = load_rotatable_secrets(
        src,
        getattr(settings, "callback_signature_secrets_json", "") or "",
        path,
    )

    # reconcile expired before rotate
    secrets, changed = reconcile_expired(secrets)
    if changed:
        persist_if_file(src, path, secrets)

    updated, msg = rotate_activate_rotatable(secrets, active_id, grace_seconds=int(getattr(settings,"callback_secret_rotation_grace_seconds",3600) or 3600))
    json_out = dump_rotatable_secrets_json(updated)

    if src.lower() == "file":
        if not path:
            raise HTTPException(status_code=500, detail={"error":{"code":"MISCONFIG","message":"CALLBACK_SIGNATURE_SECRETS_PATH required for file rotation"}})
        try:
            persist_if_file(src, path, updated)
        except Exception as e:
            raise HTTPException(status_code=500, detail={"error":{"code":"WRITE_FAILED","message":str(e)}})

    return {"ok": True, "message": msg, "source": src, "secrets_json": json_out}

@app.post("/ops/reconcile_callback_secrets")
async def reconcile_callback_secrets(x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    """Deactivate expired callback secrets based on deactivate_at timestamps.

    Only persists when CALLBACK_SECRET_ROTATION_SOURCE=file.
    """
    require_api_key(x_api_key, authorization)
    src = str(getattr(settings, "callback_secret_rotation_source", "env") or "env")
    path = str(getattr(settings, "callback_signature_secrets_path", "") or "")
    secrets = load_rotatable_secrets(src, getattr(settings, "callback_signature_secrets_json", "") or "", path)
    secrets, changed = reconcile_expired(secrets)
    if changed:
        persist_if_file(src, path, secrets)
    return {"ok": True, "changed": bool(changed), "source": src, "count": len(secrets)}
@app.get("/alarm/peek")
def alarm_peek(limit: int = 10, x_admin_key: Optional[str] = Header(None)):
    """Peek messages from ALARM queue (best-effort)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 50))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)
    declare_alarm_queue(ch)

    out = []
    scanned = 0
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.alarm_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            out.append({"correlation_id": getattr(props, "correlation_id", None), "headers": headers, "message": msg})
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(out), "scanned": scanned, "items": out}


@app.post("/alarm/purge")
def alarm_purge(limit: int = 1000, dry_run: bool = False, x_admin_key: Optional[str] = Header(None)):
    """Purge ALARM queue messages (best-effort)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 5000))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)
    declare_alarm_queue(ch)

    purged = 0
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.alarm_queue, auto_ack=False)
            if not method_frame:
                break
            if dry_run:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                purged += 1
                continue
            ch.basic_ack(method_frame.delivery_tag)
            purged += 1
    finally:
        conn.close()

    return {"purged": purged, "dry_run": dry_run}

@app.post("/hold/fix_pr_ci")
def hold_fix_pr_ci(limit: int = 1, provider: str = "anthropic", dry_run: bool = False,
                   apply_patches: bool = False, allowlist: str = "", max_files: int = 5, max_lines: int = 400,
                   x_admin_key: Optional[str] = Header(None)):
    """Create PR from HOLD, optionally apply patches, dispatch CI, and comment result back to PR."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 1))  # single item per call to keep runtime bounded

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    out = []
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            fc = extract_failure_code(headers, msg) or "unknown"

            if dry_run:
                out.append({"dry_run": True, "failure_code": fc, "provider": provider})
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue

            allow = [p.strip() for p in allowlist.split(",") if p.strip()] if allowlist else None
            res = create_fix_pr_and_ci(msg, fc, provider_override=(provider or None),
                                       apply_patches=apply_patches, allowlist=allow,
                                       max_files=max_files, max_lines=max_lines)
            out.append({
                "dry_run": False,
                "failure_code": fc,
                "provider": provider,
                "ok": res.ok,
                "pr_url": res.pr_url,
                "workflow_run_url": (res.run.run_url if res.run else None),
                "status": (res.run.status if res.run else None),
                "conclusion": (res.run.conclusion if res.run else None),
                "comment_url": res.comment_url,
                "error": res.error,
            })
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(out), "items": out}

@app.post("/hold/fix_pr")
def hold_fix_pr(limit: int = 1, provider: str = "anthropic", dry_run: bool = False, apply_patches: bool = False, allowlist: str = "", max_files: int = 5, max_lines: int = 400, x_admin_key: Optional[str] = Header(None)):
    """Create GitHub PRs from HOLD with an auto-generated fix suggestion (adds markdown file)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 2))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    out = []
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            fc = extract_failure_code(headers, msg) or "unknown"

            if dry_run:
                out.append({"dry_run": True, "failure_code": fc, "provider": provider})
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue

            allow = [p.strip() for p in allowlist.split(",") if p.strip()] if allowlist else None
            res = create_fix_pr_from_hold(msg, fc, provider_override=(provider or None), apply_patches=apply_patches, allowlist=allow, max_files=max_files, max_lines=max_lines)
            out.append({
                "dry_run": False,
                "failure_code": fc,
                "provider": provider,
                "ok": res.ok,
                "pr_url": (res.pr.pr_url if res.pr else None),
                "branch": (res.pr.branch if res.pr else None),
                "md_path": res.md_path,
                "error": res.error,
            })
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(out), "items": out}

@app.post("/hold/fix_issue")
def hold_fix_issue(limit: int = 1, provider: str = "anthropic", dry_run: bool = False, x_admin_key: Optional[str] = Header(None)):
    """Create GitHub issues from HOLD with an auto-generated fix suggestion."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 3))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    out = []
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            fc = extract_failure_code(headers, msg) or "unknown"

            if dry_run:
                out.append({"dry_run": True, "failure_code": fc, "provider": provider})
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue

            res = create_fix_issue_from_hold(msg, fc, provider_override=(provider or None))
            out.append({
                "dry_run": False,
                "failure_code": fc,
                "provider": provider,
                "ok": res.ok,
                "issue_url": (res.issue.url if res.issue else None),
                "error": res.error,
                "suggestion": res.suggestion,
            })
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(out), "items": out}

@app.post("/hold/github_issue")
def hold_github_issue(limit: int = 1, dry_run: bool = False, x_admin_key: Optional[str] = Header(None)):
    """Create GitHub issues from HOLD messages (schema/prompt fix tickets)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 5))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    created = []
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))

            tpl = build_hold_pr(msg, headers=headers)
            if dry_run:
                created.append({"dry_run": True, "title": tpl.title})
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue

            res = create_issue(tpl.title, tpl.body, labels=["hold", "schema"])
            created.append({"dry_run": False, "title": tpl.title, "ok": res.ok, "url": res.url, "error": res.error})
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(created), "items": created}

@app.get("/hold/suggest_fix")
def hold_suggest_fix(limit: int = 1, provider: str = "", x_admin_key: Optional[str] = Header(None)):
    """Generate fix suggestions (prompt/schema/code) for HOLD messages using selected LLM provider."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 3))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    out = []
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            fc = extract_failure_code(headers, msg) or "unknown"
            r = suggest_fix(msg, fc, provider_override=(provider or None))
            out.append({"failure_code": fc, "ok": r.ok, "provider": r.provider, "model": r.model, "repaired": r.repaired, "attempts": r.attempts, "data": r.data, "error": r.error})
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(out), "items": out}

@app.get("/hold/pr")
def hold_pr(limit: int = 1, x_admin_key: Optional[str] = Header(None)):
    """Generate a PR template for the first HOLD message (best-effort). Does not modify the queue."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 5))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    templates = []
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            # generate template
            tpl = build_hold_pr(msg, headers=headers)
            templates.append({"title": tpl.title, "body": tpl.body})
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(templates), "items": templates}

@app.get("/hold/peek")
def hold_peek(limit: int = 10, x_admin_key: Optional[str] = Header(None)):
    """Peek messages from HOLD queue (best-effort)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 50))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    out = []
    scanned = 0
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            out.append({"correlation_id": getattr(props, "correlation_id", None), "headers": headers, "message": msg})
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    return {"count": len(out), "scanned": scanned, "items": out}


@app.post("/hold/purge")
def hold_purge(limit: int = 1000, dry_run: bool = False, x_admin_key: Optional[str] = Header(None)):
    """Purge HOLD queue messages (best-effort)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 5000))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    purged = 0
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.hold_queue, auto_ack=False)
            if not method_frame:
                break
            if dry_run:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                purged += 1
                continue
            ch.basic_ack(method_frame.delivery_tag)
            purged += 1
    finally:
        conn.close()

    return {"purged": purged, "dry_run": dry_run}

@app.get("/dlq/stats")
def dlq_stats(sample: int = 200, x_admin_key: Optional[str] = Header(None)):
    """Best-effort DLQ stats by failure_code/task_type. Non-destructive scan with bounded work."""
    require_admin_key(x_admin_key)
    sample = max(10, min(sample, 2000))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)

    by_code = {}
    by_type = {}
    scanned = 0

    try:
        for _ in range(sample):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))

            # Age window safety
            max_age = int(getattr(settings, "dlq_apply_max_age_seconds", 7200))
            failed_at = (msg.get("failed_at") or (msg.get("failure") or {}).get("failed_at") or "")
            if failed_at:
                try:
                    dt = datetime.fromisoformat(str(failed_at).replace("Z", "+00:00"))
                    age = (datetime.now(timezone.utc) - dt).total_seconds()
                    if age > max_age:
                        ch.basic_nack(method_frame.delivery_tag, requeue=True)
                        continue
                except Exception:
                    pass

            fc = extract_failure_code(headers, msg) or "unknown"
            tt = extract_task_type(msg)

            by_code[fc] = by_code.get(fc, 0) + 1
            by_type[tt] = by_type.get(tt, 0) + 1

            # requeue (non-destructive)
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    # sort descending
    by_code = dict(sorted(by_code.items(), key=lambda kv: kv[1], reverse=True))
    by_type = dict(sorted(by_type.items(), key=lambda kv: kv[1], reverse=True))

    return {"scanned": scanned, "by_failure_code": by_code, "by_task_type": by_type}

@app.post("/alerts/test")
def alerts_test(x_admin_key: Optional[str] = Header(None)):
    """Send a test alert to configured webhook."""
    require_admin_key(x_admin_key)
    from shared.alerter import send_webhook
    res = send_webhook("test", {"ts": time.time(), "service": "nexus_supervisor"})
    return {"ok": res.ok, "status_code": res.status_code, "error": res.error}

@app.post("/dlq/apply")
def dlq_apply(sample: int = 500, dry_run: bool = False, send_alert: bool = True, max_requeue: int = 200, max_hold: int = 200, max_alarm: int = 50, x_admin_key: Optional[str] = Header(None)):
    """Apply triage policy to DLQ: requeue transient, route schema to HOLD, route auth/disabled to ALARM. Best-effort scan."""
    require_admin_key(x_admin_key)
    sample = max(10, min(sample, 5000))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)
    declare_alarm_queue(ch)

    scanned = 0
    acted = {"requeue": 0, "hold": 0, "alarm": 0, "ignore": 0}
    alerted = 0

    try:
        for _ in range(sample):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))

            # Age window safety
            max_age = int(getattr(settings, "dlq_apply_max_age_seconds", 7200))
            failed_at = (msg.get("failed_at") or (msg.get("failure") or {}).get("failed_at") or "")
            if failed_at:
                try:
                    dt = datetime.fromisoformat(str(failed_at).replace("Z", "+00:00"))
                    age = (datetime.now(timezone.utc) - dt).total_seconds()
                    if age > max_age:
                        ch.basic_nack(method_frame.delivery_tag, requeue=True)
                        continue
                except Exception:
                    pass

            fc = extract_failure_code(headers, msg) or "unknown"
            decision = triage_failure_code(fc)
            action = decision.action
            # Safety caps (prevent large accidental moves)
            if action == "requeue" and acted["requeue"] >= max_requeue:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue
            if action == "hold" and acted["hold"] >= max_hold:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue
            if action == "alarm" and acted["alarm"] >= max_alarm:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue

            if dry_run:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                acted[action] = acted.get(action, 0) + 1
                continue

            correlation_id = getattr(props, "correlation_id", None) or msg.get("task_id", "unknown")

            if action == "requeue":
                # publish back to main queue; keep headers and reset retry counter
                h = dict(headers or {})
                h["x-retry-count"] = 0
                publish_json(ch, settings.task_queue, msg, correlation_id=correlation_id, headers=h)
                ch.basic_ack(method_frame.delivery_tag)
                acted["requeue"] += 1
                continue

            if action == "hold":
                publish_json(ch, settings.hold_queue, msg, correlation_id=correlation_id, headers=headers)
                ch.basic_ack(method_frame.delivery_tag)
                acted["hold"] += 1
                continue

            if action == "alarm":
                publish_json(ch, settings.alarm_queue, msg, correlation_id=correlation_id, headers=headers)
                ch.basic_ack(method_frame.delivery_tag)
                acted["alarm"] += 1
                if send_alert:
                    try:
                        from shared.alerter import send_webhook
                        rb = get_runbook(fc)
                        dedupe = AlertDedupe()
                        dedupe_key = f"{extract_task_type(msg)}:{fc}"
                        d = dedupe.allow(dedupe_key)
                        if d.allowed:
                            res = send_webhook("dlq_alarm", {"failure_code": fc, "task_id": correlation_id, "task_type": extract_task_type(msg), "runbook": rb, "dedupe_ttl": d.ttl_seconds})
                            if getattr(res, 'ok', False):
                                alerted += 1
                    except Exception:
                        pass
                continue

            # ignore: keep in DLQ
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
            acted["ignore"] += 1

    finally:
        conn.close()

    return {"scanned": scanned, "dry_run": dry_run, "send_alert": send_alert, "acted": acted, "alerted": alerted}

@app.post("/dlq/alarm")
def dlq_alarm(limit: int = 100, mode: str = "auto", dry_run: bool = False, send_alert: bool = True, x_admin_key: Optional[str] = Header(None)):
    """Move DLQ messages to ALARM queue based on triage policy (mode=auto) and optionally send webhook alerts."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 500))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)
    declare_alarm_queue(ch)

    moved = 0
    scanned = 0
    alerted = 0

    try:
        max_scan = limit * 50
        for _ in range(max_scan):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            fc = extract_failure_code(headers, msg) or "unknown"

            if mode.lower() == "auto":
                decision = triage_failure_code(fc)
                if decision.action != "alarm":
                    ch.basic_nack(method_frame.delivery_tag, requeue=True)
                    continue

            if dry_run:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                moved += 1
                if moved >= limit:
                    break
                continue

            correlation_id = getattr(props, "correlation_id", None) or msg.get("task_id", "unknown")
            publish_json(ch, settings.alarm_queue, msg, correlation_id=correlation_id, headers=headers)
            ch.basic_ack(method_frame.delivery_tag)
            moved += 1

            if send_alert:
                try:
                    from shared.alerter import send_webhook
                    rb = get_runbook(fc)
                    dedupe = AlertDedupe()
                    dedupe_key = f"{extract_task_type(msg)}:{fc}"
                    d = dedupe.allow(dedupe_key)
                    if not d.allowed:
                        res = None
                    else:
                        res = send_webhook("dlq_alarm", {"failure_code": fc, "task_id": correlation_id, "task_type": extract_task_type(msg), "runbook": rb, "dedupe_ttl": d.ttl_seconds})
                    if res.ok:
                        alerted += 1
                except Exception:
                    pass

            if moved >= limit:
                break
    finally:
        conn.close()

    return {"moved": moved, "scanned": scanned, "dry_run": dry_run, "send_alert": send_alert, "alerted": alerted}

@app.post("/dlq/route")
def dlq_route(limit: int = 100, mode: str = "auto", dry_run: bool = False, x_admin_key: Optional[str] = Header(None)):
    """Move DLQ messages to HOLD queue based on triage policy (mode=auto)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 500))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    declare_hold_queue(ch)

    moved = 0
    scanned = 0
    try:
        max_scan = limit * 50
        for _ in range(max_scan):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            fc = extract_failure_code(headers, msg) or "unknown"

            if mode.lower() == "auto":
                decision = triage_failure_code(fc)
                if decision.action != "hold":
                    ch.basic_nack(method_frame.delivery_tag, requeue=True)
                    continue

            if dry_run:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                moved += 1
                if moved >= limit:
                    break
                continue

            # publish into HOLD queue, then ack DLQ message
            correlation_id = getattr(props, "correlation_id", None) or msg.get("task_id", "unknown")
            publish_json(ch, settings.hold_queue, msg, correlation_id=correlation_id, headers=headers)
            ch.basic_ack(method_frame.delivery_tag)
            moved += 1
            if moved >= limit:
                break
    finally:
        conn.close()

    return {"moved": moved, "scanned": scanned, "mode": mode, "dry_run": dry_run}

@app.get("/dlq/triage")
def dlq_triage(sample: int = 200, x_admin_key: Optional[str] = Header(None)):
    """Non-destructive DLQ triage based on policy rules. Returns counts by action and top codes."""
    require_admin_key(x_admin_key)
    sample = max(10, min(sample, 2000))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)

    counts = {"requeue": 0, "hold": 0, "alarm": 0, "ignore": 0}
    by_code = {}
    scanned = 0

    try:
        for _ in range(sample):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))
            fc = extract_failure_code(headers, msg) or "unknown"

            decision = triage_failure_code(fc)
            counts[decision.action] = counts.get(decision.action, 0) + 1
            by_code[fc] = by_code.get(fc, 0) + 1

            ch.basic_nack(method_frame.delivery_tag, requeue=True)
    finally:
        conn.close()

    by_code = dict(sorted(by_code.items(), key=lambda kv: kv[1], reverse=True))
    return {"scanned": scanned, "counts": counts, "by_failure_code": by_code}

@app.get("/dlq/peek")
def dlq_peek(limit: int = 10, failure_code: Optional[str] = None, task_type: Optional[str] = None, x_admin_key: Optional[str] = Header(None)):
    """Peek messages from DLQ without removing them (best-effort). Supports simple filters."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 50))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)

    out = []
    scanned = 0
    max_scan = limit * 20  # bounded scan to allow filtering without losing messages

    try:
        for _ in range(max_scan):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            headers = (props.headers or {}) if props else {}
            msg = json.loads(body.decode("utf-8"))

            # filter
            fc = extract_failure_code(headers, msg)
            if failure_code and (fc != failure_code):
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue
            tt = extract_task_type(msg)
            if task_type and (tt != task_type):
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                continue

            out.append({
                "delivery_tag": method_frame.delivery_tag,
                "correlation_id": getattr(props, "correlation_id", None),
                "headers": headers,
                "message": msg,
            })
            ch.basic_nack(method_frame.delivery_tag, requeue=True)
            if len(out) >= limit:
                break
    finally:
        conn.close()

    return {"count": len(out), "scanned": scanned, "items": out}


@app.post("/dlq/requeue")
def dlq_requeue(limit: int = 10, dry_run: bool = False, mode: str = "manual", x_admin_key: Optional[str] = Header(None)):
    """Move up to N messages from DLQ back to main task queue.

    - mode=manual: requeue everything up to limit
    - mode=auto: only requeue items whose triage policy action is 'requeue'
    """
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 200))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)

    moved = 0
    scanned = 0
    try:
        for _ in range(limit * 50):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            scanned += 1
            msg = json.loads(body.decode("utf-8"))
            correlation_id = getattr(props, "correlation_id", None) or msg.get("task_id", "unknown")
            headers = (props.headers or {}) if props else {}

            if mode.lower() == "auto":
                fc_auto = extract_failure_code(headers, msg) or "unknown"
                decision = triage_failure_code(fc_auto)
                if decision.action != "requeue":
                    ch.basic_nack(method_frame.delivery_tag, requeue=True)
                    continue

            if dry_run:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                moved += 1
                if moved >= limit:
                    break
                continue

            # reset retry counter on requeue
            headers["x-retry-count"] = 0
            publish_json(ch, settings.task_queue, msg, correlation_id=correlation_id, headers=headers)
            ch.basic_ack(method_frame.delivery_tag)
            moved += 1
            if moved >= limit:
                break
    finally:
        conn.close()

    logger.info(json.dumps({"event": "DLQ_REQUEUE", "scanned": scanned, "moved": moved, "dry_run": dry_run, "mode": mode}, ensure_ascii=False))
    return {"scanned": scanned, "moved": moved, "dry_run": dry_run, "mode": mode}

@app.post("/dlq/purge")
def dlq_purge(limit: int = 1000, x_admin_key: Optional[str] = Header(None)):
    """Purge up to N messages from DLQ (destructive)."""
    require_admin_key(x_admin_key)
    limit = max(1, min(limit, 10000))

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)

    purged = 0
    try:
        for _ in range(limit):
            method_frame, props, body = ch.basic_get(queue=settings.dlq_queue, auto_ack=False)
            if not method_frame:
                break
            if dry_run:
                ch.basic_nack(method_frame.delivery_tag, requeue=True)
                purged += 1
                if purged >= limit:
                    break
                continue

            ch.basic_ack(method_frame.delivery_tag)
            purged += 1
    finally:
        conn.close()

    logger.info(json.dumps({"event":"DLQ_PURGE","purged":purged}, ensure_ascii=False))
    return {"purged": purged}


class CharacterChatRequest(BaseModel):
    user_input: str = Field(..., description="User message")
    request_id: Optional[str] = Field(default=None, description="Id for deterministic presence generation")
    context: Dict[str, Any] = Field(default_factory=dict, description="Character context: intimacy, jealousy_level, etc.")
class ChatSendRequest(BaseModel):
    message: str = Field(..., description="User message (plain text). Supports slash commands: /yt, /rag, /play")
    request_id: Optional[str] = Field(default=None, description="Deterministic request id; if omitted server will generate")
    session_id: Optional[str] = Field(default=None, description="Stable session id for play/chat continuity")
    correlation_id: Optional[str] = Field(default=None, description="Client correlation id for UI button-lock matching")
    context: Dict[str, Any] = Field(default_factory=dict, description="Character context: intimacy, jealousy_level, etc.")
    client_context: Dict[str, Any] = Field(default_factory=dict, description="UI surface metadata (optional)")


class ChatSendAccepted(BaseModel):
    accepted: bool
    first_followup_report_id: str
    correlation_id: str


@app.post("/chat", status_code=202)
def chat_shorthand(
    body: Dict[str, Any] = Body(...),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    """
    Frontend shorthand: POST /chat → forwards to /chat/send logic.
    Accepts: {"text": "...", "session_id": "..."}
    Returns: 202 Accepted (UI update via SSE)
    """
    require_api_key(x_api_key, authorization)
    
    # Map frontend body to ChatSendRequest
    message = body.get("text", "").strip()
    session_id = body.get("session_id", "")
    
    request = ChatSendRequest(
        message=message,
        session_id=session_id
    )
    
    return chat_send(request, x_api_key, authorization, x_org_id, x_project_id)


@app.post("/chat/send", status_code=202, response_model=ChatSendAccepted)
def chat_send(
    body: ChatSendRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)
    tenant = _tenant_from_headers(x_org_id, x_project_id)
    tenant_id = tenant.tenant_id

    msg = (body.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail={"error": {"code": "BAD_REQUEST", "message": "message required"}})

    request_id = (body.request_id or "").strip() or str(uuid.uuid4())
    session_id = (body.session_id or "").strip() or _session_id_from_context({**(body.context or {}), "session_id": (body.session_id or "")}, request_id)
    correlation_id = (body.correlation_id or "").strip() or f"corr_{uuid.uuid4().hex}"

    causality = {"type": "chat.send", "command_id": None, "correlation_id": correlation_id}

    # Emit agent_status: listening (user message received)
    _emit_agent_status(tenant_id, "listening", {"user_message": msg[:80]})

    # 1) append user message as a chat report
    user_report = _mk_report(
        status="done",
        summary=f"user: {msg[:80]}",
        risk="GREEN",
        causality=causality,
        ui_hint={"renderer": "chat.message"},
        data={"role": "user", "text": mask_sensitive(msg), "session_id": session_id, "snapshot": stream_store.snapshot(tenant_id)},
    )
    stream_store.append_event(tenant_id, "report", user_report)

    # 2) route slash commands
    try:
        if msg.startswith("/yt"):
            q = msg[3:].strip()
            if not q:
                assistant_text = "사용법: /yt 검색어"
                assistant = _mk_report(
                    status="done",
                    summary="chat: youtube usage",
                    risk="GREEN",
                    causality=causality,
                    ui_hint={"renderer": "chat.message"},
                    data={"role": "assistant", "text": assistant_text, "session_id": session_id, "snapshot": stream_store.snapshot(tenant_id)},
                )
                stream_store.append_event(tenant_id, "report", assistant)
                return {"accepted": True, "first_followup_report_id": assistant["report_id"], "correlation_id": correlation_id}

            if not youtube_client.enabled():
                ask = _mk_report(
                    status="ask",
                    summary="YouTube API 키가 필요합니다.",
                    risk="YELLOW",
                    causality=causality,
                    ui_hint={"renderer": "ask.youtube_api_key"},
                    data={
                        "ask_id": f"ask_{uuid.uuid4().hex}",
                        "instructions": "환경변수 YOUTUBE_API_KEY 또는 settings.youtube_api_key에 키를 설정한 뒤 재시도하세요.",
                        "snapshot": stream_store.snapshot(tenant_id),
                    },
                )
                stream_store.append_event(tenant_id, "report", ask)
                return {"accepted": True, "first_followup_report_id": ask["report_id"], "correlation_id": correlation_id}

            results = youtube_client.search(tenant=tenant_id, query=q, max_results=6, region="KR", language="ko")
            rep = _mk_report(
                status="done",
                summary=f"youtube.search: {q}",
                risk=settings.youtube_default_risk,
                causality=causality,
                ui_hint={"renderer": "youtube.search.results"},
                data={"query": q, "results": results, "session_id": session_id, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", rep)
            assistant = _mk_report(
                status="done",
                summary="chat: youtube search done",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "chat.message"},
                data={"role": "assistant", "text": "유튜브 검색 결과를 표시했어요. 재생/큐에 추가할 수 있어요.", "session_id": session_id, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", assistant)
            return {"accepted": True, "first_followup_report_id": rep["report_id"], "correlation_id": correlation_id}

        if msg.startswith("/rag"):
            q = msg[4:].strip()
            if not q:
                assistant_text = "사용법: /rag 질문 또는 키워드"
                assistant = _mk_report(
                    status="done",
                    summary="chat: rag usage",
                    risk="GREEN",
                    causality=causality,
                    ui_hint={"renderer": "chat.message"},
                    data={"role": "assistant", "text": assistant_text, "session_id": session_id, "snapshot": stream_store.snapshot(tenant_id)},
                )
                stream_store.append_event(tenant_id, "report", assistant)
                return {"accepted": True, "first_followup_report_id": assistant["report_id"], "correlation_id": correlation_id}

            results = rag_engine.query(tenant=tenant_id, q=q, top_k=5)
            rep = _mk_report(
                status="done",
                summary=f"rag.query: {q}",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "rag.query.results"},
                data={"query": q, "results": results, "session_id": session_id, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", rep)
            assistant = _mk_report(
                status="done",
                summary="chat: rag query done",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "chat.message"},
                data={"role": "assistant", "text": "RAG 검색 결과를 표시했어요. 필요하면 더 구체적으로 물어봐요.", "session_id": session_id, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", assistant)
            return {"accepted": True, "first_followup_report_id": rep["report_id"], "correlation_id": correlation_id}

        # default: normal chat (includes /play and '놀아줘' via state_engine -> play_engine)
        # inject session_id for continuity
        # Emit agent_status: thinking (processing chat request)
        _emit_agent_status(tenant_id, "thinking", {"user_message": msg[:80]})
        
        context = dict(body.context or {})
        context["session_id"] = session_id
        payload = _run_character_chat_core(tenant_id=tenant_id, user_input=msg, context=context, request_id=request_id)
        
        # Emit agent_status: speaking (sending response)
        response_text = payload.get("text", "")
        _emit_agent_status(tenant_id, "speaking", {"response": response_text[:80]})
        
        # Generate high-quality TTS audio using Google Cloud TTS
        if TTS_ENABLED and response_text:
            tts_result = generate_tts(
                text=response_text,
                voice_name="ko-KR-Wavenet-A",  # High-quality Korean female voice
                speaking_rate=1.0,
                pitch=0.0
            )
            
            if tts_result:
                # Emit TTS start event with audio URL
                _emit_tts(tenant_id, "tts_start", {
                    "text": response_text,
                    "audio_url": tts_result["audio_url"],
                    "duration_ms": tts_result["duration_ms"],
                    "voice": tts_result["voice"]
                })
                
                # Emit TTS end event
                _emit_tts(tenant_id, "tts_end", {
                    "duration_ms": tts_result["duration_ms"]
                })
            else:
                # Fallback: simulate TTS without actual audio
                estimated_duration_ms = len(response_text) * 100
                _emit_tts(tenant_id, "tts_start", {"text": response_text, "voice": "ko-KR-Wavenet-A"})
                _emit_tts(tenant_id, "tts_end", {"duration_ms": estimated_duration_ms})
        else:
            # TTS disabled: just emit events without audio
            estimated_duration_ms = len(response_text) * 100
            _emit_tts(tenant_id, "tts_start", {"text": response_text, "voice": "ko-KR-Wavenet-A"})
            _emit_tts(tenant_id, "tts_end", {"duration_ms": estimated_duration_ms})
        
        assistant = _mk_report(
            status="done",
            summary="chat: assistant reply",
            risk="GREEN",
            causality=causality,
            ui_hint={"renderer": "chat.message"},
            data={
                "role": "assistant",
                "text": payload.get("text", ""),
                "mode": payload.get("mode", ""),
                "presence_packet": payload.get("presence_packet"),
                "confirm_card": payload.get("confirm_card"),
                "session_id": session_id,
                "snapshot": stream_store.snapshot(tenant_id),
            },
        )
        stream_store.append_event(tenant_id, "report", assistant)
        
        # Emit agent_status: idle (chat completed)
        _emit_agent_status(tenant_id, "idle", {"chat_completed": True})
        
        return {"accepted": True, "first_followup_report_id": assistant["report_id"], "correlation_id": correlation_id}

    except Exception as e:
        err = _mk_report(
            status="error",
            summary=str(e),
            risk="YELLOW",
            causality=causality,
            ui_hint={"renderer": "error"},
            data={"snapshot": stream_store.snapshot(tenant_id)},
        )
        stream_store.append_event(tenant_id, "report", err)
        # Emit agent_status: idle (error occurred)
        _emit_agent_status(tenant_id, "idle", {"error": str(e)})
        return {"accepted": True, "first_followup_report_id": err["report_id"], "correlation_id": correlation_id}




@app.post("/character/chat")
def character_chat(
    req: CharacterChatRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)

    tenant = _tenant_from_headers(x_org_id, x_project_id)
    if not req.user_input.strip():
        raise HTTPException(status_code=400, detail={"error": {"code": "BAD_REQUEST", "message": "user_input required"}})

    tenant_id = tenant.tenant_id
    request_id = (req.request_id or "").strip() or str(uuid.uuid4())
    user_input = mask_sensitive(req.user_input.strip())

    return _run_character_chat_core(tenant_id=tenant_id, user_input=user_input, context=(req.context or {}), request_id=request_id)

@app.post("/llm/generate")
def llm_generate(
    body: dict,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)

    tenant = _tenant_from_headers(x_org_id, x_project_id)
    input_text = body.get("input_text", "")
    schema_name = body.get("schema_name")  # optional
    allow_repair = bool(body.get("allow_repair", True))

    if not input_text:
        raise HTTPException(status_code=400, detail={"error": {"code": "BAD_REQUEST", "message": "input_text required"}})

    provider = body.get('provider')
    model = body.get('model')
    purpose = body.get('purpose') or 'generic'
    preset = body.get('preset')
    temperature = body.get('temperature')
    max_tokens = body.get('max_tokens')
    timeout_s = body.get('timeout_s')
    cache_ttl_s = body.get('cache_ttl_s')
    schema_name = body.get('schema_name')
    allow_repair = body.get('allow_repair', False)

    res = llm_client.generate(
        input_text,
        provider_override=provider,
        model_override=model,
        purpose=purpose,
        preset=preset,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout_s=timeout_s,
        cache_ttl_s=cache_ttl_s,
        schema_name=schema_name,
        allow_repair=bool(allow_repair),
        tenant=tenant,
    )

    if res.disabled and settings.llm_required:
        raise HTTPException(status_code=503, detail={"error": {"code": "LLM_DISABLED", "message": res.output_text}})

    if not schema_name:
        return {"provider": res.provider, "model": res.model, "latency_ms": res.latency_ms, "text": res.output_text}

    # schema mode
    # SCHEMA_FALLBACK: when LLM is disabled and not required, return deterministic payload to keep pipeline alive.
    if res.disabled and (not settings.llm_required):
        return {
            "provider": res.provider,
            "model": res.model,
            "latency_ms": res.latency_ms,
            "schema_name": schema_name,
            "repaired": False,
            "data": {"action": "noop", "result": {"text": "LLM_DISABLED"}, "warnings": ["LLM disabled"]},
        }

    # schema mode
    from shared.json_guard import validate, repair

    vr = validate(res.output_text, schema_name)
    if (not vr.ok) and allow_repair:
        vr = repair(res.output_text, schema_name, llm_client, max_attempts=2, tenant=tenant)

    if not vr.ok:
        raise HTTPException(status_code=422, detail={
            "error": {"code": vr.error_code or "SCHEMA_VALIDATION_FAILED", "message": vr.error},
            "provider": res.provider, "model": res.model, "latency_ms": res.latency_ms,
            "schema_name": schema_name,
        })

    return {
        "provider": res.provider,
        "model": res.model,
        "latency_ms": res.latency_ms,
        "schema_name": schema_name,
        "repaired": bool(vr.repaired),
        "data": vr.data,
        "repair_provider": vr.provider,
        "repair_model": vr.model,
    }


# -----------------------------------------------------------------------------
# Minimal BFF layer for UI: SSE stream + sidecar commands + approvals
# -----------------------------------------------------------------------------

def _tenant_key(tenant: TenantCtx) -> str:
    return StreamStore.tenant_id(tenant.org_id, tenant.project_id)


def _sse_event(seq: int, event_type: str, data: Dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"id: {seq}\nevent: {event_type}\ndata: {payload}\n\n"


def _mk_report(
    *,
    status: str,
    summary: str,
    risk: str,
    causality: Dict[str, Any],
    ui_hint: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    report_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "report_id": report_id or f"r-{uuid.uuid4().hex}",
        "ts": _utc_now(),
        "status": status,
        "summary": summary,
        "risk": risk,
        "ui_hint": ui_hint or {},
        "data": data or {},
        "causality": causality,
    }


def _emit_agent_status(tenant_id: str, status: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Emit agent_status event to SSE stream for Live2D character state sync.
    
    Args:
        tenant_id: Tenant identifier
        status: One of: idle, listening, thinking, speaking, busy, waiting_approval
        context: Optional context data (e.g., current_task, message)
    """
    valid_statuses = {"idle", "listening", "thinking", "speaking", "busy", "waiting_approval"}
    if status not in valid_statuses:
        logger.warning(f"Invalid agent_status: {status}. Defaulting to 'idle'")
        status = "idle"
    
    payload = {
        "status": status,
        "ts": _utc_now(),
        "context": context or {},
    }
    stream_store.append_event(tenant_id, "agent_status", payload)
    logger.debug(f"[agent_status] {tenant_id}: {status}")


def _emit_tts(tenant_id: str, event_type: str, data: Dict[str, Any]) -> None:
    """
    Emit TTS event to SSE stream for Live2D lip-sync.
    
    Args:
        tenant_id: Tenant identifier
        event_type: One of: tts_start, tts_chunk, tts_end
        data: TTS event data (e.g., audio_url, chunk_data, duration)
    """
    valid_event_types = {"tts_start", "tts_chunk", "tts_end"}
    if event_type not in valid_event_types:
        logger.warning(f"Invalid tts event_type: {event_type}")
        return
    
    payload = {
        "ts": _utc_now(),
        **data,
    }
    stream_store.append_event(tenant_id, event_type, payload)
    logger.debug(f"[{event_type}] {tenant_id}")


@app.get("/tts/{filename}")
async def serve_tts_audio(filename: str):
    """
    Serve TTS audio files.
    
    This endpoint serves generated TTS audio files from temporary storage.
    Files are automatically cleaned up after 24 hours.
    """
    from pathlib import Path
    from fastapi.responses import FileResponse
    
    # Security: validate filename format
    if not filename.startswith("tts_") or not filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Invalid filename format")
    
    if TTS_ENABLED:
        audio_path = tts_service.temp_dir / filename
        
        if audio_path.exists():
            return FileResponse(
                audio_path,
                media_type="audio/mpeg",
                headers={
                    "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                    "Access-Control-Allow-Origin": "*",  # Allow CORS
                }
            )
    
    raise HTTPException(status_code=404, detail="Audio file not found")


@app.post("/api/character/decide")
async def character_decide(request: Request):
    """
    Character state decision API for testing Ceria's self system.
    
    Request body:
    {
        "user_input": str,
        "context": {
            "intimacy": int (0~100),
            "jealousy_level": int (0~4),
            "sexy_blocked": bool,
            "sexy_cooldown_seconds": int,
            "user_opt_out_sexy": bool,
            "task_busy": bool,
            "tool_allowlist_active": bool,
            "last_cooldown_update": float (optional),
            "turns_since_jealousy_trigger": int (optional),
            "tool_success": bool (optional),
            "approval_granted": bool (optional),
            "negative_feedback": bool (optional)
        },
        "auto_update": bool (default: true)
    }
    
    Response:
    {
        "decision": CharacterDecision,
        "presence": PresencePacket,
        "context": CharacterContext (auto-updated),
        "user_input": str,
        "auto_updates": {
            "intimacy_change": str,
            "jealousy_change": str,
            "cooldown_change": str
        }
    }
    """
    from shared.character.state_engine import CharacterContext, decide_state
    from shared.character.presence import presence_to_live2d
    from shared.character.auto_intimacy import auto_update_intimacy
    from shared.character.jealousy_detector import auto_update_jealousy
    from shared.character.cooldown_manager import auto_manage_cooldown
    import uuid
    import time
    
    try:
        body = await request.json()
        user_input = body.get("user_input", "")
        ctx_data = body.get("context", {})
        auto_update = body.get("auto_update", True)
        
        # Extract current values
        intimacy = int(ctx_data.get("intimacy", 0))
        jealousy_level = int(ctx_data.get("jealousy_level", 0))
        sexy_cooldown_seconds = int(ctx_data.get("sexy_cooldown_seconds", 0))
        last_cooldown_update = ctx_data.get("last_cooldown_update", time.time())
        turns_since_jealousy = ctx_data.get("turns_since_jealousy_trigger", 0)
        
        # Auto-update logic
        auto_updates = {
            "intimacy_change": "자동 업데이트 비활성",
            "jealousy_change": "자동 업데이트 비활성",
            "cooldown_change": "자동 업데이트 비활성"
        }
        
        if auto_update:
            # 1. Update intimacy
            tool_success = ctx_data.get("tool_success", False)
            approval_granted = ctx_data.get("approval_granted", False)
            negative_feedback = ctx_data.get("negative_feedback", False)
            
            intimacy, intimacy_msg = auto_update_intimacy(
                current_intimacy=intimacy,
                user_input=user_input,
                tool_success=tool_success,
                approval_granted=approval_granted,
                negative_feedback=negative_feedback
            )
            auto_updates["intimacy_change"] = intimacy_msg
            
            # 2. Update jealousy
            jealousy_level, jealousy_msg = auto_update_jealousy(
                current_jealousy=jealousy_level,
                user_input=user_input,
                turns_since_trigger=turns_since_jealousy
            )
            auto_updates["jealousy_change"] = jealousy_msg
            
            # 3. Update cooldown
            sexy_cooldown_seconds, cooldown_msg = auto_manage_cooldown(
                current_cooldown_seconds=sexy_cooldown_seconds,
                last_update_timestamp=last_cooldown_update
            )
            auto_updates["cooldown_change"] = cooldown_msg
        
        # Build context with updated values
        ctx = CharacterContext(
            intimacy=intimacy,
            jealousy_level=jealousy_level,
            sexy_blocked=bool(ctx_data.get("sexy_blocked", False)),
            sexy_cooldown_seconds=sexy_cooldown_seconds,
            user_opt_out_sexy=bool(ctx_data.get("user_opt_out_sexy", False)),
            task_busy=bool(ctx_data.get("task_busy", False)),
            tool_allowlist_active=bool(ctx_data.get("tool_allowlist_active", True)),
        )
        
        # Decide state
        decision = decide_state(user_input, ctx)
        
        # Generate presence packet
        request_id = str(uuid.uuid4())
        presence = presence_to_live2d(request_id, decision, ctx)
        
        return {
            "decision": {
                "mode": decision.mode,
                "sexy_level": decision.sexy_level,
                "jealousy_level": decision.jealousy_level,
                "requires_confirm": decision.requires_confirm,
                "tool_calls_allowed": decision.tool_calls_allowed,
            },
            "presence": presence,
            "context": {
                "intimacy": ctx.intimacy,
                "jealousy_level": ctx.jealousy_level,
                "sexy_blocked": ctx.sexy_blocked,
                "sexy_cooldown_seconds": ctx.sexy_cooldown_seconds,
                "user_opt_out_sexy": ctx.user_opt_out_sexy,
                "task_busy": ctx.task_busy,
                "tool_allowlist_active": ctx.tool_allowlist_active,
                "last_cooldown_update": time.time()
            },
            "user_input": user_input,
            "auto_updates": auto_updates
        }
        
    except Exception as e:
        logger.error(f"Character decide error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def landing_page(lang: str = "ko"):
    """World-Class Landing Page with huge Live2D character."""
    return HTMLResponse(render_landing_page_i18n(lang))


@app.get("/intro")
def intro_page(lang: str = "ko"):
    """Intro page: purpose + core values + architecture + developer section."""
    return HTMLResponse(render_intro_page_i18n(lang))


@app.get("/developer")
def developer_page():
    """Developer page: text-only section about 서경대학교 남현우 교수."""
    body = """
<div class="container-narrow">
  <h1>개발자 소개</h1>
  
  <div class="card">
    <h2>서경대학교 남현우 교수</h2>
    <p class="lead">
      NEXUS-ON 프로젝트를 설계하고 개발하는 연구자이자 교육자입니다.
    </p>
    
    <h3>연구 분야</h3>
    <p>
      • AI 에이전트 시스템과 Human-in-the-loop 인터페이스<br>
      • 자율 시스템의 안전성과 신뢰성<br>
      • 소프트웨어 공학과 AI의 융합<br>
      • 한국어 문서 처리 및 RAG 시스템
    </p>
    
    <h3>프로젝트 비전</h3>
    <p>
      NEXUS-ON은 AI가 사람을 대체하는 것이 아니라,<br>
      사람과 AI가 협력하여 더 나은 결과를 만들어내는 것을 목표로 합니다.<br>
      <br>
      특히 한국어 문서(HWP 포함)를 자연스럽게 처리하고,<br>
      로컬 환경에서도 안전하게 작동하는 시스템을 구축하는 데 중점을 두고 있습니다.
    </p>
    
    <h3>개발 철학</h3>
    <p>
      • <strong>Local-first</strong>: 데이터와 제어권은 사용자에게<br>
      • <strong>Human oversight</strong>: 중요한 결정은 반드시 사람이<br>
      • <strong>Fail-safe</strong>: 실패해도 안전하게, 복구 가능하게<br>
      • <strong>Open by design</strong>: 투명하고 확장 가능한 아키텍처
    </p>
  </div>
  
  <div class="card">
    <p class="small">
      연락: 서경대학교 컴퓨터공학과<br>
      NEXUS-ON은 교육 및 연구 목적으로 개발된 오픈소스 프로젝트입니다.
    </p>
  </div>
</div>
"""
    return HTMLResponse(render_page("Developer", body, "developer"))


@app.get("/modules")
def modules_page(lang: str = "ko"):
    """Modules page: render modules.json + benchmark table on same page."""
    modules = load_modules_data()
    benchmark = load_benchmark_data()
    
    # Build modules table
    modules_rows = ""
    for m in modules:
        status_class = {"G": "green", "Y": "yellow", "R": "red"}.get(m.get("status", "Y"), "yellow")
        highlights = "<br>".join([f"• {h}" for h in m.get("highlights", [])])
        modules_rows += f"""
<tr>
  <td><strong>{m.get('module_id', '')}</strong></td>
  <td>{m.get('name', '')}</td>
  <td><span class="badge badge-{status_class}">{m.get('status', 'Y')}</span></td>
  <td style="font-size:12px">{highlights}</td>
  <td style="font-size:12px">{m.get('last_updated', '')}</td>
</tr>
"""
    
    # Build benchmark table
    benchmark_rows = ""
    for b in benchmark:
        benchmark_rows += f"""
<tr>
  <td><strong>{b.get('category', '')}</strong></td>
  <td>{b.get('product', '')}</td>
  <td style="font-size:12px">{b.get('strengths', '')}</td>
  <td style="font-size:12px">{b.get('weaknesses', '')}</td>
  <td>{b.get('price_tier', '')}</td>
  <td style="font-size:12px">{b.get('last_updated', '')}</td>
</tr>
"""
    
    body = f"""
<div class="container">
  <h1>모듈 현황</h1>
  <p class="lead">
    NEXUS-ON을 구성하는 핵심 모듈들의 상태와 주요 기능을 확인하세요.
  </p>
  
  <table>
    <thead>
      <tr>
        <th>Module ID</th>
        <th>Name</th>
        <th>Status</th>
        <th>Highlights</th>
        <th>Last Updated</th>
      </tr>
    </thead>
    <tbody>
      {modules_rows}
    </tbody>
  </table>
  
  <h2 style="margin-top:48px">경쟁 제품 비교</h2>
  <p class="lead">
    NEXUS-ON과 유사한 제품들의 강점, 약점, 가격대를 비교합니다.
  </p>
  
  <table>
    <thead>
      <tr>
        <th>Category</th>
        <th>Product</th>
        <th>Strengths</th>
        <th>Weaknesses</th>
        <th>Price Tier</th>
        <th>Last Updated</th>
      </tr>
    </thead>
    <tbody>
      {benchmark_rows}
    </tbody>
  </table>
  
  <div class="card" style="margin-top:24px">
    <p class="small">
      <strong>참고:</strong> 위 비교 데이터는 /data/modules.json 및 /data/benchmark.json 파일에서 로드됩니다.<br>
      향후 데이터베이스 기반 실시간 업데이트로 전환될 예정입니다.
    </p>
  </div>
</div>
"""
    return HTMLResponse(render_modules_page_i18n(lang))


@app.get("/benchmark")
def benchmark_page():
    """Benchmark page: render benchmark.json as table."""
    benchmark = load_benchmark_data()
    
    rows = ""
    for b in benchmark:
        rows += f"""
<tr>
  <td><strong>{b.get('category', '')}</strong></td>
  <td>{b.get('product', '')}</td>
  <td>{b.get('strengths', '')}</td>
  <td>{b.get('weaknesses', '')}</td>
  <td>{b.get('price_tier', '')}</td>
  <td style="font-size:12px">{b.get('notes', '')}</td>
  <td style="font-size:12px">{b.get('last_updated', '')}</td>
</tr>
"""
    
    body = f"""
<div class="container">
  <h1>제품 비교표</h1>
  <p class="lead">
    AI Assistant 및 Autonomous Agent 관련 제품들을 카테고리별로 비교합니다.<br>
    NEXUS-ON의 포지셔닝과 차별화 포인트를 확인하세요.
  </p>
  
  <table>
    <thead>
      <tr>
        <th>Category</th>
        <th>Product</th>
        <th>Strengths</th>
        <th>Weaknesses</th>
        <th>Price Tier</th>
        <th>Notes</th>
        <th>Last Updated</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  
  <div class="card" style="margin-top:24px">
    <h3>NEXUS-ON의 차별점</h3>
    <p>
      • <strong>Human-in-the-loop 내장</strong>: 승인 시스템이 플랫폼에 통합됨<br>
      • <strong>로컬 우선</strong>: 외부 의존성 최소화, 데이터 주권 보장<br>
      • <strong>한국어 문서 지원</strong>: HWP 파일을 네이티브로 처리<br>
      • <strong>SSE 기반 실시간 UI</strong>: 단일 소스 원칙으로 일관성 보장
    </p>
  </div>
</div>
"""
    return HTMLResponse(render_page("Benchmark", body, "benchmark"))


@app.get("/app")
def ui_app():
    """Existing work app UI moved to /app. All functionality unchanged."""
    # Simple, zero-build local UI.
    html = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NEXUS Local</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Sans KR", sans-serif; margin: 0; background:#0b0f17; color:#e8eefc;}
    header { padding: 12px 14px; border-bottom: 1px solid rgba(255,255,255,0.08); display:flex; gap:12px; align-items:center; }
    header .pill { border: 1px solid rgba(255,255,255,0.12); padding: 6px 10px; border-radius: 999px; font-size:12px; color:#c9d6ff; }
    header input { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); color:#e8eefc; border-radius:10px; padding:8px 10px; width: 260px; }
    main { display:grid; grid-template-columns: 1.35fr 0.65fr; gap:12px; padding: 12px; height: calc(100vh - 56px); box-sizing:border-box; }
    .card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; overflow:hidden; }
    .card h3 { margin:0; padding:10px 12px; border-bottom: 1px solid rgba(255,255,255,0.08); font-size:14px; color:#dbe6ff;}
    .chat { display:flex; flex-direction:column; height: 100%; }
    #log { flex:1; overflow:auto; padding: 10px 12px; line-height:1.45; font-size:13px; }
    .msg { margin: 8px 0; }
    .msg .meta { font-size:11px; color:#9fb3ea; margin-bottom:3px; }
    .msg .bubble { display:inline-block; padding: 8px 10px; border-radius: 12px; max-width: 92%; white-space: pre-wrap; }
    .msg.user .bubble { background: rgba(100,140,255,0.18); border: 1px solid rgba(100,140,255,0.25); }
    .msg.assistant .bubble { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); }
    .composer { display:flex; gap:8px; padding: 10px; border-top: 1px solid rgba(255,255,255,0.08); }
    .composer input { flex:1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); color:#e8eefc; border-radius:10px; padding:10px 10px; }
    .composer button { background:#2f6bff; border:0; color:white; border-radius:10px; padding: 10px 12px; cursor:pointer; }
    .small { font-size:12px; color:#9fb3ea; padding: 8px 12px; }
    .gridRight { display:flex; flex-direction:column; gap:12px; overflow:auto; }
    .panel { padding: 10px 12px; }
    .btn { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); color:#e8eefc; border-radius:10px; padding: 7px 10px; cursor:pointer; font-size:12px; }
    .btn.primary { background:#2f6bff; border:0; }
    .row { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
    .list { display:flex; flex-direction:column; gap:8px; }
    .item { border: 1px solid rgba(255,255,255,0.10); background: rgba(255,255,255,0.04); border-radius: 12px; padding: 8px 10px; }
    .item .title { font-size:13px; color:#e8eefc; }
    .item .sub { font-size:11px; color:#9fb3ea; margin-top:2px; }
    iframe { width:100%; height: 220px; border:0; background:black; }
    textarea { width:100%; min-height: 140px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); color:#e8eefc; border-radius:10px; padding:10px; resize: vertical; box-sizing:border-box; }
    code.kbd { padding: 2px 6px; border-radius:6px; border:1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.06); font-size:12px; }
  </style>
</head>
<body>
<header>
  <div class="pill">NEXUS Local P0</div>
  <div class="pill" id="sseStatus">SSE: disconnected</div>
  <div class="pill">Session: <span id="sessionId"></span></div>
  <input id="apiKey" placeholder="x-api-key (없으면 비움)" />
  <div class="pill">Tips: <code class="kbd">/yt</code> <code class="kbd">/rag</code> <code class="kbd">/play</code></div>
</header>

<main>
  <section class="card chat">
    <h3>캐릭터 비서 채팅</h3>
    <div id="log"></div>
    <div class="composer">
      <input id="msg" placeholder="메시지... (/yt, /rag, /play 지원)" />
      <button id="send">Send</button>
    </div>
    <div class="small">채팅은 서버의 SSE 스트림(/agent/reports/stream)이 단일 소스입니다.</div>
  </section>

  <section class="gridRight">
    <div class="card">
      <h3>YouTube</h3>
      <div class="panel">
        <div class="row">
          <button class="btn" id="ytClear">Clear Results</button>
          <button class="btn primary" id="ytNext">Play Next</button>
          <button class="btn" id="ytClearQ">Clear Queue</button>
        </div>
        <div style="height:10px"></div>
        <iframe id="ytFrame" title="YouTube Player" src=""></iframe>
        <div style="height:10px"></div>
        <div class="small">검색: 채팅에 <code class="kbd">/yt 키워드</code>. 결과에서 Play 또는 Queue.</div>
        <div style="height:10px"></div>
        <div class="row"><div class="pill" style="border-color:rgba(255,255,255,0.12)">Results</div></div>
        <div id="ytResults" class="list" style="margin-top:8px"></div>
        <div style="height:10px"></div>
        <div class="row"><div class="pill" style="border-color:rgba(255,255,255,0.12)">Queue</div></div>
        <div id="ytQueue" class="list" style="margin-top:8px"></div>
      </div>
    </div>

    <div class="card">
      <h3>RAG (Naive)</h3>
      <div class="panel">
        <div class="small">질문: 채팅에 <code class="kbd">/rag 키워드</code>. (P0: 토큰 겹침 기반)</div>
        <div id="ragResults" class="list" style="margin-top:8px"></div>
      </div>
    </div>

    <div class="card">
      <h3>작업 캔버스</h3>
      <div class="panel">
        <textarea id="canvas" placeholder="메모/초안/체크리스트…"></textarea>
        <div style="height:10px"></div>
        <div class="row">
          <button class="btn primary" id="canvasSave">Save (local)</button>
          <button class="btn" id="canvasClear">Clear</button>
          <div class="small" id="canvasMeta" style="padding:0"></div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>Worklog / Approvals</h3>
      <div class="panel">
        <div class="small">Approvals는 P0에서 Ask 형태로 표시됩니다.</div>
        <div id="approvals" class="list"></div>
        <div style="height:10px"></div>
        <div id="worklog" class="list"></div>
      </div>
    </div>
  </section>
</main>

<script>
  const $ = (id) => document.getElementById(id);

  function ensureSessionId() {
    let sid = localStorage.getItem("nexus_session_id");
    if (!sid) {
      sid = "sess_" + Math.random().toString(16).slice(2) + "_" + Date.now().toString(16);
      localStorage.setItem("nexus_session_id", sid);
    }
    $("sessionId").textContent = sid;
    return sid;
  }

  function apiKey() {
    const v = $("apiKey").value.trim();
    localStorage.setItem("nexus_api_key", v);
    return v;
  }

  function restoreApiKey() {
    $("apiKey").value = localStorage.getItem("nexus_api_key") || "";
  }

  function addMsg(role, text) {
    const el = document.createElement("div");
    el.className = "msg " + role;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = role === "user" ? "YOU" : "NEXUS";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    el.appendChild(meta);
    el.appendChild(bubble);
    $("log").appendChild(el);
    $("log").scrollTop = $("log").scrollHeight;
  }

  // ---------- YouTube queue ----------
  function loadQueue() {
    try { return JSON.parse(localStorage.getItem("nexus_yt_queue") || "[]"); } catch(e) { return []; }
  }
  function saveQueue(q) { localStorage.setItem("nexus_yt_queue", JSON.stringify(q.slice(0, 50))); }
  function renderQueue() {
    const q = loadQueue();
    $("ytQueue").innerHTML = "";
    if (!q.length) {
      const empty = document.createElement("div");
      empty.className = "small";
      empty.textContent = "큐가 비었습니다.";
      $("ytQueue").appendChild(empty);
      return;
    }
    q.forEach((it, idx) => {
      const d = document.createElement("div");
      d.className = "item";
      d.innerHTML = `<div class="title">${escapeHtml(it.title || it.video_id || "item")}</div>
                     <div class="sub">${escapeHtml(it.channel || "")}</div>`;
      const row = document.createElement("div");
      row.className = "row";
      row.style.marginTop = "6px";
      const play = btn("Play", () => playVideo(it.video_id, 0));
      const up = btn("Up", () => { if (idx>0){ const qq=loadQueue(); const t=qq[idx-1]; qq[idx-1]=qq[idx]; qq[idx]=t; saveQueue(qq); renderQueue(); }});
      const del = btn("Remove", () => { const qq=loadQueue(); qq.splice(idx,1); saveQueue(qq); renderQueue(); });
      row.appendChild(play); row.appendChild(up); row.appendChild(del);
      d.appendChild(row);
      $("ytQueue").appendChild(d);
    });
  }

  function _mkCorr() {
    return "corr-" + Math.random().toString(16).slice(2) + Date.now().toString(16);
  }

  async function _sidecar(type, params) {
    const corr = _mkCorr();
    const cmd = "cmd-" + corr.slice(5);
    return postJSON("/sidecar/command", {
      command_id: cmd,
      type,
      context: { ref: "ui", title: "ui" },
      params: params || {},
      client_context: { surface: "sidecar", correlation_id: corr, session_id: ensureSessionId() },
    });
  }

  async function enqueue(item) {
    // Optimistic local update
    const q = loadQueue();
    q.push(item);
    saveQueue(q);
    renderQueue();

    try {
      await _sidecar("youtube.queue.add", {
        video_id: item.video_id,
        title: item.title || "",
        channel: item.channel || "",
      });
    } catch (e) {
      // Local queue remains usable
    }
  }

  async function playNext() {
    try {
      await _sidecar("youtube.queue.next", {});
      return;
    } catch (e) {
      // Fallback to local queue
    }

    const q = loadQueue();
    if (!q.length) { addMsg("assistant", "YouTube 큐가 비었습니다."); return; }
    const it = q.shift();
    saveQueue(q);
    renderQueue();
    playVideo(it.video_id, 0);
  }

  async function clearQueue() {
    saveQueue([]);
    renderQueue();
    try { await _sidecar("youtube.queue.clear", {}); } catch (e) {}
  }

  async function syncQueueFromServer() {
    try { await _sidecar("youtube.queue.list", {}); } catch (e) {}
  }

  // ---------- Work canvas ----------
  function restoreCanvas() {
    const c = localStorage.getItem("nexus_work_canvas") || "";
    $("canvas").value = c;
    const ts = localStorage.getItem("nexus_work_canvas_ts") || "";
    $("canvasMeta").textContent = ts ? ("saved: " + ts) : "";
  }
  function saveCanvas() {
    localStorage.setItem("nexus_work_canvas", $("canvas").value);
    const ts = new Date().toISOString();
    localStorage.setItem("nexus_work_canvas_ts", ts);
    $("canvasMeta").textContent = "saved: " + ts;
  }
  function clearCanvas() {
    $("canvas").value = "";
    saveCanvas();
  }

  // ---------- RAG render ----------
  function renderRag(results, query) {
    $("ragResults").innerHTML = "";
    if (!results || !results.length) {
      const empty = document.createElement("div");
      empty.className = "small";
      empty.textContent = query ? "결과 없음" : "대기 중";
      $("ragResults").appendChild(empty);
      return;
    }
    results.forEach(r => {
      const d = document.createElement("div");
      d.className = "item";
      d.innerHTML = `<div class="title">${escapeHtml(r.doc_id)} <span class="sub">(score ${r.score})</span></div>
                     <div class="sub">${escapeHtml((r.snippet || "").slice(0, 240))}</div>`;
      $("ragResults").appendChild(d);
    });
  }

  function escapeHtml(s) {
    return (s || "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
  }

  function btn(label, onClick) {
    const b = document.createElement("button");
    b.className = "btn";
    b.textContent = label;
    b.onclick = onClick;
    return b;
  }

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey() || ""
      },
      body: JSON.stringify(body)
    });
    return await res.json();
  }

  async function playVideo(video_id, start_seconds) {
    await postJSON("/sidecar/command", {
      command_id: "cmd_" + Math.random().toString(16).slice(2),
      type: "youtube.play",
      context: { ref: "ui", title: "youtube.play" },
      params: { video_id, start_seconds: start_seconds || 0 },
      client_context: { surface: "ui", correlation_id: "corr_" + Math.random().toString(16).slice(2) }
    });
  }

  async function sendChat() {
    const msg = $("msg").value.trim();
    if (!msg) return;
    $("msg").value = "";
    await postJSON("/chat/send", {
      message: msg,
      session_id: ensureSessionId(),
      correlation_id: "corr_" + Math.random().toString(16).slice(2),
      context: {}
    });
  }

  function connectSSE() {
    const key = apiKey();
    const url = "/agent/reports/stream" + (key ? ("?api_key=" + encodeURIComponent(key)) : "");
    const es = new EventSource(url);
    $("sseStatus").textContent = "SSE: connecting…";
    es.addEventListener("open", () => $("sseStatus").textContent = "SSE: connected");
    es.addEventListener("error", () => $("sseStatus").textContent = "SSE: error/reconnecting…");

    es.addEventListener("snapshot", (ev) => {
      try {
        const snap = JSON.parse(ev.data || "{}");
        renderSnapshot(snap);
      } catch(e) {}
    });

    es.addEventListener("report", (ev) => {
      try {
        const r = JSON.parse(ev.data || "{}");
        renderReport(r);
      } catch(e) {}
    });

    es.addEventListener("ping", () => {});
  }

  function renderSnapshot(snap) {
    if (!snap) return;

    // approvals (asks)
    const a = $("approvals");
    a.innerHTML = "";
    const asks = (snap.asks || []).slice(0, 20);
    if (!asks.length) {
      const emptyA = document.createElement("div");
      emptyA.className = "small";
      emptyA.textContent = "승인/Ask 없음";
      a.appendChild(emptyA);
    } else {
      asks.forEach(x => {
        const d = document.createElement("div");
        d.className = "item";
        d.innerHTML = `<div class="title">${escapeHtml(x.summary || "Ask")}</div>
                       <div class="sub">${escapeHtml((x.data && x.data.instructions) || "")}</div>`;
        a.appendChild(d);
      });
    }

    // worklog
    const w = $("worklog");
    w.innerHTML = "";
    const logs = (snap.worklog || []).slice(0, 20);
    if (!logs.length) {
      const empty = document.createElement("div");
      empty.className = "small";
      empty.textContent = "worklog 비어 있음";
      w.appendChild(empty);
      return;
    }
    logs.forEach(e => {
      const d = document.createElement("div");
      d.className = "item";
      const title = e.event_type || (e.ui_hint && e.ui_hint.renderer) || "event";
      const summary = e.summary || (e.payload && (e.payload.summary || e.payload.status)) || "";
      d.innerHTML = `<div class="title">${escapeHtml(title)}</div>
                     <div class="sub">${escapeHtml(summary)}</div>`;
      w.appendChild(d);
    });
  }

  function renderReport(r) {
    const renderer = (r.ui_hint && r.ui_hint.renderer) || "";
    const data = r.data || {};

    if (renderer === "chat.message") {
      addMsg(data.role === "user" ? "user" : "assistant", data.text || "");
      return;
    }

    if (renderer === "youtube.search.results") {
      const results = data.results || data.items || [];
      $("ytResults").innerHTML = "";
      if (!results.length) {
        const empty = document.createElement("div");
        empty.className = "small";
        empty.textContent = "검색 결과 없음";
        $("ytResults").appendChild(empty);
        return;
      }
      results.forEach(it => {
        const d = document.createElement("div");
        d.className = "item";
        d.innerHTML = `<div class="title">${escapeHtml(it.title || "")}</div>
                       <div class="sub">${escapeHtml(it.channel || "")} • ${escapeHtml(it.duration || "")}</div>`;
        const row = document.createElement("div");
        row.className = "row";
        row.style.marginTop = "6px";
        row.appendChild(btn("Play", () => playVideo(it.video_id, 0)));
        row.appendChild(btn("Queue", () => enqueue(it)));
        d.appendChild(row);
        $("ytResults").appendChild(d);
      });
      return;
    }

    if (renderer === "youtube.play.embed") {
      const video_id = data.video_id || (data.queue_item ? (data.queue_item.video_id || "") : "");
      const start = data.start_seconds || 0;
      const url = video_id ? `https://www.youtube.com/embed/${video_id}?autoplay=1&start=${start}` : "";
      $("ytFrame").src = url;
      if (Array.isArray(data.queue)) {
        saveQueue(data.queue);
        renderQueue();
      }
      return;
    }

    if (renderer === "youtube.queue.updated") {
      if (Array.isArray(data.queue)) {
        saveQueue(data.queue);
        renderQueue();
      }
      return;
    }

    if (renderer === "rag.folder.ingest.done") {
      const r = data.result || {};
      const errs = (r.errors || []).slice(0, 5).map(e => `${escapeHtml(e.path || "")}: ${escapeHtml(e.error || "")}`).join("<br/>");
      $("ragResults").innerHTML = `
        <div><b>Folder ingest</b></div>
        <div>folder: ${escapeHtml(r.folder || "")}</div>
        <div>ingested_chunks: ${r.ingested_chunks ?? 0} / candidates: ${r.candidates ?? 0} / skipped: ${r.skipped ?? 0}</div>
        <div>pending_hwp: ${r.pending_hwp ?? 0}</div>
        <div>started: ${escapeHtml(r.started_at || "")}</div>
        <div>finished: ${escapeHtml(r.finished_at || "")}</div>
        <div style="margin-top:6px;color:#a00">${errs}</div>
      `;
      return;
    }

    if (renderer === "rag.folder.status") {
      $("ragResults").textContent = data.raw || "(no status)";
      return;
    }

    if (renderer === "rag.query.results") {
      renderRag(data.results || [], data.query || "");
      return;
    }

    // Ask-style approvals (minimal)
    if (renderer.startsWith("ask.")) {
      const a = document.createElement("div");
      a.className = "item";
      a.innerHTML = `<div class="title">${escapeHtml(r.summary || "승인 필요")}</div>
                     <div class="sub">${escapeHtml((data && data.instructions) || "")}</div>`;
      $("approvals").prepend(a);
      return;
    }

    // fallback to worklog
    const w = document.createElement("div");
    w.className = "item";
    w.innerHTML = `<div class="title">${escapeHtml(renderer || "report")}</div>
                   <div class="sub">${escapeHtml(r.summary || "")}</div>`;
    $("worklog").prepend(w);
  }

  $("send").onclick = sendChat;
  $("msg").addEventListener("keydown", (e) => { if (e.key === "Enter") sendChat(); });

  $("ytClear").onclick = () => { $("ytResults").innerHTML = ""; };
  $("ytNext").onclick = playNext;
  $("ytClearQ").onclick = clearQueue;

  $("canvasSave").onclick = saveCanvas;
  $("canvasClear").onclick = clearCanvas;

  restoreApiKey();
  ensureSessionId();
  renderQueue();
  restoreCanvas();
  connectSSE();
    syncQueueFromServer();
</script>
</body>
</html>
"""
    return HTMLResponse(html)


@app.get("/api/public/modules")
def api_public_modules():
    """Public API: return modules.json data. For future real-time updates."""
    modules = load_modules_data()
    return {"modules": modules, "count": len(modules), "last_updated": _utc_now()}


@app.get("/api/public/benchmark")
def api_public_benchmark():
    """Public API: return benchmark.json data. For future real-time updates."""
    benchmark = load_benchmark_data()
    return {"benchmark": benchmark, "count": len(benchmark), "last_updated": _utc_now()}


# ============================================
# NEW WORLD-CLASS PAGES
# ============================================

@app.get("/pricing")
def pricing_page_route(lang: str = "ko"):
    """Pricing page with 3-tier plans."""
    return HTMLResponse(render_pricing_page_i18n(lang))


@app.get("/dashboard-preview")
def dashboard_preview_page_route(lang: str = "ko"):
    """Dashboard preview page."""
    return HTMLResponse(render_dashboard_page_i18n(lang))


@app.get("/canvas-preview")
def canvas_preview_page_route(lang: str = "ko"):
    """Canvas workspace preview page."""
    return HTMLResponse(render_canvas_page_i18n(lang))


@app.get("/login")
def login_page_route(lang: str = "ko"):
    """Login page."""
    return HTMLResponse(render_login_page_i18n(lang))


@app.get("/signup")
def signup_page_route(lang: str = "ko"):
    """Sign up page (redirects to login for now)."""
    return HTMLResponse(render_login_page_i18n(lang))


@app.get("/ceria-test")
def ceria_system_test_page():
    """Ceria Character Self System Test Page."""
    from pathlib import Path
    html_path = Path(__file__).parent.parent.parent / "public" / "ceria-system-test.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    else:
        return HTMLResponse("<h1>Test page not found</h1><p>Please ensure ceria-system-test.html exists in public/</p>", status_code=404)


# ============================================
# SSE STREAMING
# ============================================


@app.get("/agent/reports/stream")
def agent_reports_stream(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
    api_key: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    cursor: Optional[int] = Query(None),
):
    # EventSource cannot set headers, so allow api_key/org/project via query for this endpoint only.
    require_api_key(api_key or x_api_key, authorization)
    tenant = _tenant_from_headers(x_org_id or org_id, x_project_id or project_id)
    tenant_id = _tenant_key(tenant)
    start = int(cursor or 0)

    def gen():
        # snapshot first (not persisted)
        snap = stream_store.snapshot(tenant_id)
        current = stream_store.current_seq(tenant_id)
        yield _sse_event(current, "snapshot", snap)

        last_sent = start
        # replay backlog
        for ev in stream_store.replay(tenant_id, after_seq=last_sent, limit=1000):
            yield _sse_event(ev.seq, ev.event_type, ev.payload)
            last_sent = ev.seq

        # live poll
        ping_every = 15
        last_ping = time.time()
        while True:
            evs = stream_store.replay(tenant_id, after_seq=last_sent, limit=200)
            if evs:
                for ev in evs:
                    yield _sse_event(ev.seq, ev.event_type, ev.payload)
                    last_sent = ev.seq
                continue
            now = time.time()
            if now - last_ping >= ping_every:
                yield f"event: ping\ndata: {json.dumps({'ts': _utc_now()}, ensure_ascii=False)}\n\n"
                last_ping = now
            time.sleep(0.5)

    return StreamingResponse(gen(), media_type="text/event-stream")


# RED Command Types Registry (불변 계약)
RED_COMMAND_TYPES = {
    "external_share.execute",
    "external_share.prepare",
    "email.send",
    "slack.post",
    "github.create_issue",
    "system.sudo",
    "system.delete_production_data",
}


def _is_red_command(cmd_type: str) -> bool:
    """Check if command requires RED approval."""
    return cmd_type in RED_COMMAND_TYPES


@app.post("/sidecar/command", response_model=SidecarCommandAccepted, status_code=202)
def sidecar_command(
    body: SidecarCommandRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)
    tenant = _tenant_from_headers(x_org_id, x_project_id)
    tenant_id = _tenant_key(tenant)

    # Validate command_id (required for idempotency)
    if not body.command_id or not body.command_id.strip():
        raise HTTPException(status_code=400, detail={"error": {"code": "BAD_REQUEST", "message": "command_id is required"}})

    correlation_id = (body.client_context or {}).get("correlation_id") or f"corr-{uuid.uuid4().hex}"

    # Optional per-client session key used for queue/state scoping
    session_id = (body.client_context or {}).get("session_id") or (body.client_context or {}).get("client_session_id") or correlation_id
    causality = {
        "command_id": body.command_id,
        "type": body.type,
        "correlation_id": correlation_id,
        "surface": (body.client_context or {}).get("surface") or "sidecar",
    }

    # Emit agent_status: listening (command received)
    _emit_agent_status(tenant_id, "listening", {"command_type": body.type, "command_id": body.command_id})

    started = _mk_report(
        status="started",
        summary=f"accepted: {body.type}",
        risk="GREEN",
        causality=causality,
        ui_hint={"renderer": "sidecar.command.accepted"},
        data={"command": {"type": body.type, "params": body.params}, "snapshot": stream_store.snapshot(tenant_id)},
    )
    stream_store.append_event(tenant_id, "report", started)
    stream_store.add_worklog(tenant_id, {"title": "Command accepted", "body": f"{body.type}", "ts": _utc_now()})

    # Check RED approval requirement BEFORE execution
    if _is_red_command(body.type):
        snap = stream_store.snapshot(tenant_id)
        asks = snap.get("asks", [])
        approved = any(
            ask.get("meta", {}).get("command_id") == body.command_id
            and ask.get("decision") == "approve"
            for ask in asks
        )
        
        if not approved:
            # Create RED Ask and return 202 (execution blocked)
            # Emit agent_status: waiting_approval
            _emit_agent_status(tenant_id, "waiting_approval", {"command_type": body.type, "command_id": body.command_id})
            
            ask_id = f"ask-{uuid.uuid4().hex[:10]}"
            ask = {
                "ask_id": ask_id,
                "risk": "RED",
                "title": f"승인 필요: {body.type}",
                "body": "이 작업은 외부 전송/공유를 포함하며, 승인 없이는 실행되지 않습니다.",
                "meta": {"command_id": body.command_id, "type": body.type, "correlation_id": correlation_id},
            }
            stream_store.add_ask(tenant_id, ask)
            stream_store.set_autopilot(tenant_id, {"state": "blocked", "blocked_by_red": True})
            
            blocked_report = _mk_report(
                status="blocked",
                summary=f"RED approval required: {body.type}",
                risk="RED",
                causality=causality,
                ui_hint={"renderer": "approval.ask.created"},
                data={"ask": ask, "reason": "RED command requires approval", "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", blocked_report)
            logger.info(json.dumps({"event": "RED_BLOCKED", "command_id": body.command_id, "ask_id": ask_id}, ensure_ascii=False))
            
            # Return 202 immediately (execution will wait for approval)
            return SidecarCommandAccepted(
                command_id=body.command_id,
                first_followup_report_id=started["report_id"],
                correlation_id=correlation_id,
            )

    # execute (P0: in-process)
    # Emit agent_status: thinking (command execution started)
    _emit_agent_status(tenant_id, "thinking", {"command_type": body.type, "command_id": body.command_id})
    
    try:
        if body.type == "external_share.prepare":
            # Already handled by RED check above
            pass
        elif body.type == "external_share.execute":
            # This would only run if approved
            ask_id = f"ask-{uuid.uuid4().hex[:10]}"
            ask = {
                "ask_id": ask_id,
                "risk": "RED",
                "title": "외부 공유 승인 필요",
                "body": "외부 전송/공유는 승인 없이는 실행되지 않습니다.",
                "meta": {"command_id": body.command_id, "type": body.type, "correlation_id": correlation_id},
            }
            stream_store.add_ask(tenant_id, ask)
            stream_store.set_autopilot(tenant_id, {"state": "blocked", "blocked_by_red": True})
            done = _mk_report(
                status="ask",
                summary="created approval (RED)",
                risk="RED",
                causality=causality,
                ui_hint={"renderer": "approval.ask.created"},
                data={"ask": ask, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "youtube.search":
            q = (body.params or {}).get("query") or ""
            max_results = int((body.params or {}).get("max_results") or 5)
            if not q:
                raise ValueError("query is required")
            if not youtube_client.enabled():
                ask_id = f"ask-{uuid.uuid4().hex[:10]}"
                ask = {
                    "ask_id": ask_id,
                    "risk": "YELLOW",
                    "title": "YouTube API 키가 필요함",
                    "body": "YOUTUBE_API_KEY 환경변수를 설정하면 유튜브 검색/재생 기능을 사용할 수 있습니다.",
                    "meta": {"command_id": body.command_id, "type": body.type, "correlation_id": correlation_id},
                }
                stream_store.add_ask(tenant_id, ask)
                done = _mk_report(
                    status="ask",
                    summary="youtube disabled (missing api key)",
                    risk="YELLOW",
                    causality=causality,
                    ui_hint={"renderer": "approval.ask.created"},
                    data={"ask": ask, "snapshot": stream_store.snapshot(tenant_id)},
                )
                stream_store.append_event(tenant_id, "report", done)
            else:
                items = youtube_client.search(tenant=tenant_id, query=q, max_results=max_results, region=settings.youtube_default_region, language=settings.youtube_default_language)
                done = _mk_report(
                    status="done",
                    summary=f"youtube.search: {q}",
                    risk=settings.youtube_default_risk,
                    causality=causality,
                    ui_hint={"renderer": "youtube.search.results"},
                    data={"query": q, "results": items, "snapshot": stream_store.snapshot(tenant_id)},
                )
                stream_store.append_event(tenant_id, "report", done)

        elif body.type == "youtube.play":
            vid = (body.params or {}).get("video_id") or ""
            if not vid:
                raise ValueError("video_id is required")
            done = _mk_report(
                status="done",
                summary=f"youtube.play: {vid}",
                risk=settings.youtube_default_risk,
                causality=causality,
                ui_hint={"renderer": "youtube.play.embed"},
                data={"video_id": vid, "embed_url": f"https://www.youtube.com/embed/{vid}", "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "youtube.queue.add":
            vid = (body.params or {}).get("video_id") or ""
            title = (body.params or {}).get("title") or ""
            channel = (body.params or {}).get("channel") or ""
            if not vid:
                raise ValueError("video_id is required")
            item = {
                "video_id": vid,
                "title": title or vid,
                "channel": channel,
                "embed_url": f"https://www.youtube.com/embed/{vid}",
            }
            new_len = youtube_queue_store.add(tenant_id=tenant_id, session_id=session_id, item=item)
            done = _mk_report(
                status="done",
                summary=f"youtube.queue.add: {vid}",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "youtube.queue.updated"},
                data={"action": "add", "item": item, "length": new_len, "queue": youtube_queue_store.list(tenant_id=tenant_id, session_id=session_id), "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "youtube.queue.next":
            nxt = youtube_queue_store.pop_next(tenant_id=tenant_id, session_id=session_id)
            done = _mk_report(
                status="done",
                summary="youtube.queue.next",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "youtube.play.embed"},
                data={
                    "queue_item": nxt,
                    "video_id": (nxt or {}).get("video_id"),
                    "embed_url": (nxt or {}).get("embed_url"),
                    "queue": youtube_queue_store.list(tenant_id=tenant_id, session_id=session_id),
                    "snapshot": stream_store.snapshot(tenant_id),
                },
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "youtube.queue.list":
            q = youtube_queue_store.list(tenant_id=tenant_id, session_id=session_id)
            done = _mk_report(
                status="done",
                summary="youtube.queue.list",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "youtube.queue.updated"},
                data={"action": "list", "queue": q, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "youtube.queue.clear":
            youtube_queue_store.clear(tenant_id=tenant_id, session_id=session_id)
            done = _mk_report(
                status="done",
                summary="youtube.queue.clear",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "youtube.queue.updated"},
                data={"action": "clear", "queue": [], "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "rag.folder.ingest":
            folder = (body.params or {}).get("folder") or settings.rag_auto_ingest_path
            exts = (body.params or {}).get("extensions") or settings.rag_auto_ingest_extensions
            allowed = [e.strip() for e in str(exts).split(",") if e.strip()]
            res = rag_folder_ingestor.ingest_folder(
                tenant=tenant_id,
                folder=folder,
                allowed_exts=allowed,
                max_files=int((body.params or {}).get("max_files") or settings.rag_auto_ingest_max_files),
                max_file_mb=int((body.params or {}).get("max_file_mb") or settings.rag_auto_ingest_max_file_mb),
            )
            done = _mk_report(
                status="done" if res.ok else "error",
                summary="rag.folder.ingest",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "rag.folder.ingest.done"},
                data={"result": res.__dict__, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "rag.folder.status":
            raw = rag_folder_ingestor.last_result_raw(tenant_id)
            done = _mk_report(
                status="done",
                summary="rag.folder.status",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "rag.folder.status"},
                data={"raw": raw, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "rag.ingest":
            doc_id = (body.params or {}).get("doc_id") or ""
            text = (body.params or {}).get("text") or ""
            meta = (body.params or {}).get("meta") or {}
            if not doc_id or not text:
                raise ValueError("doc_id and text are required")
            res = rag_engine.ingest(tenant=tenant_id, doc_id=doc_id, text=text, meta=meta)
            done = _mk_report(
                status="done",
                summary=f"rag.ingest: {doc_id}",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "rag.ingest.done"},
                data={"result": res, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        elif body.type == "rag.query":
            q = (body.params or {}).get("query") or ""
            top_k = int((body.params or {}).get("top_k") or 5)
            if not q:
                raise ValueError("query is required")
            results = rag_engine.query(tenant=tenant_id, q=q, top_k=top_k)
            done = _mk_report(
                status="done",
                summary=f"rag.query: {q}",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "rag.query.results"},
                data={"query": q, "results": results, "snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

        else:
            done = _mk_report(
                status="done",
                summary=f"noop: {body.type}",
                risk="GREEN",
                causality=causality,
                ui_hint={"renderer": "noop"},
                data={"snapshot": stream_store.snapshot(tenant_id)},
            )
            stream_store.append_event(tenant_id, "report", done)

    except Exception as e:
        err = _mk_report(
            status="error",
            summary=str(e),
            risk="YELLOW",
            causality=causality,
            ui_hint={"renderer": "error"},
            data={"error": {"message": str(e)}, "snapshot": stream_store.snapshot(tenant_id)},
        )
        stream_store.append_event(tenant_id, "report", err)
        # Emit agent_status: idle (error occurred)
        _emit_agent_status(tenant_id, "idle", {"error": str(e)})

    # Emit agent_status: idle (command completed successfully)
    _emit_agent_status(tenant_id, "idle", {"command_type": body.type, "command_id": body.command_id, "completed": True})

    return SidecarCommandAccepted(
        command_id=body.command_id,
        first_followup_report_id=started["report_id"],
        correlation_id=correlation_id,
    )


@app.post("/approvals/{ask_id}/decide", response_model=ApprovalDecisionAccepted, status_code=202)
def approvals_decide(
    ask_id: str,
    body: ApprovalDecisionRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None),
):
    require_api_key(x_api_key, authorization)
    tenant = _tenant_from_headers(x_org_id, x_project_id)
    tenant_id = _tenant_key(tenant)

    removed = False
    if body.decision in ("approve", "reject"):
        removed = stream_store.remove_ask(tenant_id, ask_id)

    # unblock autopilot if no RED asks remain
    remaining = stream_store.list_asks(tenant_id)
    blocked = any((a.get("risk") == "RED") for a in remaining)
    stream_store.set_autopilot(tenant_id, {"state": "idle" if not blocked else "blocked", "blocked_by_red": blocked})

    # Emit agent_status based on approval decision
    if body.decision == "approve":
        _emit_agent_status(tenant_id, "idle", {"approval": "approved", "ask_id": ask_id})
    else:
        _emit_agent_status(tenant_id, "idle", {"approval": "rejected", "ask_id": ask_id})

    report = _mk_report(
        status="done",
        summary=f"approval {body.decision}: {ask_id}",
        risk="GREEN",
        causality={"ask_id": ask_id, "decision": body.decision, "correlation_id": body.correlation_id},
        ui_hint={"renderer": "approval.decided"},
        data={"removed": removed, "snapshot": stream_store.snapshot(tenant_id)},
    )
    stream_store.add_worklog(tenant_id, {"title": "Approval", "body": f"{body.decision} {ask_id}", "ts": _utc_now()})
    stream_store.append_event(tenant_id, "report", report)

    return ApprovalDecisionAccepted(first_followup_report_id=report["report_id"], correlation_id=body.correlation_id)



# -----------------------
# RAG Auto Ingest Scheduler (03:00 KST default)
# -----------------------

def _seconds_until_next_kst_run(hour: int, minute: int) -> float:
    tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(tz)
    run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if run <= now:
        run = run + timedelta(days=1)
    return max(1.0, (run - now).total_seconds())


def _rag_auto_ingest_once() -> None:
    try:
        tenant_id = stream_store.tenant_id(settings.rag_auto_ingest_org_id, settings.rag_auto_ingest_project_id)
        allowed = [e.strip() for e in str(settings.rag_auto_ingest_extensions).split(",") if e.strip()]
        res = rag_folder_ingestor.ingest_folder(
            tenant=tenant_id,
            folder=settings.rag_auto_ingest_path,
            allowed_exts=allowed,
            max_files=int(settings.rag_auto_ingest_max_files),
            max_file_mb=int(settings.rag_auto_ingest_max_file_mb),
        )
        report = _mk_report(
            status="done" if res.ok else "error",
            summary="rag.auto.ingest",
            risk="GREEN",
            causality={"type": "scheduler"},
            ui_hint={"renderer": "rag.folder.ingest.done"},
            data={"result": res.__dict__, "snapshot": stream_store.snapshot(tenant_id)},
        )
        stream_store.add_worklog(
            tenant_id,
            {"title": "RAG Auto Ingest", "body": f"chunks={res.ingested_chunks} pending_hwp={res.pending_hwp}", "ts": _utc_now()},
        )
        stream_store.append_event(tenant_id, "report", report)
    except Exception as e:
        logger.exception("rag auto ingest failed: %s", e)


def _rag_auto_ingest_loop() -> None:
    while True:
        secs = _seconds_until_next_kst_run(int(settings.rag_auto_ingest_hour), int(settings.rag_auto_ingest_minute))
        time.sleep(secs)
        _rag_auto_ingest_once()


@app.on_event("startup")
def _startup_rag_scheduler() -> None:
    if bool(settings.rag_auto_ingest_enabled):
        t = threading.Thread(target=_rag_auto_ingest_loop, daemon=True)
        t.start()
        logger.info("RAG auto ingest scheduler enabled: %s @ %02d:%02d KST", settings.rag_auto_ingest_path, settings.rag_auto_ingest_hour, settings.rag_auto_ingest_minute)


# ============================================================
# Windows Node Management Endpoints
# ============================================================

class NodePairingCreateResponse(BaseModel):
    """페어링 코드 생성 응답"""
    pairing_code: str
    expires_in: int  # seconds


class NodePairingClaimRequest(BaseModel):
    """페어링 코드 사용 요청"""
    pairing_code: str
    node_id: str
    hostname: str
    os_version: Optional[str] = None
    agent_version: Optional[str] = None


class NodePairingClaimResponse(BaseModel):
    """페어링 코드 사용 응답"""
    node_token: str  # JWT (미래 구현)
    node_id: str
    tenant_id: str


class NodeCommandRequest(BaseModel):
    """노드 명령 전송 요청"""
    node_id: str
    command_type: str  # "local.folder.ingest" 등
    params: Dict[str, Any] = Field(default_factory=dict)


class NodeCommandResponse(BaseModel):
    """노드 명령 전송 응답 (202 Accepted)"""
    command_id: str
    node_id: str
    accepted: bool = True


class NodeReportRequest(BaseModel):
    """노드 리포트 업로드 요청"""
    node_id: str
    command_id: str
    status: str  # "in_progress" | "completed" | "failed"
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class NodeReportResponse(BaseModel):
    """노드 리포트 업로드 응답"""
    received: bool = True
    report_id: str


class NodeStateResponse(BaseModel):
    """노드 상태 조회 응답"""
    node_id: str
    status: str  # "online" | "offline" | "enrolled"
    last_seen: Optional[str] = None
    connection_type: Optional[str] = None
    info: Optional[Dict[str, Any]] = None


@app.post("/node/pairing/create", status_code=200, response_model=NodePairingCreateResponse)
def node_pairing_create(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: str = Header(...),
    x_project_id: str = Header(...)
):
    """
    페어링 코드 생성 (6자리, 5분 TTL)
    
    User → Dashboard: "새 노드 추가" 클릭
    Backend: 페어링 코드 생성
    """
    require_api_key(x_api_key, authorization)
    tenant_id = f"{x_org_id}:{x_project_id}"
    
    pairing_code = node_store.create_pairing_code(tenant_id, ttl_seconds=300)
    
    logger.info(f"[Node Pairing] Created code={pairing_code} tenant={tenant_id}")
    
    # SSE로 페어링 코드 생성 알림
    report = _mk_report(
        status="done",
        summary=f"페어링 코드 생성: {pairing_code}",
        risk="GREEN",
        causality={
            "correlation_id": f"pairing-create-{pairing_code}",
            "command_id": None,
            "ask_id": None,
            "type": "node.pairing.create"
        },
        ui_hint={
            "surface": "dashboard",
            "cards": [{
                "type": "node_pairing",
                "title": "노드 페어링 코드",
                "body": f"페어링 코드: **{pairing_code}**\n\nWindows Node에서 다음 명령을 실행하세요:\n```\nnode_agent.exe --enroll {pairing_code}\n```\n\n유효 시간: 5분"
            }]
        },
        data={"pairing_code": pairing_code, "expires_in": 300}
    )
    stream_store.append_event(tenant_id, "report", report)
    
    return NodePairingCreateResponse(pairing_code=pairing_code, expires_in=300)


@app.post("/node/pairing/claim", status_code=200, response_model=NodePairingClaimResponse)
def node_pairing_claim(body: NodePairingClaimRequest):
    """
    페어링 코드 사용 (일회용)
    
    Node → Backend: 페어링 요청
    Backend: 노드 등록 + 토큰 발급
    """
    node_info = {
        "hostname": body.hostname,
        "os_version": body.os_version,
        "agent_version": body.agent_version
    }
    
    tenant_id = node_store.claim_pairing_code(
        pairing_code=body.pairing_code,
        node_id=body.node_id,
        node_info=node_info
    )
    
    if not tenant_id:
        raise HTTPException(status_code=404, detail="Invalid or expired pairing code")
    
    logger.info(f"[Node Pairing] Claimed code={body.pairing_code} node={body.node_id} tenant={tenant_id}")
    
    # TODO: JWT 토큰 발급 (미래 구현)
    node_token = f"node-token-{body.node_id}-{uuid.uuid4().hex[:8]}"
    
    # SSE로 노드 등록 알림
    report = _mk_report(
        status="done",
        summary=f"노드 등록 완료: {body.node_id}",
        risk="GREEN",
        causality={
            "correlation_id": f"pairing-claim-{body.node_id}",
            "command_id": None,
            "ask_id": None,
            "type": "node.pairing.claim"
        },
        ui_hint={
            "surface": "dashboard",
            "cards": [{
                "type": "node_enrolled",
                "title": "노드 등록 완료",
                "body": f"**{body.node_id}** (hostname: {body.hostname})\n\n노드가 성공적으로 등록되었습니다."
            }]
        },
        data={"node_id": body.node_id, "hostname": body.hostname}
    )
    stream_store.append_event(tenant_id, "report", report)
    
    return NodePairingClaimResponse(
        node_token=node_token,
        node_id=body.node_id,
        tenant_id=tenant_id
    )


@app.get("/node/poll", status_code=200)
def node_poll(
    node_id: str = Query(...),
    node_token: str = Query(...)
):
    """
    노드 Poll 엔드포인트 (Fallback for WSS failure)
    
    Node → Backend: HTTP Long Polling (30초 타임아웃)
    Backend: 큐에 있는 명령 반환
    """
    # TODO: JWT 검증 (미래 구현)
    # 현재는 node_token이 "node-token-{node_id}-*" 형식인지만 확인
    if not node_token.startswith(f"node-token-{node_id}"):
        raise HTTPException(status_code=403, detail="Invalid node token")
    
    # tenant_id 추출 (Redis에서 조회)
    # 임시로 모든 테넌트 검색 (비효율적이지만 프로토타입용)
    tenant_id = None
    for tid in ["demo:demo", "org123:proj456"]:  # 하드코딩된 테넌트 목록
        node_state = node_store.get_node_state(tid, node_id)
        if node_state:
            tenant_id = tid
            break
    
    if not tenant_id:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # 연결 상태 업데이트
    node_store.set_node_state(tenant_id, node_id, "online", "poll")
    
    # 명령 가져오기
    commands = node_store.pop_commands(tenant_id, node_id, limit=10)
    
    logger.info(f"[Node Poll] node={node_id} tenant={tenant_id} commands={len(commands)}")
    
    return {
        "commands": commands,
        "timestamp": _utc_now()
    }


@app.post("/node/command", status_code=202, response_model=NodeCommandResponse)
def node_command(
    body: NodeCommandRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: str = Header(...),
    x_project_id: str = Header(...)
):
    """
    노드에게 명령 전송
    
    User → Dashboard: "로컬 폴더 스캔" 버튼 클릭
    Backend: 명령을 Redis 큐에 추가 → 202 Accepted
    """
    require_api_key(x_api_key, authorization)
    tenant_id = f"{x_org_id}:{x_project_id}"
    
    command_id = f"cmd-{uuid.uuid4().hex[:12]}"
    
    command = {
        "command_id": command_id,
        "type": body.command_type,
        "params": body.params
    }
    
    # 명령 큐에 추가
    node_store.push_command(tenant_id, body.node_id, command)
    
    logger.info(f"[Node Command] command_id={command_id} node={body.node_id} type={body.command_type}")
    
    # SSE로 명령 전송 알림
    report = _mk_report(
        status="started",
        summary=f"명령 전송: {body.command_type}",
        risk="GREEN",
        causality={
            "correlation_id": command_id,
            "command_id": command_id,
            "ask_id": None,
            "type": body.command_type
        },
        ui_hint={
            "surface": "sidecar",
            "cards": [{
                "type": "command_sent",
                "title": f"명령 전송: {body.command_type}",
                "body": f"Node: **{body.node_id}**\nParams: {json.dumps(body.params, indent=2)}"
            }]
        },
        data={"command": command}
    )
    stream_store.append_event(tenant_id, "report", report)
    
    return NodeCommandResponse(command_id=command_id, node_id=body.node_id)


@app.post("/node/report", status_code=200, response_model=NodeReportResponse)
def node_report(body: NodeReportRequest):
    """
    노드 리포트 수신
    
    Node → Backend: 진행 상황 또는 최종 결과 업로드
    Backend: SSE로 UI에 전파
    """
    # TODO: JWT 검증
    # 임시로 node_id 기반으로 tenant_id 조회
    tenant_id = None
    for tid in ["demo:demo", "org123:proj456"]:
        node_state = node_store.get_node_state(tid, body.node_id)
        if node_state:
            tenant_id = tid
            break
    
    if not tenant_id:
        raise HTTPException(status_code=404, detail="Node not found")
    
    report_id = f"r-node-{uuid.uuid4().hex[:12]}"
    
    # 리포트 생성
    report = _mk_report(
        report_id=report_id,
        status=body.status,
        summary=f"Node 리포트: {body.command_id}",
        risk="GREEN" if body.status != "failed" else "YELLOW",
        causality={
            "correlation_id": body.command_id,
            "command_id": body.command_id,
            "ask_id": None,
            "type": "node.report"
        },
        ui_hint={
            "surface": "dashboard",
            "cards": [{
                "type": "node_report",
                "title": f"Node 리포트: {body.status}",
                "body": f"Node: **{body.node_id}**\nCommand: {body.command_id}\n\n{json.dumps(body.progress or body.result or {}, indent=2)}"
            }]
        },
        data={
            "node_id": body.node_id,
            "command_id": body.command_id,
            "status": body.status,
            "progress": body.progress,
            "result": body.result,
            "error": body.error
        }
    )
    
    # SSE 전파
    stream_store.append_event(tenant_id, "report", report)
    
    # 완료 시 RAG 인제스트 (result에 chunks가 있는 경우)
    if body.status == "completed" and body.result and "chunks" in body.result:
        chunks = body.result["chunks"]
        ingested = 0
        for chunk in chunks[:100]:  # 최대 100개씩
            try:
                rag_engine.ingest(
                    tenant=tenant_id,
                    doc_id=chunk["doc_id"],
                    text=chunk["text"],
                    meta=chunk.get("meta", {})
                )
                ingested += 1
            except Exception as e:
                logger.error(f"[Node Report] RAG ingest failed: {e}")
        
        logger.info(f"[Node Report] RAG ingested {ingested}/{len(chunks)} chunks from node={body.node_id}")
        
        # RAG 인제스트 완료 리포트
        rag_report = _mk_report(
            status="done",
            summary=f"RAG 인제스트 완료: {ingested}개 청크",
            risk="GREEN",
            causality={
                "correlation_id": body.command_id,
                "command_id": body.command_id,
                "ask_id": None,
                "type": "rag.ingest"
            },
            ui_hint={
                "surface": "dashboard",
                "cards": [{
                    "type": "rag_ingest_done",
                    "title": "RAG 인제스트 완료",
                    "body": f"Node **{body.node_id}**에서 **{ingested}개** 청크를 RAG 인덱스에 추가했습니다."
                }]
            },
            data={"ingested": ingested, "total": len(chunks)}
        )
        stream_store.append_event(tenant_id, "report", rag_report)
    
    logger.info(f"[Node Report] node={body.node_id} command={body.command_id} status={body.status}")
    
    return NodeReportResponse(received=True, report_id=report_id)


@app.get("/node/list", status_code=200)
def node_list(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: str = Header(...),
    x_project_id: str = Header(...),
    status_filter: Optional[str] = Query(None)
):
    """
    테넌트의 노드 목록 조회
    
    Dashboard: 노드 상태 표시
    """
    require_api_key(x_api_key, authorization)
    tenant_id = f"{x_org_id}:{x_project_id}"
    
    nodes = node_store.list_tenant_nodes(tenant_id, status_filter=status_filter)
    
    return {"nodes": nodes, "total": len(nodes)}
