from __future__ import annotations

import time, secrets
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

# ---------------- Events (tenant+session scoped) ----------------

@dataclass
class Event:
    event_id: int
    event: str   # snapshot|report
    data: Dict[str, Any]

class InMemoryEventStore:
    """tenant+session event store; event_id is monotonic per tenant."""
    def __init__(self) -> None:
        self._lock = Lock()
        self._events: Dict[Tuple[str, str], List[Event]] = {}
        self._seq: Dict[str, int] = {}

    def _next_id(self, tenant: str) -> int:
        self._seq[tenant] = self._seq.get(tenant, 0) + 1
        return self._seq[tenant]

    def ensure_snapshot(self, tenant: str, session_id: str, report_obj: Dict[str, Any]) -> Event:
        key = (tenant, session_id)
        with self._lock:
            if key in self._events and any(e.event == "snapshot" for e in self._events[key]):
                snaps = [e for e in self._events[key] if e.event == "snapshot"]
                return snaps[-1]
            if key not in self._events:
                self._events[key] = []
            eid = self._next_id(tenant)
            report_obj.setdefault("meta", {})["event_id"] = eid
            self._events[key].append(Event(event_id=eid, event="snapshot", data=report_obj))
            return self._events[key][-1]

    def append(self, tenant: str, session_id: str, event: str, report_obj: Dict[str, Any]) -> Event:
        key = (tenant, session_id)
        with self._lock:
            if key not in self._events:
                self._events[key] = []
            eid = self._next_id(tenant)
            report_obj.setdefault("meta", {})["event_id"] = eid
            self._events[key].append(Event(event_id=eid, event=event, data=report_obj))
            return self._events[key][-1]

    def replay_after(self, tenant: str, session_id: str, after_id: int, limit: int = 200) -> List[Event]:
        key = (tenant, session_id)
        with self._lock:
            items = [e for e in self._events.get(key, []) if e.event_id > after_id]
            return items[:limit]

# ---------------- Devices ----------------

@dataclass
class PairingRecord:
    pairing_id: str
    code: str
    device_nonce: str
    expires_at_epoch: float
    tenant: str
    device_name: str
    device_type: str
    capabilities: List[str] = field(default_factory=list)
    confirmed: bool = False
    device_id: Optional[str] = None
    device_token: Optional[str] = None
    credentials_claimed: bool = False

@dataclass
class DeviceRecord:
    device_id: str
    device_token: str
    tenant: str
    device_name: str
    device_type: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "offline"
    last_seen_epoch: float = 0.0

@dataclass
class CommandRecord:
    seq: int
    command_id: str
    payload: Dict[str, Any]
    ack_at: Optional[str] = None

class InMemoryDeviceStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._pairings: Dict[str, PairingRecord] = {}
        self._pairings_by_code: Dict[str, str] = {}
        self._devices: Dict[str, DeviceRecord] = {}
        self._commands_by_device: Dict[str, List[CommandRecord]] = {}
        self._seq_cmd = 0

    def _new_id(self, prefix: str) -> str:
        return f"{prefix}_{secrets.token_hex(8)}"

    def start_pairing(self, tenant: str, device_type: str, device_name: str, capabilities: List[str], ttl_sec: int = 300) -> Tuple[str, str, str, float]:
        with self._lock:
            pairing_id = self._new_id("pair")
            device_nonce = self._new_id("nonce")
            for _ in range(10):
                code = f"{secrets.randbelow(1000):03d}-{secrets.randbelow(1000):03d}"
                if code not in self._pairings_by_code:
                    break
            else:
                code = f"{secrets.token_hex(3)}"
            expires = time.time() + ttl_sec
            rec = PairingRecord(pairing_id, code, device_nonce, expires, tenant, device_name, device_type, capabilities)
            self._pairings[pairing_id] = rec
            self._pairings_by_code[code] = pairing_id
            return pairing_id, code, device_nonce, expires

    def confirm_by_code(self, code: str) -> Optional[PairingRecord]:
        with self._lock:
            pairing_id = self._pairings_by_code.get(code)
            if not pairing_id:
                return None
            rec = self._pairings.get(pairing_id)
            if not rec:
                return None
            if time.time() > rec.expires_at_epoch:
                return None
            if rec.confirmed:
                return rec
            # create device credentials now, but do NOT return token to web
            device_id = self._new_id("dev")
            token = self._new_id("dtok")
            rec.confirmed = True
            rec.device_id = device_id
            rec.device_token = token
            # create device record so device can auth immediately after complete
            dev = DeviceRecord(device_id, token, rec.tenant, rec.device_name, rec.device_type, rec.capabilities, status="online", last_seen_epoch=time.time())
            self._devices[device_id] = dev
            self._commands_by_device.setdefault(device_id, [])
            return rec

    def complete(self, pairing_id: str, device_nonce: str) -> Optional[DeviceRecord]:
        with self._lock:
            rec = self._pairings.get(pairing_id)
            if not rec:
                return None
            if time.time() > rec.expires_at_epoch:
                return None
            if rec.device_nonce != device_nonce:
                return None
            if not rec.confirmed or not rec.device_id or not rec.device_token:
                # web hasn't confirmed yet
                return None
            if rec.credentials_claimed:
                # already claimed
                dev = self._devices.get(rec.device_id)
                return dev
            rec.credentials_claimed = True
            # We can optionally delete pairing record after claim to reduce leakage window
            # but we keep it for ttl to simplify POC.
            return self._devices.get(rec.device_id)

    def get_device_by_token(self, device_id: str, token: str) -> Optional[DeviceRecord]:
        with self._lock:
            dev = self._devices.get(device_id)
            if not dev or dev.device_token != token:
                return None
            return dev

    def heartbeat(self, device_id: str, status: str):
        with self._lock:
            dev = self._devices.get(device_id)
            if dev:
                dev.status = status
                dev.last_seen_epoch = time.time()

    def enqueue_command(self, device_id: str, cmd_payload: Dict[str, Any]) -> CommandRecord:
        with self._lock:
            self._seq_cmd += 1
            command_id = cmd_payload.get("command_id") or self._new_id("cmd")
            cmd_payload["command_id"] = command_id
            rec = CommandRecord(seq=self._seq_cmd, command_id=command_id, payload=cmd_payload)
            self._commands_by_device.setdefault(device_id, []).append(rec)
            return rec

    def list_commands_since(self, device_id: str, cursor: Optional[str], limit: int = 50) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        with self._lock:
            seq_cursor = int(cursor) if cursor else 0
            all_cmds = self._commands_by_device.get(device_id, [])
            out = [c for c in all_cmds if c.seq > seq_cursor]
            out = out[:limit]
            next_cursor = str(out[-1].seq) if out else cursor
            return [c.payload for c in out], next_cursor

    def ack_command(self, device_id: str, command_id: str, received_at: str) -> bool:
        with self._lock:
            cmds = self._commands_by_device.get(device_id, [])
            for c in cmds:
                if c.command_id == command_id:
                    c.ack_at = received_at
                    return True
            return False

    def list_devices(self, tenant: str) -> List[Dict[str, Any]]:
        with self._lock:
            out = []
            for dev in self._devices.values():
                if dev.tenant != tenant:
                    continue
                out.append({
                    "device_id": dev.device_id,
                    "device_name": dev.device_name,
                    "device_type": dev.device_type,
                    "status": dev.status,
                    "last_seen_epoch": dev.last_seen_epoch,
                    "capabilities": dev.capabilities,
                })
            out.sort(key=lambda x: x["last_seen_epoch"], reverse=True)
            return out

event_store = InMemoryEventStore()
device_store = InMemoryDeviceStore()
