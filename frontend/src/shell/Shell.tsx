import { useMemo, useState } from 'react'
import { useAgentReportStream } from '../stream/useAgentReportStream'
import { Dock } from './components/Dock'
import { TopNav } from './components/TopNav'
import { AssistantStage } from './components/AssistantStage'
import { Dashboard } from './components/Dashboard'
import { Sidecar } from './components/Sidecar'
import type { AgentReport } from '../types'
import { corr } from '../lib/correlation'
import { postJSON } from '../lib/http'
import { DevicesModal } from '../devices/DevicesModal'
import { isDemoMode } from '../devices/api'
import { createMockChatMessage } from '../lib/mockData'
import { YouTubePanel } from '../youtube/YouTubePanel'
import { NodesManager } from '../nodes/NodesManager'

type View = 'stage' | 'dashboard' | 'youtube' | 'nodes'

export function Shell() {
  const [orgId, setOrgId] = useState('o')
  const [projectId, setProjectId] = useState('p')
  const [sessionId, setSessionId] = useState('s1')
  const [view, setView] = useState<View>('stage')
  const [devicesOpen, setDevicesOpen] = useState(false)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const baseUrl = ((import.meta as any).env?.VITE_API_BASE as string) ?? ''
  const demoMode = isDemoMode()

  const { reports, latest, lastEventId, connected, lastPingTs } = useAgentReportStream({
    orgId,
    projectId,
    sessionId,
    baseUrl,
    demoMode
  })

  const counts = useMemo(() => {
    const asks = latest?.ask?.length ?? 0
    const redAsks = (latest?.ask ?? []).filter(a => a.severity === 'red').length
    const blocked = latest?.blocked?.length ?? 0
    return { asks, redAsks, blocked }
  }, [latest])

  const headers = useMemo(() => ({ 'x-org-id': orgId, 'x-project-id': projectId }), [orgId, projectId])

  async function sendChatMessage(text: string) {
    if (demoMode) {
      console.log('[Demo Mode] Mock chat message:', text)
      
      // Demo 모드: Mock user + assistant 메시지 추가
      const userMsg = createMockChatMessage(sessionId, Date.now(), 'user', text)
      // @ts-ignore (reports is read-only, but we're mocking)
      reports.push(userMsg)
      
      setTimeout(() => {
        const assistantMsg = createMockChatMessage(
          sessionId,
          Date.now() + 1,
          'assistant',
          `[데모 모드 응답] "${text}"에 대한 답변입니다. 실제 LLM 연동은 백엔드 실행 시 작동합니다.`
        )
        // @ts-ignore
        reports.push(assistantMsg)
      }, 500)
      
      return
    }
    
    // POST /chat API 호출
    await postJSON(
      `${baseUrl}/chat`,
      {
        session_id: sessionId,
        text
      },
      { ...headers, 'x-api-key': 'dev-api-key-change-in-production' }
    )
  }

  async function emitSidecarRed() {
    if (demoMode) {
      console.log('[Demo Mode] Skipping /sidecar/command API call')
      return
    }
    await postJSON(
      `${baseUrl}/sidecar/command`,
      {
        command_id: 'cmd-ui-red',
        type: 'external_share.execute',
        client_context: { correlation_id: corr('corr-ui-sidecar'), session_id: sessionId }
      },
      { ...headers, 'x-api-key': 'dev-api-key-change-in-production' }
    )
  }

  async function approveYes() {
    if (demoMode) {
      console.log('[Demo Mode] Skipping /approvals API call')
      return
    }
    
    // v7.7 Backend: /approvals 엔드포인트 미구현
    // 임시로 /sidecar/command 사용
    console.warn('[Frontend] /approvals API not implemented in v7.7 Backend')
    console.log('[Frontend] Would approve ask with correlation_id:', corr('corr-ui-approve'))
    
    // TODO: v7.7 Backend에 /approvals/*/decide 엔드포인트 추가 필요
    // await postJSON(`${baseUrl}/approvals/ask-demo/decide`, { session_id: sessionId, correlation_id: corr('corr-ui-approve'), decision: 'yes' }, { ...headers, 'x-api-key': 'dev-api-key-change-in-production' })
  }

  return (
    <div className="app">
      <TopNav currentView={view} onViewChange={setView} />

      <main className="main">
        {view === 'stage' ? (
          <AssistantStage
            report={latest}
            counts={counts}
            onOpenDashboard={() => setView('dashboard')}
            onSendMessage={sendChatMessage}
          />
        ) : view === 'youtube' ? (
          <YouTubePanel
            baseUrl={baseUrl}
            orgId={orgId}
            projectId={projectId}
            sessionId={sessionId}
            apiKey="dev-api-key-change-in-production"
            demoMode={demoMode}
          />
        ) : view === 'nodes' ? (
          <NodesManager
            baseUrl={baseUrl}
            orgId={orgId}
            projectId={projectId}
            apiKey="dev-api-key-change-in-production"
            onError={(err) => console.error('[Nodes Error]', err)}
          />
        ) : (
          <div className="dashWrap">
            <Dashboard report={latest} />
            <Sidecar report={latest} />
          </div>
        )}
      </main>

<DevicesModal
  open={devicesOpen}
  onClose={() => setDevicesOpen(false)}
  orgId={orgId}
  projectId={projectId}
/>

<Dock
        view={view}
        counts={counts}
        personaId={latest?.persona_id ?? '-'}
        skinId={latest?.skin_id ?? '-'}
        approval={latest?.meta?.approval_level ?? '-'}
        onToggle={() => setView(v => (v === 'stage' ? 'dashboard' : 'stage'))}
      />

      <section className="debug">
        <div className="debugHead">Reports (deduped by report_id)</div>
        <div className="debugList">
          {reports.map((r: AgentReport) => (
            <div key={r.meta.report_id} className="debugItem">
              <div className="debugMeta">
                <b>{r.meta.report_id}</b>
                <span>event_id={r.meta.event_id}</span>
                <span>{r.meta.approval_level}</span>
                <span>{r.meta.causality?.correlation_id}</span>
              </div>
              <pre className="debugJson">{JSON.stringify(r, null, 2)}</pre>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
