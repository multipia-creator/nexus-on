import type { AgentReport } from '../../types'

type Props = { report: AgentReport | null }

export function Sidecar(p: Props) {
  const cards = p.report?.ui_hint?.cards ?? []
  const actions = (p.report?.ui_hint?.actions ?? []).slice(0, 3)

  return (
    <div className="sidecar">
      <div className="sideHead">Sidecar</div>
      <div className="stack">
        {cards.length ? cards.map((c, idx) => (
          <div key={idx} className={`card type-${c.type}`}>
            <div className="cardTitle">{c.title} <span className="small">({c.type})</span></div>
            <div className="cardBody pre">{c.body}</div>
          </div>
        )) : <div className="empty">No ui_hint.</div>}
      </div>

      {actions.length ? (
        <div className="actions">
          {actions.map(a => (
            <button key={a.id} className={a.style === 'primary' ? 'btn primary' : 'btn'}>{a.label}</button>
          ))}
        </div>
      ) : null}

      <div className="sideMeta">
        <span className="pill">approval={p.report?.meta?.approval_level ?? '-'}</span>
        <span className="pill">corr={p.report?.meta?.causality?.correlation_id ?? '-'}</span>
      </div>
    </div>
  )
}
