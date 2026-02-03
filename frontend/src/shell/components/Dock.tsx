type Props = {
  view: 'stage' | 'dashboard' | 'youtube' | 'nodes'
  counts: { asks: number; redAsks: number; blocked: number }
  personaId: string
  skinId: string
  approval: string
  onToggle: () => void
}

export function Dock(p: Props) {
  const viewLabel = p.view === 'stage' ? 'stage' : p.view === 'youtube' ? 'youtube' : p.view === 'nodes' ? 'nodes' : 'dashboard'
  
  return (
    <div className="dock" onClick={p.onToggle} role="button" aria-label="dock">
      <div className="dockAvatar">S</div>
      <div className="dockBody">
        <div className="dockLine1">
          <span className="dockName">Seria</span>
          <span className="dockMode">{viewLabel}</span>
          <span className={`badge ${p.counts.redAsks ? 'red' : ''}`}>RED {p.counts.redAsks}</span>
          <span className={`badge ${p.counts.asks ? 'yellow' : ''}`}>ASK {p.counts.asks}</span>
          <span className={`badge ${p.counts.blocked ? 'red' : ''}`}>BLK {p.counts.blocked}</span>
        </div>
        <div className="dockLine2">
          <span className="pill">approval={p.approval}</span>
          <span className="pill">persona={p.personaId}</span>
          <span className="pill">skin={p.skinId}</span>
        </div>
      </div>
      <div className="dockHint">click</div>
    </div>
  )
}
