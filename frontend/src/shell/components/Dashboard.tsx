import type { AgentReport } from '../../types'

type Props = { report: AgentReport | null }

export function Dashboard(p: Props) {
  return (
    <div className="dashboard">
      <div className="dashCol">
        <div className="dashHead">Asks</div>
        <Asks report={p.report} />
      </div>
      <div className="dashCol">
        <div className="dashHead">Worklog</div>
        <Worklog report={p.report} />
      </div>
      <div className="dashCol">
        <div className="dashHead">Autopilot</div>
        <Autopilot report={p.report} />
      </div>
    </div>
  )
}

function Asks({ report }: Props) {
  const asks = report?.ask ?? []
  if (!asks.length) return <div className="empty">No asks.</div>
  return (
    <div className="stack">
      {asks.map((a, idx) => (
        <div key={idx} className={`card sev-${a.severity}`}>
          <div className="cardTitle">[{a.severity}] {a.type}</div>
          <div className="cardBody">{a.question}</div>
          {a.options?.length ? <div className="chips">{a.options.map(o => <span key={o} className="chip">{o}</span>)}</div> : null}
          <div className="cardActions">
            {a.type === 'confirm' ? (
              <>
                <button className="btn primary">예</button>
                <button className="btn">아니오</button>
              </>
            ) : a.type === 'input' ? (
              <button className="btn primary">입력</button>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  )
}

function Worklog({ report }: Props) {
  const done = report?.done ?? []
  const blocked = report?.blocked ?? []
  if (!done.length && !blocked.length) return <div className="empty">No worklog.</div>
  return (
    <div className="stack">
      {done.map((d, idx) => (
        <div key={`d-${idx}`} className="card">
          <div className="cardTitle">DONE</div>
          <div className="cardBody"><b>{d.title}</b> — {d.detail}</div>
        </div>
      ))}
      {blocked.map((b, idx) => (
        <div key={`b-${idx}`} className="card blocked">
          <div className="cardTitle">BLOCKED</div>
          <div className="cardBody"><b>{b.title}</b><br/>why: {b.why}<br/>needs: {b.needs}</div>
        </div>
      ))}
    </div>
  )
}

function Autopilot({ report }: Props) {
  const next = report?.next ?? []
  if (!next.length) return <div className="empty">No next steps.</div>
  return (
    <div className="stack">
      {next.map((n, idx) => (
        <div key={idx} className="card">
          <div className="cardTitle">NEXT</div>
          <div className="cardBody"><b>{n.title}</b> — {n.detail}<br/><span className="small">owner={n.owner ?? '-'} eta={n.eta ?? '-'}</span></div>
        </div>
      ))}
    </div>
  )
}
