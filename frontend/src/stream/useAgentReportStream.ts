import { useEffect, useMemo, useRef, useState } from 'react'
import type { AgentReport, StreamEvent } from '../types'
import { createMockSSEStream } from '../lib/mockData'

type Params = {
  sessionId: string
  orgId: string
  projectId: string
  baseUrl?: string
  demoMode?: boolean
}

export function useAgentReportStream(p: Params) {
  const baseUrl = p.baseUrl ?? ''
  const key = useMemo(
    () => `nexus:last_event_id:${p.orgId}:${p.projectId}:${p.sessionId}`,
    [p.orgId, p.projectId, p.sessionId]
  )

  const [reports, setReports] = useState<AgentReport[]>([])
  const [lastEventId, setLastEventId] = useState<number>(() => {
    const raw = localStorage.getItem(key)
    return raw ? Number(raw) : 0
  })
  const [connected, setConnected] = useState(false)
  const [lastPingTs, setLastPingTs] = useState<number | null>(null)

  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    const abort = new AbortController()
    abortRef.current = abort

    // 🎭 데모 모드: Mock SSE 스트림
    if (p.demoMode) {
      async function runDemo() {
        setConnected(true)

        const pushEvent = (ev: StreamEvent) => {
          if (ev.event === 'ping') {
            setLastPingTs(ev.data.ts)
            return
          }
          setReports(prev => {
            const map = new Map(prev.map(r => [r.meta.report_id, r]))
            map.set(ev.data.meta.report_id, ev.data)
            return Array.from(map.values()).sort((a, b) => a.meta.event_id - b.meta.event_id)
          })
          setLastEventId(ev.id)
          localStorage.setItem(key, String(ev.id))
        }

        const parseBlock = (block: string): StreamEvent | null => {
          const lines = block.split('\n').map(l => l.trimEnd()).filter(Boolean)
          let id: number | null = null
          let event: string | null = null
          let data: string | null = null
          for (const ln of lines) {
            if (ln.startsWith('id:')) id = Number(ln.slice(3).trim())
            if (ln.startsWith('event:')) event = ln.slice(6).trim()
            if (ln.startsWith('data:')) data = ln.slice(5).trim()
          }
          if (!event || !data) return null
          const obj = JSON.parse(data)
          if (event === 'ping') return { event: 'ping', data: obj }
          if (id == null) return null
          return { event: event as any, id, data: obj }
        }

        // Mock SSE 스트림 생성기
        const stream = createMockSSEStream(p.sessionId)

        for (const chunk of stream) {
          if (abort.signal.aborted) break

          // SSE 형식 파싱
          const blocks = chunk.split('\n\n').filter(Boolean)
          for (const block of blocks) {
            const ev = parseBlock(block)
            if (ev) pushEvent(ev)
          }

          // 각 이벤트 사이에 1초 지연 (실제 스트리밍 시뮬레이션)
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      }

      runDemo().catch(err => {
        console.error('[Demo Mode] SSE stream error:', err)
        setConnected(false)
      })

      return () => abort.abort()
    }

    // 🔌 실제 백엔드 모드
    async function run() {
      setConnected(false)

      // v7.7 Backend: query string으로 인증 정보 전달 (EventSource는 헤더 설정 불가)
      const params = new URLSearchParams({
        session_id: p.sessionId,
        org_id: p.orgId,
        project_id: p.projectId,
        // API 키는 환경 변수에서 가져오거나 하드코딩 (개발용)
        api_key: 'dev-api-key-change-in-production'
      })
      
      // cursor 파라미터로 재연결 지원
      if (lastEventId > 0) {
        params.set('cursor', String(lastEventId))
      }

      const url = `${baseUrl}/agent/reports/stream?${params.toString()}`
      const res = await fetch(url, { signal: abort.signal })
      if (!res.ok || !res.body) throw new Error(`SSE failed: ${res.status}`)

      setConnected(true)

      const reader = res.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buf = ''

      const pushEvent = (ev: StreamEvent) => {
        if (ev.event === 'ping') {
          setLastPingTs(ev.data.ts)
          return
        }
        setReports(prev => {
          const map = new Map(prev.map(r => [r.meta.report_id, r]))
          map.set(ev.data.meta.report_id, ev.data)
          return Array.from(map.values()).sort((a, b) => a.meta.event_id - b.meta.event_id)
        })
        setLastEventId(ev.id)
        localStorage.setItem(key, String(ev.id))
      }

      const parseBlock = (block: string): StreamEvent | null => {
        const lines = block.split('\n').map(l => l.trimEnd()).filter(Boolean)
        let id: number | null = null
        let event: string | null = null
        let data: string | null = null
        for (const ln of lines) {
          if (ln.startsWith('id:')) id = Number(ln.slice(3).trim())
          if (ln.startsWith('event:')) event = ln.slice(6).trim()
          if (ln.startsWith('data:')) data = ln.slice(5).trim()
        }
        if (!event || !data) return null
        const obj = JSON.parse(data)
        if (event === 'ping') return { event: 'ping', data: obj }
        if (id == null) return null
        return { event: event as any, id, data: obj }
      }

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })
        let idx: number
        while ((idx = buf.indexOf('\n\n')) >= 0) {
          const block = buf.slice(0, idx)
          buf = buf.slice(idx + 2)
          if (!block.includes('event:')) continue
          const ev = parseBlock(block)
          if (ev) pushEvent(ev)
        }
      }
    }

    run().catch(err => {
      console.error('[Real Backend] SSE stream error:', err)
      setConnected(false)
    })

    return () => abort.abort()
  }, [p.orgId, p.projectId, p.sessionId, p.demoMode, baseUrl, key, lastEventId])

  const latest = useMemo(() => (reports.length ? reports[reports.length - 1] : null), [reports])

  return { reports, latest, lastEventId, connected, lastPingTs }
}
