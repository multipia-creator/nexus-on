from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

import pika

from shared.settings import settings
from shared.logging_utils import get_logger
from shared.mq_utils import declare_queues, publish_json, choose_retry_queue
from shared.notify import route_payload

logger = get_logger("alarm_worker")


def _parse_body(raw: bytes) -> Dict[str, Any]:
    try:
        js = json.loads(raw.decode("utf-8"))
        if isinstance(js, dict):
            return js
    except Exception:
        pass
    return {"raw": raw.decode("utf-8", errors="replace")}


def _handle_message(ch, method, props, body: bytes) -> None:
    corr = getattr(props, "correlation_id", "") or ""
    headers = getattr(props, "headers", {}) or {}
    try:
        retry_count = int(headers.get("x-retry-count", 0) or 0)
    except Exception:
        retry_count = 0

    payload = _parse_body(body)

    payload.setdefault("origin", "alarm_worker")
    rv = payload.get("routed_via")
    if not isinstance(rv, list):
        rv = []
    if "alarm_worker" not in [str(x) for x in rv]:
        rv.append("alarm_worker")
    payload["routed_via"] = rv

    # Ensure minimal schema
    payload.setdefault("event", "alarm")
    payload.setdefault("severity", "error")
    payload.setdefault("title", "NEXUS Alarm")
    payload.setdefault("message", payload.get("message") or payload.get("raw") or "")

    try:
        res = route_payload(payload, prefer="slack", allow_alarm_queue=False, allow_github=True)
        ok = bool(res.get("overall_ok"))
        if ok:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        raise RuntimeError("route_payload_overall_ok=false")
    except Exception as e:
        # Never nack/requeue. Republish to retry/DLQ queues.
        err = f"{type(e).__name__}:{e}"
        max_r = int(getattr(settings, "alarm_max_retries", 2) or 2)
        retry_prefix = getattr(settings, "alarm_retry_queue_prefix", "nexus.alarm.retry") or "nexus.alarm.retry"
        dlq = getattr(settings, "alarm_dlq_queue", "nexus.alarm.dlq") or "nexus.alarm.dlq"

        hdr2 = dict(headers)
        hdr2["x-last-error"] = err[:200]

        try:
            if retry_count < max_r:
                q, secs = choose_retry_queue(retry_prefix, retry_count)
                hdr2["x-retry-count"] = retry_count + 1
                hdr2["x-retry-after-seconds"] = secs
                publish_json(ch, q, payload, correlation_id=(corr or ""), headers=hdr2)
                logger.warning({"event": "ALARM_WORKER_RETRY", "queue": q, "retry_count": retry_count + 1, "corr": corr, "err": err})
            else:
                hdr2["x-retry-count"] = retry_count
                publish_json(ch, dlq, {"payload": payload, "error": err}, correlation_id=(corr or ""), headers=hdr2)
                logger.error({"event": "ALARM_WORKER_DLQ", "queue": dlq, "retry_count": retry_count, "corr": corr, "err": err})
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    url = getattr(settings, "rabbitmq_url", "") or os.getenv("RABBITMQ_URL") or ""
    if not url:
        raise SystemExit("RABBITMQ_URL not set")

    task_q = getattr(settings, "alarm_queue", "nexus.alarm") or "nexus.alarm"
    retry_prefix = getattr(settings, "alarm_retry_queue_prefix", "nexus.alarm.retry") or "nexus.alarm.retry"
    dlq = getattr(settings, "alarm_dlq_queue", "nexus.alarm.dlq") or "nexus.alarm.dlq"

    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()

    declare_queues(ch, task_queue=task_q, retry_prefix=retry_prefix, dlq_queue=dlq)

    ch.basic_qos(prefetch_count=10)
    ch.basic_consume(queue=task_q, on_message_callback=_handle_message)

    logger.info({"event": "ALARM_WORKER_START", "queue": task_q, "retry_prefix": retry_prefix, "dlq": dlq})
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
