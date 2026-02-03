from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from shared.logging_utils import get_logger
from shared.settings import settings

logger = get_logger("alerter")

@dataclass
class AlertResult:
    ok: bool
    status_code: Optional[int] = None
    error: Optional[str] = None

def resolve_webhook_url(event: str) -> str:
    # Route by event type
    if event in ("dlq_alarm", "alarm") and getattr(settings, "alert_webhook_url_alarm", ""):
        return settings.alert_webhook_url_alarm
    if event in ("hold", "dlq_hold") and getattr(settings, "alert_webhook_url_hold", ""):
        return settings.alert_webhook_url_hold
    return getattr(settings, "alert_webhook_url", "") or ""


def send_webhook(event: str, payload: Dict[str, Any]) -> AlertResult:
    url = resolve_webhook_url(event)
    if not url:
        return AlertResult(False, None, "ALERT_WEBHOOK_URL not set")

    body = {"event": event, "payload": payload}
    try:
        r = requests.post(url, json=body, timeout=10)
        if 200 <= r.status_code < 300:
            return AlertResult(True, r.status_code, None)
        logger.warning({"event":"ALERT_WEBHOOK_NON2XX","status":r.status_code,"text":r.text[:500]})
        return AlertResult(False, r.status_code, f"non-2xx: {r.status_code}")
    except Exception as e:
        logger.warning({"event":"ALERT_WEBHOOK_ERROR","err":str(e)})
        return AlertResult(False, None, str(e))
