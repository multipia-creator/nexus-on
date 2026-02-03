# NEXUS 데모 모드 가이드

**작성일**: 2026-02-03  
**버전**: v2.0  
**목적**: 백엔드 없이도 동작하는 SaaS 데모 모드 설명

---

## 📋 개요

NEXUS Frontend는 **데모 모드**를 지원하여 백엔드 서버 없이도 완전히 동작합니다. 이는 SaaS 데모, 오프라인 개발, 프레젠테이션 등에 유용합니다.

---

## 🎯 데모 모드 특징

### ✅ **지원 기능**
1. **Mock SSE 스트림**
   - Snapshot → Report 시퀀스 자동 생성
   - 5개의 다양한 Report 템플릿 (Green/Yellow/Red)
   - 1초 간격으로 이벤트 전송 (실제 스트리밍 시뮬레이션)

2. **Mock Devices API**
   - 3개의 Mock 디바이스 (Desktop, Laptop, Server)
   - 온라인/오프라인 상태 시뮬레이션
   - 페어링 성공 메시지

3. **UI 동작**
   - AssistantStage, Dashboard, Sidecar 완전 동작
   - Devices Modal 페어링 흐름
   - 상태 표시 (DEMO MODE 배지)

### ❌ **제한 사항**
- `/chat`, `/sidecar/command`, `/approvals` API 호출 무시
- 데이터 영속성 없음 (페이지 새로고침 시 초기화)
- 백엔드 의존 기능 미동작

---

## 🔧 설정 방법

### **1. 환경 변수 설정**

#### `.env.local` 파일 생성
```bash
cd /home/user/webapp/frontend
cp .env.local.example .env.local
```

#### 데모 모드 활성화
```env
VITE_API_BASE=http://localhost:8000
VITE_DEMO_MODE=true
```

**옵션**:
- `VITE_DEMO_MODE=true` → 데모 모드 활성화
- `VITE_DEMO_MODE=false` → 실제 백엔드 모드 (기본값)
- `VITE_DEMO_MODE=1` → 데모 모드 활성화 (대체 표기)

---

### **2. 실행 방법**

#### Frontend만 실행 (백엔드 불필요)
```bash
cd /home/user/webapp/frontend
npm install  # 최초 1회만
npm run dev
```

**접속**: http://localhost:5173

#### 빌드 (프로덕션)
```bash
cd /home/user/webapp/frontend
npm run build
# 빌드 결과: dist/
```

---

## 🎭 데모 모드 동작 방식

### **1. SSE 스트림 (Mock)**

**실제 백엔드 호출 대신**:
```typescript
// useAgentReportStream.ts
if (p.demoMode) {
  const stream = createMockSSEStream(p.sessionId)
  for (const chunk of stream) {
    // SSE 이벤트 파싱 및 전송
    // 1초 간격으로 이벤트 전송
  }
}
```

**Mock 이벤트 시퀀스**:
1. **Snapshot** (event_id: 0) → 초기 상태
2. **Ping** (id 없음) → 연결 확인
3. **Report 1-5** (event_id: 1-5) → 다양한 시나리오

---

### **2. Devices API (Mock)**

**페어링 확인**:
```typescript
// devices/api.ts
export async function pairingConfirmByCode(pairingCode: string) {
  if (isDemoMode()) {
    await new Promise(resolve => setTimeout(resolve, 500))
    return { device_id: 'demo-device-new', message: '페어링 성공 (데모 모드)' }
  }
  // 실제 API 호출...
}
```

**디바이스 목록**:
```typescript
export async function listDevices(orgId: string, projectId: string) {
  if (isDemoMode()) {
    return mockDevices.map(d => ({
      device_id: d.device_id,
      device_name: d.device_name,
      device_type: d.device_type,
      status: d.status,
      last_seen_epoch: new Date(d.last_seen).getTime(),
      capabilities: d.capabilities
    }))
  }
  // 실제 API 호출...
}
```

---

### **3. UI 표시**

**데모 모드 배지**:
```tsx
// Shell.tsx
<div className="brandTitle">NEXUS UI Skeleton {demoMode && '🎭 DEMO'}</div>
<span className="pill" style={{ backgroundColor: '#ff9800' }}>DEMO MODE</span>
```

**API 호출 무시**:
```typescript
async function emitChat() {
  if (demoMode) {
    console.log('[Demo Mode] Skipping /chat API call')
    return
  }
  await postJSON('/chat', { ... })
}
```

---

## 📦 Mock 데이터 구조

### **Mock Devices**
```typescript
export const mockDevices: MockDevice[] = [
  {
    device_id: 'demo-device-001',
    device_name: 'Demo Desktop PC',
    device_type: 'windows_desktop',
    status: 'online',
    last_seen: new Date().toISOString(),
    capabilities: ['file_ops', 'shell', 'screenshot']
  },
  // ... 2개 더
]
```

### **Mock AgentReport (Snapshot)**
```typescript
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
    // ...
  },
  done: [],
  next: [{ title: '환영합니다!', detail: 'NEXUS 데모 모드...', ... }],
  // ...
})
```

