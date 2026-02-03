type Props = { status: string }

export function DeviceBadge(p: Props) {
  const s = (p.status || '').toLowerCase()
  const cls = s === 'online' ? 'badge ok' : s === 'offline' ? 'badge bad' : 'badge'
  return <span className={cls}>{s || 'unknown'}</span>
}
