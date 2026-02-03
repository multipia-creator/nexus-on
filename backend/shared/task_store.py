import json
from typing import Any, Dict, Optional
import redis

class TaskStore:
    def __init__(self, redis_url: str, ttl_seconds: int):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl_seconds

    def ping(self) -> bool:
        return bool(self.r.ping())

    def put(self, task_id: str, task: Dict[str, Any]) -> None:
        key = f"task:{task_id}"
        self.r.set(key, json.dumps(task, ensure_ascii=False))
        self.r.expire(key, self.ttl)

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        key = f"task:{task_id}"
        raw = self.r.get(key)
        if not raw:
            return None
        return json.loads(raw)

    def update(self, task_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task = self.get(task_id)
        if not task:
            return None
        task.update(patch)
        self.put(task_id, task)
        return task
