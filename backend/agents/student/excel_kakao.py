import os
import json
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import pika
import requests

from shared.logging_utils import setup_logging
from shared.settings import settings
from shared.mq_utils import declare_queues, publish_json, choose_retry_queue
from shared.security import sign_payload
from shared.envelope import attach_failure
from shared.task_lock import TaskLock

setup_logging()
logger = logging.getLogger("nexus_agent_excel_kakao")

SUPERVISOR_URL = os.getenv("SUPERVISOR_URL", "http://supervisor:8000")

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def callback_update(payload: Dict[str, Any]):
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "X-API-Key": settings.nexus_api_key}
    if settings.callback_signature_secret:
        headers["X-Signature"] = sign_payload(settings.callback_signature_secret, body)

    r = requests.post(f"{SUPERVISOR_URL}/agent/callback", headers=headers, data=body, timeout=10)
    r.raise_for_status()

def classify_failure_code(exc: Exception) -> str:
    # requests.HTTPError carries response with status_code
    try:
        import requests
        if isinstance(exc, requests.HTTPError) and exc.response is not None:
            sc = exc.response.status_code
            if sc == 422:
                return "SCHEMA_REPAIR_FAILED"
            if sc == 503:
                return "PROVIDER_DISABLED"
            if sc == 401 or sc == 403:
                return "PROVIDER_AUTH_ERROR"
            if sc == 429:
                return "PROVIDER_RATE_LIMIT"
            if sc == 408:
                return "PROVIDER_TIMEOUT"
            if 500 <= sc < 600:
                return "PROVIDER_UPSTREAM_ERROR"
    except Exception:
        pass
    name = type(exc).__name__.lower()
    if "timeout" in name:
        return "PROVIDER_TIMEOUT"
    return "UNKNOWN"


def llm_generate_schema(prompt: str, schema_name: str) -> Dict[str, Any]:
    """Use Supervisor /llm/generate schema mode (enforced)."""
    headers = {"Content-Type": "application/json", "X-API-Key": settings.nexus_api_key}
    body = {"input_text": prompt, "schema_name": schema_name, "allow_repair": True}
    r = requests.post(f"{SUPERVISOR_URL}/llm/generate", headers=headers, json=body, timeout=60)
    # If schema validation fails (422) or LLM disabled (503 when required), raise for outer handler.
    r.raise_for_status()
    return r.json()

def process_excel_kakao(task: Dict[str, Any]) -> Dict[str, Any]:
    payload = task.get("payload", {})
    members = payload.get("members", [])
    group_name = payload.get("group_name", "unknown")

    # demo latency
    time.sleep(1.0)

    # Structured Output enforced for operational reliability
    schema_name = "excel_kakao_output"
    prompt = (
        "You MUST output only valid JSON (no markdown, no code fences).\n"
        "JSON format: {\n"
        '  "action": "send_message",\n'
        '  "result": {"text": "[공지] ... (끝에 마침표)"},\n'
        '  "warnings": []\n'
        "}\n\n"
        "Rules:\n"
        "- output must be Korean\n"
        "- one line only\n"
        "- must end with a period (.)\n\n"
        f"Context:\n- group_name: {group_name}\n- member_count: {len(members)}\n"
    )

    try:
        llm_resp = llm_generate_schema(prompt, schema_name=schema_name)
        data = llm_resp.get("data", {}) or {}
        msg = (data.get("result") or {}).get("text") or "[공지] 알림입니다."
        llm_meta = {"provider": llm_resp.get("provider"), "model": llm_resp.get("model"), "repaired": llm_resp.get("repaired", False)}
    except Exception as e:
        # Hard fallback to keep the agent functional
        msg = f"[공지] {group_name} 단톡방이 생성되었습니다. (LLM 실패)."
        llm_meta = {"provider": "none", "model": "none", "error": str(e)}

    return {
        "group_name": group_name,
        "member_count": len(members),
        "assistant_message": msg,
        "llm": llm_meta,
        "note": "demo worker processed task (no real Kakao integration)"
    }

def main():
    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    declare_queues(ch, settings.task_queue, settings.retry_queue_prefix, settings.dlq_queue)
    ch.basic_qos(prefetch_count=1)

    task_lock = TaskLock()

    logger.info(json.dumps({"event":"WORKER_START","queue":settings.task_queue,"provider":settings.llm_provider}, ensure_ascii=False))

    def on_message(channel, method, properties, body):
        task = json.loads(body.decode("utf-8"))
        task_id = task.get("task_id", "unknown")
        retry_count = 0
        if properties and properties.headers:
            retry_count = int(properties.headers.get("x-retry-count", 0))

        callback_update({"event":"task_status","task_id":task_id,"status":"running","ts":utc_now()})

        try:
            result = process_excel_kakao(task)
            callback_update({"event":"task_status","task_id":task_id,"status":"succeeded","result":result,"ts":utc_now()})
            channel.basic_ack(method.delivery_tag)
        except Exception as e:
            err = {"message": str(e), "type": type(e).__name__}
            callback_update({"event":"task_status","task_id":task_id,"status":"failed","error":err,"ts":utc_now()})

            failure_code = classify_failure_code(e)
            task_failed = attach_failure(task, failure_code, err)

            lock_state = task_lock.is_locked(task_id)
            if lock_state.locked:
                failure_code = failure_code or "UNKNOWN"
                # force DLQ when locked
                headers = (properties.headers or {}) if properties else {}
                headers["x-retry-count"] = retry_count
                headers["failure_code"] = failure_code
                publish_json(channel, settings.dlq_queue, task_failed, correlation_id=task_id, headers=headers)
                channel.basic_ack(method.delivery_tag)
                return

            # Retry policy: use configured retry queues, then DLQ
            if retry_count < settings.max_retries:
                next_retry = retry_count + 1
                headers = (properties.headers or {}) if properties else {}
                headers["x-retry-count"] = next_retry
                headers["failure_code"] = failure_code
                retry_queue = choose_retry_queue(settings.retry_queue_prefix, next_retry)
                publish_json(channel, retry_queue, task_failed, correlation_id=task_id, headers=headers)
                channel.basic_ack(method.delivery_tag)
            else:
                headers = (properties.headers or {}) if properties else {}
                headers["x-retry-count"] = retry_count
                headers["failure_code"] = failure_code
                publish_json(channel, settings.dlq_queue, task_failed, correlation_id=task_id, headers=headers)
                channel.basic_ack(method.delivery_tag)

    ch.basic_consume(queue=settings.task_queue, on_message_callback=on_message, auto_ack=False)
    ch.start_consuming()

if __name__ == "__main__":
    main()
