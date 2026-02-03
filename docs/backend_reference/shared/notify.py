from __future__ import annotations

import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

try:
    import pika  # type: ignore
    _HAS_PIKA = True
except Exception:
    pika = None  # type: ignore
    _HAS_PIKA = False

from shared.alerter import send_webhook
from shared.github_client import create_issue, upsert_alert_issue
from shared.settings import settings
from shared.logging_utils import get_logger

logger = get_logger(__name__)

try:
    from shared.alert_dedupe import AlertDedupe  # type: ignore
    _HAS_DEDUPE = True
except Exception:
    AlertDedupe = None  # type: ignore
    _HAS_DEDUPE = False


@dataclass
class NotifyResult:
    ok: bool
    channel: str
    status: Optional[int] = None
    error: Optional[str] = None


def _alarm_publish_allowed(payload: dict) -> bool:
    """Hard guard against alarm queue loops and unapproved publishes."""
    origin = str((payload or {}).get("origin") or "").strip().lower()
    if origin in ("alarm_worker", "alarm_queue_worker", "alarm-queue-worker"):
        return False
    routed_via = (payload or {}).get("routed_via") or []
    if isinstance(routed_via, list):
        if any(str(x).strip().lower() in ("alarm_worker", "alarm_queue") for x in routed_via):
            return False
    # explicit opt-out
    if bool((payload or {}).get("suppress_alarm_queue")):
        return False
    return True



def _publish_alarm(payload: dict) -> bool:
    """Best-effort publish to RabbitMQ alarm queue."""
    if not _HAS_PIKA:
        return False
    if not _alarm_publish_allowed(payload):
        return False
    try:
        url = getattr(settings, "rabbitmq_url", "") or os.getenv("RABBITMQ_URL") or ""
        q = getattr(settings, "alarm_queue", "") or os.getenv("ALARM_QUEUE") or "nexus.alarm"
        if not url or not q:
            return False
        conn = pika.BlockingConnection(pika.URLParameters(url))
        ch = conn.channel()
        ch.queue_declare(queue=q, durable=True)
        ch.basic_publish(
            exchange="",
            routing_key=q,
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=2,
                correlation_id=str(payload.get("correlation_id") or ""),
                content_type="application/json",
            ),
        )
        conn.close()
        return True
    except Exception:
        return False


def _issue_body(title: str, text: str, payload: dict) -> str:
    body = []
    body.append(f"### {title}")
    body.append("")
    body.append("```json")
    body.append(json.dumps(payload, ensure_ascii=False, indent=2))
    body.append("```")
    body.append("")
    if text:
        body.append(text)
    return "\n".join(body)


def _post_json(url: str, payload: Dict[str, Any], timeout_s: int = 10) -> NotifyResult:
    try:
        r = requests.post(url, json=payload, timeout=timeout_s)
        if 200 <= r.status_code < 300:
            return NotifyResult(ok=True, channel="webhook", status=r.status_code)
        return NotifyResult(ok=False, channel="webhook", status=r.status_code, error=(r.text or "")[:200])
    except Exception as e:
        return NotifyResult(ok=False, channel="webhook", error=str(e))


def notify_slack(text: str) -> NotifyResult:
    url = getattr(settings, "slack_webhook_url", "") or os.getenv("SLACK_WEBHOOK_URL") or ""
    if not url:
        return NotifyResult(ok=False, channel="slack", error="no_slack_webhook")
    return _post_json(url, {"text": text}, timeout_s=10)


def notify_teams(title: str, text: str) -> NotifyResult:
    url = getattr(settings, "teams_webhook_url", "") or os.getenv("TEAMS_WEBHOOK_URL") or ""
    if not url:
        return NotifyResult(ok=False, channel="teams", error="no_teams_webhook")
    payload = {"title": title, "text": text}
    return _post_json(url, payload, timeout_s=10)


def _dedupe_gate(dedupe_key: str) -> tuple[bool, int]:
    dk = (dedupe_key or "").strip()
    if not dk:
        return True, 0
    if not _HAS_DEDUPE or AlertDedupe is None:
        return True, 0
    try:
        res = AlertDedupe().allow(dk)
        return bool(getattr(res, "allowed", True)), int(getattr(res, "ttl_seconds", 0) or 0)
    except Exception:
        # Fail-open: do not block alerts if dedupe backend is unavailable
        return True, 0


