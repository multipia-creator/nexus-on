import { useState } from 'react'
import type { AgentReport } from '../../types'

type Props = {
  report: AgentReport | null
  counts: { asks: number; redAsks: number; blocked: number }
  onOpenDashboard: () => void
  onSendMessage: (text: string) => Promise<void>
}

function pickSummary(report: AgentReport | null) {
  const cards = report?.ui_hint?.cards ?? []
  const first = cards[0]
  return first?.body ?? '대기 중입니다.'
}

function computeStageCards(report: AgentReport | null) {
  const asks = report?.ask ?? []
  const next = report?.next ?? []
  const urgent = next.find(n => (n.eta ?? '').toLowerCase() === 'now' || (n.title ?? '').includes('마감'))
  const red = asks.filter(a => a.severity === 'red').length
  const schedule = (pickSummary(report).includes('캘린더') ? '캘린더 권한 확인 필요' : '일정: 데이터 없음')
  return {
    urgent: urgent ? `${urgent.title} — ${urgent.detail}` : '긴급 마감: 없음',
    approvals: red ? `RED 승인 대기: ${red}건` : 'RED 승인: 없음',
    schedule
  }
}

export function AssistantStage(p: Props) {
  const stage = computeStageCards(p.report)
  const [chatInput, setChatInput] = useState('')
  const [sending, setSending] = useState(false)

  async function handleSend() {
    if (!chatInput.trim() || sending) return
    setSending(true)
    try {
      await p.onSendMessage(chatInput.trim())
      setChatInput('')
    } catch (err) {
      console.error('[AssistantStage] Send failed:', err)
      alert('메시지 전송 실패. 다시 시도해주세요.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="stage">
      <div className="stageLeft">
        <div className="character">
          <div className="characterFrame">
            <div className="characterName">Seria</div>
            <div className="characterSub">Assistant Stage (Live2D placeholder)</div>
            <div className="characterFace">◉</div>
          </div>
          <div className="caption">
            <div className="captionTag">voice</div>
            <div className="captionText">{pickSummary(p.report)}</div>
          </div>
        </div>
      </div>

      <div className="stageRight">
        <div className="stageCards">
          <div className="stageCard">
            <div className="stageCardTitle">긴급 마감</div>
            <div className="stageCardBody">{stage.urgent}</div>
          </div>
          <div className="stageCard">
            <div className="stageCardTitle">RED 승인</div>
            <div className="stageCardBody">{stage.approvals}</div>
          </div>
          <div className="stageCard">
            <div className="stageCardTitle">다음 일정</div>
            <div className="stageCardBody">{stage.schedule}</div>
          </div>
        </div>

        <div className="stageActions">
          <button className="btn primary" onClick={p.onOpenDashboard}>대시보드로 이동</button>
          <button className="btn" onClick={() => alert('Dock로 축소: 화면 하단 Dock를 클릭하세요.')}>Dock로 축소</button>
        </div>

        {/* 채팅 입력창 */}
        <div className="chatInput">
          <input
            type="text"
            value={chatInput}
            onChange={e => setChatInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="메시지를 입력하세요..."
            disabled={sending}
          />
          <button className="btn primary" onClick={handleSend} disabled={sending || !chatInput.trim()}>
            {sending ? '전송 중...' : '전송'}
          </button>
        </div>

        <div className="stageNote">
          정책: UI 갱신 단일 소스는 stream report. POST(202)는 수락 확인만.
        </div>
      </div>
    </div>
  )
}
