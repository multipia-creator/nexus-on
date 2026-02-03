import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import redis


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class AgentEvent:
    seq: int
    event_type: str
    payload: Dict[str, Any]


class StreamStore:
    """Tenant-scoped event log + minimal UI state (asks/worklog/autopilot) in Redis.

    Keys:
      - nexus:stream:{tenant}:seq -> integer
      - nexus:stream:{tenant}:z -> zset(score=seq, value=json)
      - nexus:stream:{tenant}:asks -> hash(ask_id -> json)
      - nexus:stream:{tenant}:worklog -> list(json)
      - nexus:stream:{tenant}:autopilot -> string(json)
    """

    def __init__(self, redis_url: str, event_keep: int = 2000, worklog_keep: int = 200):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)
        self.event_keep = int(event_keep)
        self.worklog_keep = int(worklog_keep)

    @staticmethod
    def tenant_id(org_id: str, project_id: str) -> str:
        return f"{org_id}::{project_id}"

    def _k(self, tenant: str, suffix: str) -> str:
        return f"nexus:stream:{tenant}:{suffix}"

    def alloc_seq(self, tenant: str) -> int:
        return int(self.r.incr(self._k(tenant, "seq")))

    def append_event(self, tenant: str, event_type: str, payload: Dict[str, Any]) -> AgentEvent:
        seq = self.alloc_seq(tenant)
        envelope = {
            "seq": seq,
            "event_type": event_type,
            "payload": payload,
            "created_at": _utc_iso(),
        }
        zkey = self._k(tenant, "z")
        self.r.zadd(zkey, {json.dumps(envelope, ensure_ascii=False): seq})
        # keep last N
        if self.event_keep > 0:
            self.r.zremrangebyrank(zkey, 0, -(self.event_keep + 1))
        return AgentEvent(seq=seq, event_type=event_type, payload=payload)

    def replay(self, tenant: str, after_seq: int, limit: int = 1000) -> List[AgentEvent]:
        zkey = self._k(tenant, "z")
        raw = self.r.zrangebyscore(zkey, min=after_seq + 1, max="+inf", start=0, num=int(limit))
        out: List[AgentEvent] = []
        for s in raw:
            try:
                env = json.loads(s)
                out.append(AgentEvent(seq=int(env["seq"]), event_type=env["event_type"], payload=env["payload"]))
            except Exception:
                continue
        return out

    def current_seq(self, tenant: str) -> int:
        v = self.r.get(self._k(tenant, "seq"))
        return int(v) if v else 0

    # ---- UI state ----
    def get_autopilot(self, tenant: str) -> Dict[str, Any]:
        k = self._k(tenant, "autopilot")
        raw = self.r.get(k)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass
        default = {"state": "idle", "blocked_by_red": False, "updated_at": _utc_iso()}
        self.set_autopilot(tenant, default)
        return default

    def set_autopilot(self, tenant: str, state: Dict[str, Any]) -> None:
        state = {**state, "updated_at": _utc_iso()}
        self.r.set(self._k(tenant, "autopilot"), json.dumps(state, ensure_ascii=False))

    def add_worklog(self, tenant: str, entry: Dict[str, Any]) -> None:
        entry = {**entry, "ts": entry.get("ts") or _utc_iso()}
        k = self._k(tenant, "worklog")
        self.r.rpush(k, json.dumps(entry, ensure_ascii=False))
        if self.worklog_keep > 0:
            self.r.ltrim(k, -self.worklog_keep, -1)

    def list_worklog(self, tenant: str, limit: int = 200) -> List[Dict[str, Any]]:
        k = self._k(tenant, "worklog")
        raw = self.r.lrange(k, max(-int(limit), -10000), -1)
        out: List[Dict[str, Any]] = []
        for s in raw:
            try:
                out.append(json.loads(s))
            except Exception:
                continue
        return out

    def add_ask(self, tenant: str, ask: Dict[str, Any]) -> None:
        ask = {**ask, "created_at": ask.get("created_at") or _utc_iso()}
        self.r.hset(self._k(tenant, "asks"), ask["ask_id"], json.dumps(ask, ensure_ascii=False))

    def list_asks(self, tenant: str) -> List[Dict[str, Any]]:
        raw = self.r.hgetall(self._k(tenant, "asks"))
        out: List[Dict[str, Any]] = []
        for _, s in raw.items():
            try:
                out.append(json.loads(s))
            except Exception:
                continue
        out.sort(key=lambda a: (a.get("created_at") or ""))
        return out

    def remove_ask(self, tenant: str, ask_id: str) -> bool:
        return bool(self.r.hdel(self._k(tenant, "asks"), ask_id))

    def snapshot(self, tenant: str) -> Dict[str, Any]:
        return {
            "report_id": f"snapshot-{int(time.time()*1000)}",
            "ts": _utc_iso(),
            "asks": self.list_asks(tenant),
            "worklog": self.list_worklog(tenant),
            "autopilot": self.get_autopilot(tenant),
        }