def route_payload(
    payload: Dict[str, Any],
    *,
    prefer: str = "slack",
    allow_alarm_queue: bool = True,
    allow_github: bool = True,
) -> Dict[str, Any]:
    """Route a prebuilt payload through the notification stack.

    Used by both direct `notify()` calls and alarm-queue consumers.
    When consuming from the alarm queue, set allow_alarm_queue=False to prevent loop.
    """
    payload.setdefault("origin", "notify")
    rv = payload.get("routed_via")
    if not isinstance(rv, list):
        rv = []
    payload["routed_via"] = rv

    title = str(payload.get("title") or "NEXUS Notification")
    message = str(payload.get("message") or payload.get("text") or "")
    event = str(payload.get("event") or "alarm")
    severity = str(payload.get("severity") or "error")
    dedupe_key = str(payload.get("dedupe_key") or "")

    allowed, ttl = _dedupe_gate(dedupe_key)
    if not allowed:
        return {
            "overall_ok": True,
            "results": [{"channel": "dedupe_suppressed", "ok": True, "status": None, "error": None, "ttl_seconds": ttl}],
        }

    results: list[dict] = []

    # (1) Unified alert webhook routing
    try:
        res = send_webhook(event, payload)
        ok = bool(getattr(res, "ok", False))
        results.append({"channel": "alert_webhook", "ok": ok, "status": getattr(res, "status_code", None), "error": getattr(res, "error", None)})
        if ok:
            return {"overall_ok": True, "results": results}
    except Exception as e:
        results.append({"channel": "alert_webhook", "ok": False, "status": None, "error": str(e)})

    # (2) Slack/Teams webhooks (settings driven)
    prefer2 = (prefer or "slack").lower().strip()
    try:
        if prefer2 in ("slack", "both"):
            r = notify_slack(f"*{title}*\n{message}")
            results.append({"channel": "slack", "ok": r.ok, "status": r.status, "error": r.error})
            if r.ok and prefer2 != "both":
                return {"overall_ok": True, "results": results}
        if prefer2 in ("teams", "both"):
            r = notify_teams(title, message)
            results.append({"channel": "teams", "ok": r.ok, "status": r.status, "error": r.error})
            if r.ok and prefer2 != "both":
                return {"overall_ok": True, "results": results}
    except Exception as e:
        results.append({"channel": "legacy_webhook", "ok": False, "status": None, "error": str(e)})

    # (3) Alarm queue fallback (optional)
    if allow_alarm_queue:
        try:
            ok = _publish_alarm(payload)
            results.append({"channel": "alarm_queue", "ok": ok, "status": None, "error": None if ok else "publish_failed_or_disabled"})
            if ok:
                return {"overall_ok": True, "results": results}
        except Exception as e:
            results.append({"channel": "alarm_queue", "ok": False, "status": None, "error": str(e)})

    # (4) GitHub issue fallback (optional + dedupe upsert)
    if allow_github:
        try:
            labels = ["ops", "alert", f"sev:{severity}"]
            if event:
                labels.append(f"event:{event}")
            entry = _issue_body(title, message, payload)
            header = f"### NEXUS Alert\n\n- event: `{event}`\n- severity: `{severity}`\n- dedupe_key: `{dedupe_key or 'n/a'}`\n"
            title2 = f"[{event}] {title}"
            if dedupe_key:
                gh = upsert_alert_issue(title=title2, header=header, entry=entry, dedupe_key=dedupe_key, labels=labels)
            else:
                gh = create_issue(title2[:240], entry, labels=labels)
            ok = bool(getattr(gh, "ok", False))
            results.append({
                "channel": "github_issue",
                "ok": ok,
                "status": getattr(gh, "status_code", None),
                "error": getattr(gh, "error", None),
                "url": getattr(gh, "url", None),
            })
            if ok:
                return {"overall_ok": True, "results": results}
        except Exception as e:
            results.append({"channel": "github_issue", "ok": False, "status": None, "error": str(e)})

    return {"overall_ok": False, "results": results}


def notify(
    message: str,
    *,
    title: str = "NEXUS Notification",
    prefer: str = "slack",
    event: str = "alarm",
    severity: str = "error",
    dedupe_key: str = "",
    extra: dict | None = None,
) -> Dict[str, Any]:
    """Multi-route notification (backward compatible)."""
    payload = {
        "ts_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": event,
        "severity": severity,
        "title": title,
        "message": message,
        "dedupe_key": dedupe_key,
        "extra": extra or {},
    }
    return route_payload(payload, prefer=prefer, allow_alarm_queue=True, allow_github=True)
