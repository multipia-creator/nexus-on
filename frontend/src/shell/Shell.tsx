import { useMemo, useState } from 'react'
import { useAgentReportStream } from '../stream/useAgentReportStream'
import { Dock } from './components/Dock'
import { AssistantStage } from './components/AssistantStage'
import { Dashboard } from './components/Dashboard'
import { Sidecar } from './components/Sidecar'
import type { AgentReport } from '../types'
import { corr } from '../lib/correlation'
import { postJSON } from '../lib/http'
import { DevicesModal } from '../devices/DevicesModal'
import { isDemoMode } from '../devices/api'

type View = 'stage' | 'dashboard'

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

  async function emitChat() {
    if (demoMode) {
      console.log('[Demo Mode] Skipping /chat API call')
      return
    }
    await postJSON('/chat', { session_id: sessionId, correlation_id: corr('corr-ui-chat'), text: 'ui probe' }, headers)
  }

  async function emitSidecarRed() {
    if (demoMode) {
      console.log('[Demo Mode] Skipping /sidecar/command API call')
      return
    }
    await postJSON(
      '/sidecar/command',
      {
        command_id: 'cmd-ui-red',
        type: 'external_share.execute',
        client_context: { correlation_id: corr('corr-ui-sidecar'), session_id: sessionId }
      },
      headers
    )
  }

  async function approveYes() {
    if (demoMode) {
      console.log('[Demo Mode] Skipping /approvals API call')
      return
    }
    await postJSON(`/approvals/ask-demo/decide`, { session_id: sessionId, correlation_id: corr('corr-ui-approve'), decision: 'yes' }, headers)
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="logo">N</div>
          <div className="brandText">
            <div className="brandTitle">NEXUS UI Skeleton {demoMode && '🎭 DEMO'}</div>
            <div className="brandSub">stream-first UI contract harness</div>
          </div>
        </div>

        <div className="status">
          <span className={connected ? 'pill ok' : 'pill bad'}>{connected ? 'connected' : 'disconnected'}</span>
          {demoMode && <span className="pill" style={{ backgroundColor: '#ff9800' }}>DEMO MODE</span>}
          <span className="pill">last_event_id={lastEventId}</span>
          <span className="pill">last_ping={lastPingTs ?? '-'}</span>
        </div>

        <div className="controls">
          <label>org <input value={orgId} onChange={e => setOrgId(e.target.value)} /></label>
          <label>project <input value={projectId} onChange={e => setProjectId(e.target.value)} /></label>
          <label>session <input value={sessionId} onChange={e => setSessionId(e.target.value)} /></label>
          <button onClick={() => { localStorage.clear(); window.location.reload() }}>Clear cursor</button>
          <button onClick={emitChat}>Emit /chat</button>
          <button onClick={emitSidecarRed}>Emit RED</button>
          <button onClick={approveYes}>Approvals yes</button>
          <button onClick={() => setDevicesOpen(true)}>Devices</button>
        </div>
      </header>

      <main className="main">
        {view === 'stage' ? (
          <AssistantStage
            report={latest}
            counts={counts}
            onOpenDashboard={() => setView('dashboard')}
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
