import json
from typing import Any, Dict, Tuple
import pika

RETRY_BACKOFFS_SECONDS = [5, 30, 300]  # 5s, 30s, 5m

def declare_queues(ch, task_queue: str, retry_prefix: str, dlq_queue: str) -> None:
    # main
    ch.queue_declare(queue=task_queue, durable=True)

    # retry queues (fixed TTL) that dead-letter back to main queue
    for secs in RETRY_BACKOFFS_SECONDS:
        q = f"{retry_prefix}.{secs}s"
        args = {
            "x-message-ttl": secs * 1000,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": task_queue,
        }
        ch.queue_declare(queue=q, durable=True, arguments=args)

    # DLQ
    ch.queue_declare(queue=dlq_queue, durable=True)

def publish_json(ch, queue: str, message: Dict[str, Any], correlation_id: str, headers: Dict[str, Any] | None = None) -> None:
    ch.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message).encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2,
            correlation_id=correlation_id,
            content_type="application/json",
            headers=headers or {},
        ),
    )

def choose_retry_queue(retry_prefix: str, retry_count: int) -> Tuple[str, int]:
    idx = min(retry_count, len(RETRY_BACKOFFS_SECONDS) - 1)
    secs = RETRY_BACKOFFS_SECONDS[idx]
    return f"{retry_prefix}.{secs}s", secs
