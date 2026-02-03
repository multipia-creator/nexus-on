from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

ApprovalLevel = Literal["green", "yellow", "red"]

class Causality(BaseModel):
    correlation_id: str = ""
    command_id: Optional[str] = None
    ask_id: Optional[str] = None
    type: str = "unknown"

class ReportMeta(BaseModel):
    mode: str = "focused"
    approval_level: ApprovalLevel = "green"
    confidence: float = 0.7
    report_id: str
    created_at: str
    event_id: int = 0
    tenant: str = "o:p"
    session_id: str = "s1"
    user_id: str = "u"
    json_repaired: bool = False
    causality: Causality = Field(default_factory=Causality)

class DoneItem(BaseModel):
    title: str
    detail: str

class NextItem(BaseModel):
    title: str
    detail: str
    owner: Optional[str] = None
    eta: Optional[str] = None

class BlockedItem(BaseModel):
    title: str
    why: str
    needs: str

class AskItem(BaseModel):
    question: str
    type: Literal["confirm", "choice", "input"] = "confirm"
    severity: ApprovalLevel = "yellow"
    options: Optional[List[str]] = None
    default: Optional[str] = None

class RiskItem(BaseModel):
    level: Literal["low", "medium", "high"] = "low"
    item: str
    mitigation: str

class UndoItem(BaseModel):
    title: str
    how: str

class UIHintCard(BaseModel):
    type: str
    title: str
    body: str

class UIHintAction(BaseModel):
    id: str
    label: str
    style: Literal["primary", "secondary"] = "secondary"

class UIHint(BaseModel):
    surface: Literal["chat", "dashboard", "sidecar"] = "dashboard"
    cards: List[UIHintCard] = Field(default_factory=list)
    actions: List[UIHintAction] = Field(default_factory=list)

class AgentReport(BaseModel):
    meta: ReportMeta
    done: List[DoneItem] = Field(default_factory=list)
    next: List[NextItem] = Field(default_factory=list)
    blocked: List[BlockedItem] = Field(default_factory=list)
    ask: List[AskItem] = Field(default_factory=list)
    risk: List[RiskItem] = Field(default_factory=list)
    rationale: str = ""
    undo: List[UndoItem] = Field(default_factory=list)
    ui_hint: UIHint = Field(default_factory=UIHint)
    persona_id: str = "seria.istj"
    skin_id: str = "seria.default"

# -------- Device API --------

class PairingStartReq(BaseModel):
    device_type: str = "windows_companion"
    device_name: str
    capabilities: List[str] = Field(default_factory=list)

class PairingStartResp(BaseModel):
    pairing_id: str
    pairing_code: str
    device_nonce: str
    expires_at: str

class PairingConfirmByCodeReq(BaseModel):
    pairing_code: str

class PairingConfirmByCodeResp(BaseModel):
    device_id: str

class PairingCompleteReq(BaseModel):
    pairing_id: str
    device_nonce: str

class PairingCompleteResp(BaseModel):
    device_id: str
    device_token: str

class HeartbeatReq(BaseModel):
    status: Literal["online", "offline"] = "online"
    metrics: Dict[str, Any] = Field(default_factory=dict)
    agent_version: str = "unknown"

class ClientContext(BaseModel):
    surface: str = "windows_agent"
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None

class DevicePolicy(BaseModel):
    risk: Literal["GREEN","YELLOW","RED"] = "YELLOW"
    approval_id: Optional[str] = None

class DeviceCommand(BaseModel):
    command_id: str
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    client_context: ClientContext
    policy: Optional[DevicePolicy] = None
    created_at: str

class CommandsResp(BaseModel):
    commands: List[DeviceCommand] = Field(default_factory=list)
    next_cursor: Optional[str] = None

class AckReq(BaseModel):
    received_at: str

class ReportsPushReq(BaseModel):
    reports: List[AgentReport]

class EmitReportReq(BaseModel):
    session_id: str = "s1"
    approval_level: ApprovalLevel = "green"
    text: str = "hello"
