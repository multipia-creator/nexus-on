from __future__ import annotations

import asyncio, json, time
from typing import AsyncIterator, Optional, Dict, Any, Tuple

from .store import event_store, Event

class Broadcaster:
    def __init__(self) -> None:
        self._q: "asyncio.Queue[Tuple[str,str,Event]]" = asyncio.Queue()

    async def publish(self, tenant: str, session_id: str, ev: Event) -> None:
        await self._q.put((tenant, session_id, ev))

    async def stream(self, tenant: str, session_id: str, last_event_id: int) -> AsyncIterator[str]:
        # replay missed events
        for e in event_store.replay_after(tenant, session_id, after_id=last_event_id, limit=200):
            yield self._event(e.event, e.event_id, e.data)

        # live + ping
        ping_every = 15.0
        last_ping = time.time()
        while True:
            timeout = max(0.2, ping_every - (time.time() - last_ping))
            try:
                t, s, e = await asyncio.wait_for(self._q.get(), timeout=timeout)
                if t == tenant and s == session_id:
                    yield self._event(e.event, e.event_id, e.data)
            except asyncio.TimeoutError:
                last_ping = time.time()
                yield self._event("ping", 0, {"ts": int(last_ping * 1000)})

    def _event(self, event: str, eid: int, data: Dict[str, Any]) -> str:
        return f"id: {eid}\nevent: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

broadcaster = Broadcaster()
