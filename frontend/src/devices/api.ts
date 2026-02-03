export type PairingConfirmByCodeResp = { device_id: string }

export type DeviceInfo = {
  device_id: string
  device_name: string
  device_type: string
  status: 'online' | 'offline' | string
  last_seen_epoch: number
  capabilities: string[]
}

export function apiBase(): string {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const v: any = (import.meta as any).env
  return (v?.VITE_API_BASE as string) ?? ''
}

export async function pairingConfirmByCode(pairingCode: string) : Promise<PairingConfirmByCodeResp> {
  const res = await fetch(`${apiBase()}/devices/pairing/confirm_by_code`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ pairing_code: pairingCode })
  })
  if (!res.ok) throw new Error(`pairingConfirm failed: ${res.status}`)
  return await res.json()
}

export async function listDevices(orgId: string, projectId: string) : Promise<DeviceInfo[]> {
  const res = await fetch(`${apiBase()}/devtools/devices`, {
    headers: { 'x-org-id': orgId, 'x-project-id': projectId }
  })
  if (!res.ok) throw new Error(`listDevices failed: ${res.status}`)
  const j = await res.json()
  return (j.devices ?? []) as DeviceInfo[]
}
