import { mockDevices, mockPairingResponse } from '../lib/mockData'

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

export function isDemoMode(): boolean {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const v: any = (import.meta as any).env
  const mode = v?.VITE_DEMO_MODE as string | undefined
  return mode === 'true' || mode === '1'
}

export async function pairingConfirmByCode(pairingCode: string): Promise<PairingConfirmByCodeResp> {
  // 🎭 데모 모드
  if (isDemoMode()) {
    console.log('[Demo Mode] Pairing confirmed:', pairingCode)
    await new Promise(resolve => setTimeout(resolve, 500)) // 네트워크 지연 시뮬레이션
    return mockPairingResponse
  }

  // 🔌 실제 백엔드
  const res = await fetch(`${apiBase()}/devices/pairing/confirm_by_code`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ pairing_code: pairingCode })
  })
  if (!res.ok) throw new Error(`pairingConfirm failed: ${res.status}`)
  return await res.json()
}

export async function listDevices(orgId: string, projectId: string): Promise<DeviceInfo[]> {
  // 🎭 데모 모드
  if (isDemoMode()) {
    console.log('[Demo Mode] Listing devices:', { orgId, projectId })
    await new Promise(resolve => setTimeout(resolve, 300)) // 네트워크 지연 시뮬레이션
    return mockDevices.map(d => ({
      device_id: d.device_id,
      device_name: d.device_name,
      device_type: d.device_type,
      status: d.status,
      last_seen_epoch: new Date(d.last_seen).getTime(),
      capabilities: d.capabilities
    }))
  }

  // 🔌 실제 백엔드
  const res = await fetch(`${apiBase()}/devtools/devices`, {
    headers: { 'x-org-id': orgId, 'x-project-id': projectId }
  })
  if (!res.ok) throw new Error(`listDevices failed: ${res.status}`)
  const j = await res.json()
  return (j.devices ?? []) as DeviceInfo[]
}