### **Mock Report 템플릿 (5종)**
1. **파일 분석 완료** (Green)
2. **배포 준비 중** (Yellow)
3. **외부 API 호출 승인 필요** (Red)
4. **데이터베이스 마이그레이션 완료** (Green)
5. **로그 분석 중** (Green)

---

## 🧪 테스트 시나리오

### **시나리오 1: SSE 스트림 확인**
1. 데모 모드 활성화 (`.env.local` → `VITE_DEMO_MODE=true`)
2. Frontend 실행 (`npm run dev`)
3. 브라우저 접속 (http://localhost:5173)
4. **확인 사항**:
   - 상단 "DEMO MODE" 배지 표시
   - SSE 스트림 자동 연결 (connected)
   - 1초 간격으로 Report 수신 (총 5개)
   - Dashboard에서 Report 내용 확인

---

### **시나리오 2: Devices 페어링**
1. 상단 **Devices** 버튼 클릭
2. Modal 열림 → 페어링 코드 입력 (임의 값, 예: `123-456`)
3. **Confirm** 클릭
4. **확인 사항**:
   - "페어링이 성공적으로 완료되었습니다. (데모 모드)" 메시지
   - Device 목록에 3개 디바이스 표시
   - 온라인/오프라인 상태 표시

---

### **시나리오 3: API 호출 무시**
1. 상단 **Emit /chat**, **Emit RED**, **Approvals yes** 버튼 클릭
2. **확인 사항**:
   - 콘솔에 `[Demo Mode] Skipping ... API call` 메시지
   - 실제 API 호출 없음 (Network 탭 확인)

---

### **시나리오 4: 빌드 및 배포**
```bash
cd /home/user/webapp/frontend
npm run build
# 빌드 성공 확인: dist/ 디렉토리 생성
```

**배포 방법**:
- Netlify, Vercel, Cloudflare Pages에 `dist/` 디렉토리 배포
- 환경 변수 `VITE_DEMO_MODE=true` 설정

---

## 🔄 데모 모드 <-> 실제 백엔드 전환

### **데모 모드 → 실제 백엔드**
```env
# .env.local
VITE_API_BASE=http://localhost:8000
VITE_DEMO_MODE=false  # 또는 삭제
```

**재시작**:
```bash
npm run dev
```

**확인**:
- "DEMO MODE" 배지 사라짐
- SSE 스트림이 실제 백엔드로 연결
- Devices API가 실제 백엔드 호출

---

### **실제 백엔드 → 데모 모드**
```env
# .env.local
VITE_DEMO_MODE=true
```

**재시작**:
```bash
npm run dev
```

---

## 📊 파일 변경 내역

| 파일 | 변경 내용 | 용도 |
|------|----------|------|
| `.env.local.example` | `VITE_DEMO_MODE` 추가 | 환경 변수 예시 |
| `src/lib/mockData.ts` | 신규 생성 (6KB) | Mock 데이터 정의 |
| `src/devices/api.ts` | `isDemoMode()` 추가 | 데모 모드 감지 |
| `src/devices/api.ts` | `pairingConfirmByCode()` 수정 | Mock 응답 추가 |
| `src/devices/api.ts` | `listDevices()` 수정 | Mock 디바이스 반환 |
| `src/stream/useAgentReportStream.ts` | `demoMode` 파라미터 추가 | Mock SSE 스트림 |
| `src/shell/Shell.tsx` | `isDemoMode()` 호출 | 데모 모드 감지 및 UI |

**총 변경**: 1개 신규 파일, 4개 기존 파일 수정

---

## 🚨 주의 사항

### **1. 타입 안정성**
✅ **보장**:
- `AgentReport` 스키마 100% 준수
- `DeviceInfo` 타입 일치
- TypeScript 빌드 통과 (0 에러)

### **2. UI 호환성**
✅ **보장**:
- 기존 UI 컴포넌트 100% 호환
- AssistantStage, Dashboard, Sidecar 정상 동작
- Devices Modal 페어링 흐름 유지

### **3. 데이터 영속성**
⚠️ **제한**:
- Mock 데이터는 메모리에만 존재
- 페이지 새로고침 시 초기화
- `localStorage`의 `last_event_id`는 유지되나 Mock 이벤트는 재생성

### **4. 프로덕션 배포**
⚠️ **주의**:
- 데모 모드는 **개발/데모 목적**으로만 사용
- 실제 사용자에게는 `VITE_DEMO_MODE=false` 권장
- 프로덕션 환경에서는 실제 백엔드 연결 필요

---

## 🎉 결론

NEXUS Frontend의 **데모 모드**는:
- ✅ 백엔드 없이도 완전히 동작
- ✅ 기존 UI/타입 100% 호환
- ✅ TypeScript 빌드 통과
- ✅ SaaS 데모, 오프라인 개발, 프레젠테이션에 최적

**환경 변수 1개(`VITE_DEMO_MODE=true`)만으로 간편하게 전환 가능!** 🚀

---

**최종 업데이트**: 2026-02-03  
**작성자**: AI Assistant (Claude Code)  
**문의**: `/home/user/webapp/docs/` 디렉토리 참조
