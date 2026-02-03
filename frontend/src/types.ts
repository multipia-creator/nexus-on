export type ApprovalLevel = 'green' | 'yellow' | 'red'

export type AgentReport = {
  meta: {
    mode: string
    approval_level: ApprovalLevel
    confidence: number
    report_id: string
    created_at: string
    event_id: number
    tenant: string
    session_id: string
    user_id: string
    json_repaired: boolean
    causality: {
      correlation_id: string
      command_id: string | null
      ask_id: string | null
      type: string
    }
  }
  done: Array<{ title: string; detail: string }>
  next: Array<{ title: string; detail: string; owner?: string; eta?: string }>
  blocked: Array<{ title: string; why: string; needs: string }>
  ask: Array<{
    question: string
    type: 'confirm' | 'choice' | 'input'
    severity: ApprovalLevel
    options: string[] | null
    default: string | null
  }>
  risk: Array<{ level: 'low' | 'medium' | 'high'; item: string; mitigation: string }>
  rationale: string
  undo: Array<{ title: string; how: string }>
  ui_hint: {
    surface: 'chat' | 'dashboard' | 'sidecar'
    cards: Array<{ type: string; title: string; body: string }>
    actions: Array<{ id: string; label: string; style: 'primary' | 'secondary' }>
  }
  persona_id: string
  skin_id: string
}

export type StreamEvent =
  | { event: 'snapshot' | 'report'; id: number; data: AgentReport }
  | { event: 'ping'; id?: undefined; data: { ts: number } }
