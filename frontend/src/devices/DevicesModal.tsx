import { useEffect, useMemo, useState } from 'react'
import { DeviceBadge } from './DeviceBadge'
import { listDevices, pairingConfirmByCode, type DeviceInfo } from './api'

type Props = {
  open: boolean
  onClose: () => void
  orgId: string
  projectId: string
}

export function DevicesModal(p: Props) {
  const [pairingCode, setPairingCode] = useState('')
  const [msg, setMsg] = useState<string>('')
  const [devices, setDevices] = useState<DeviceInfo[]>([])

  const normalizedCode = useMemo(() => pairingCode.trim().replace(/\s+/g, ''), [pairingCode])

  useEffect(() => {
    if (!p.open) return
    let alive = true
    async function tick() {
      try {
        const d = await listDevices(p.orgId, p.projectId)
        if (alive) setDevices(d)
      } catch (e: any) {
        if (alive) setMsg(e?.message ?? 'listDevices error')
      }
    }
    tick()
    const t = setInterval(tick, 2500)
    return () => {
      alive = false
      clearInterval(t)
    }
  }, [p.open, p.orgId, p.projectId])

  if (!p.open) return null

  async function onConfirm() {
    setMsg('')
    try {
      const r = await pairingConfirmByCode(normalizedCode)
      setMsg(`Confirmed. Device ID issued: ${r.device_id}. (Device will claim token itself.)`)
    } catch (e: any) {
      setMsg(e?.message ?? 'pairingConfirm failed')
    }
  }

  return (
    <div className="modalOverlay" role="dialog" aria-modal="true">
      <div className="modal">
        <div className="modalHead">
          <div className="modalTitle">Devices</div>
          <button className="btn" onClick={p.onClose}>Close</button>
        </div>

        <div className="modalBody">
          <div className="card">
            <div className="cardTitle">Pair Windows Companion</div>
            <div className="cardBody">
              <div className="row">
                <input
                  className="inputWide"
                  placeholder="Pairing code from Windows Companion (e.g., 123-456)"
                  value={pairingCode}
                  onChange={e => setPairingCode(e.target.value)}
                />
                <button className="btn primary" onClick={onConfirm} disabled={!normalizedCode}>Confirm</button>
              </div>
              {msg ? <div className="small">{msg}</div> : null}
            </div>
          </div>

          <div className="card">
            <div className="cardTitle">Paired devices</div>
            <div className="cardBody">
              {!devices.length ? <div className="empty">No devices.</div> : (
                <div className="table">
                  <div className="tr th">
                    <div>ID</div>
                    <div>Name</div>
                    <div>Status</div>
                    <div>Last Seen</div>
                  </div>
                  {devices.map(d => (
                    <div className="tr" key={d.device_id}>
                      <div className="mono">{d.device_id}</div>
                      <div>{d.device_name}</div>
                      <div><DeviceBadge status={d.status} /></div>
                      <div className="small mono">{Math.round((Date.now()/1000 - d.last_seen_epoch))}s ago</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="modalFoot small">
          Tenant: <span className="mono">{p.orgId}:{p.projectId}</span>
        </div>
      </div>
    </div>
  )
}
