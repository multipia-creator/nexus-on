import type { AgentReport } from '../types'

// Mock Device 타입 정의
export interface MockDevice {
  device_id: string
  device_name: string
  device_type: string
  status: 'online' | 'offline'
  last_seen: string
  capabilities: string[]
}

// Mock Devices 데이터
export const mockDevices: MockDevice[] = [
  {
    device_id: 'demo-device-001',
    device_name: 'Demo Desktop PC',
    device_type: 'windows_desktop',
    status: 'online',
    last_seen: new Date().toISOString(),
    capabilities: ['file_ops', 'shell', 'screenshot']
  },
  {
    device_id: 'demo-device-002',
    device_name: 'Demo Laptop',
    device_type: 'windows_laptop',
    status: 'online',
    last_seen: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    capabilities: ['file_ops', 'shell']
  },
  {
    device_id: 'demo-device-003',
    device_name: 'Demo Server',
    device_type: 'linux_server',
    status: 'offline',
    last_seen: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    capabilities: ['file_ops', 'shell', 'docker']
  }
]

// Mock AgentReport: Snapshot
export const createMockSnapshot = (sessionId: string): AgentReport => ({
  meta: {
    mode: 'focused',
    approval_level: 'green',
    confidence: 0.85,
    report_id: `snapshot_${sessionId}_${Date.now()}`,
    created_at: new Date().toISOString(),
    event_id: 0,
    tenant: 'demo:demo',
    session_id: sessionId,
    user_id: 'demo-user',
    json_repaired: false,
    causality: {
      correlation_id: '',
      command_id: null,
      ask_id: null,
      type: 'snapshot'
    }
  },
  done: [],
  next: [
    {
      title: '환영합니다!',
      detail: 'NEXUS 데모 모드가 활성화되었습니다. 모든 데이터는 Mock으로 동작합니다.',
      owner: 'Seria',
      eta: 'now'
    }
  ],
  blocked: [],
  ask: [],
  risk: [],
  rationale: '데모 모드에서 초기 스냅샷을 생성했습니다.',
  undo: [],
  ui_hint: {
    surface: 'dashboard',
    cards: [
      {
        type: 'welcome',
        title: '데모 모드',
        body: '현재 NEXUS는 데모 모드로 실행 중입니다. 백엔드 연결 없이 Mock 데이터로 동작합니다.'
      }
    ],
    actions: [
      {
        id: 'demo-action-1',
        label: 'Mock Report 생성',
        style: 'primary'
      }
    ]
  },
  persona_id: 'seria.istj',
  skin_id: 'seria.default'
})

// Mock AgentReport: 일반 Report (시퀀스)
const mockReportTemplates = [
  {
    title: '파일 분석 완료',
    detail: '총 42개의 파일을 분석했습니다. 3개의 주의사항을 발견했습니다.',
    approval_level: 'green' as const,
    cards: [
      {
        type: 'info',
        title: '분석 결과',
        body: '코드 품질: 양호 | 보안 이슈: 없음 | 성능 개선 가능: 3건'
      }
    ]
  },
  {
    title: '배포 준비 중',
    detail: 'Docker 이미지를 빌드하고 있습니다...',
    approval_level: 'yellow' as const,
    cards: [
      {
        type: 'progress',
        title: '빌드 진행 상황',
        body: 'Step 3/5: Installing dependencies...'
      }
    ]
  },
  {
    title: '외부 API 호출 승인 필요',
    detail: '민감한 데이터를 외부 서비스로 전송하려고 합니다.',
    approval_level: 'red' as const,
    cards: [
      {
        type: 'warning',
        title: '승인 필요',
        body: '외부 API 호출 전 사용자 승인이 필요합니다.'
      }
    ]
  },
  {
    title: '데이터베이스 마이그레이션 완료',
    detail: '5개의 테이블이 업데이트되었습니다.',
    approval_level: 'green' as const,
    cards: [
      {
        type: 'success',
        title: '마이그레이션 완료',
        body: 'users, posts, comments, likes, notifications 테이블이 업데이트되었습니다.'
      }
    ]
  },
  {
    title: '로그 분석 중',
    detail: '최근 24시간 동안의 에러 로그를 분석하고 있습니다...',
    approval_level: 'green' as const,
    cards: [
      {
        type: 'info',
        title: '로그 분석',
        body: '에러 발생: 12건 | 경고: 48건 | 정보: 3,542건'
      }
    ]
  }
]

export const createMockReport = (
  sessionId: string,
  eventId: number,
  templateIndex?: number
): AgentReport => {
  const index = templateIndex ?? Math.floor(Math.random() * mockReportTemplates.length)
  const template = mockReportTemplates[index % mockReportTemplates.length]

  return {
    meta: {
      mode: 'focused',
      approval_level: template.approval_level,
      confidence: 0.7 + Math.random() * 0.25,
      report_id: `report_${sessionId}_${eventId}_${Date.now()}`,
      created_at: new Date().toISOString(),
      event_id: eventId,
      tenant: 'demo:demo',
      session_id: sessionId,
      user_id: 'demo-user',
      json_repaired: false,
      causality: {
        correlation_id: `corr_${Date.now()}`,
        command_id: null,
        ask_id: template.approval_level === 'red' ? `ask_${Date.now()}` : null,
        type: 'agent.task'
      }
    },
    done: template.approval_level === 'green' ? [{ title: template.title, detail: template.detail }] : [],
    next:
      template.approval_level !== 'green'
        ? [{ title: template.title, detail: template.detail, owner: 'Seria', eta: '5m' }]
        : [],
    blocked: [],
    ask:
      template.approval_level === 'red'
        ? [
            {
              question: '외부 API 호출을 승인하시겠습니까?',
              type: 'confirm',
              severity: 'red',
              options: ['승인', '거부'],
              default: '거부'
            }
          ]
        : [],
    risk:
      template.approval_level === 'red'
        ? [
            {
              level: 'high',
              item: '민감한 데이터 외부 전송',
              mitigation: '데이터 암호화 및 HTTPS 사용'
            }
          ]
        : [],
    rationale: `데모 모드: ${template.detail}`,
    undo: [],
    ui_hint: {
      surface: 'dashboard',
      cards: template.cards,
      actions: []
    },
    persona_id: 'seria.istj',
    skin_id: 'seria.default'
  }
}

// Mock SSE 이벤트 생성기
export function* createMockSSEStream(sessionId: string): Generator<string, void, unknown> {
  // 1. Snapshot 전송
  const snapshot = createMockSnapshot(sessionId)
  yield `event: snapshot\nid: 0\ndata: ${JSON.stringify(snapshot)}\n\n`

  // 2. Ping 이벤트 (optional)
  yield `event: ping\ndata: ${JSON.stringify({ ts: Date.now() })}\n\n`

  // 3. Report 시퀀스 (5개)
  for (let i = 1; i <= 5; i++) {
    const report = createMockReport(sessionId, i)
    yield `event: report\nid: ${i}\ndata: ${JSON.stringify(report)}\n\n`
  }
}

// Mock Pairing 응답
export const mockPairingResponse = {
  device_id: 'demo-device-new',
  message: '페어링이 성공적으로 완료되었습니다. (데모 모드)'
}
