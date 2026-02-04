# NEXUS UI v1.1 컴포넌트 스펙 (보완판)

> **기준일**: 2026-02-03  
> **기반**: design_tokens_v1_0.md + 구현 보완

---

## **1. Live2D 캐릭터 규격**

### **크기 및 위치**
```css
.live2d-character {
  width: var(--live2d-width);   /* 280px */
  height: var(--live2d-height); /* 320px */
  
  /* Desktop: 좌측 상단 고정 */
  @media (min-width: 1024px) {
    position: fixed;
    top: var(--live2d-top);
    left: var(--live2d-left);
  }
  
  /* Mobile: 하단 우측 */
  @media (max-width: 1023px) {
    position: fixed;
    bottom: var(--live2d-bottom-mobile);
    right: var(--live2d-right-mobile);
    width: 140px;  /* 모바일에서 50% 축소 */
    height: 160px;
  }
  
  /* GPU 가속 */
  will-change: transform;
  transform: translateZ(0);
}
```

### **애니메이션 규격**
| 상태 | 트리거 | 지속 시간 | 설명 |
|------|--------|-----------|------|
| **Idle** | 기본 | 2-3초 주기 | 깜빡임, 미세 호흡 |
| **Speaking** | 자막 출력 | 동기화 | 입 모양 변화 (립싱크) |
| **Listening** | 사용자 입력 | 1.5초 | 부드러운 고개 끄덕임 |
| **Thinking** | LLM 응답 대기 | 반복 | 시선 이동 (좌→우→좌) |

### **상태별 Glow 효과**
```css
/* Busy 상태 (노란색 Glow) */
.live2d-character[data-status="busy"] {
  filter: drop-shadow(var(--live2d-glow-busy));
  animation: pulse-glow-busy 2s ease-in-out infinite;
}

/* Alert/RED 상태 (빨간색 Glow) */
.live2d-character[data-status="alert"] {
  filter: drop-shadow(var(--live2d-glow-alert));
  animation: pulse-glow-alert 1s ease-in-out infinite;
}

@keyframes pulse-glow-busy {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-glow-alert {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

### **인터랙션 규칙**
- **클릭**: 없음 (의도적 제한, 실수 클릭 방지)
- **롱프레스** (800ms): 설정 메뉴 표시
  - 음성 ON/OFF
  - 자막 ON/OFF
  - 일시정지
  - 설정

### **성능 요구사항**
- ✅ 모바일 60fps 유지 필수
- ✅ GPU 가속 (`will-change`, `transform3d`)
- ✅ 애니메이션 프레임 드롭 시 자동 품질 하락
- ✅ `prefers-reduced-motion`에서 애니메이션 중단

---

## **2. Stage 3카드 레이아웃**

### **카드 구조**
```html
<div class="stage-cards">
  <div class="stage-card" data-type="urgent">
    <div class="card-header">
      <div class="card-badge" data-status="yellow">긴급</div>
      <span class="card-time">2시간 전</span>
    </div>
    <h3 class="card-title">월말 보고서 마감</h3>
    <p class="card-description">오늘 18:00까지 제출 필요</p>
    <div class="card-actions">
      <button class="btn-primary">지금 처리</button>
      <button class="btn-ghost">내일로 연기</button>
    </div>
  </div>
  
  <!-- RED 승인 카드 -->
  <!-- 다음 일정 카드 -->
</div>
```

### **반응형 레이아웃**
```css
.stage-cards {
  display: grid;
  gap: var(--space-4);  /* 16px */
  padding: var(--space-4);
  
  /* Desktop: 3열 고정 */
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
    max-width: var(--max-width-content);  /* 1240px */
    margin: 0 auto;
  }
  
  /* Tablet: 2열 + 1열 */
  @media (min-width: 768px) and (max-width: 1023px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  /* Mobile: 1열 스택 */
  @media (max-width: 767px) {
    grid-template-columns: 1fr;
  }
}
```

### **카드 스타일**
```css
.stage-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-card);  /* 18px */
  padding: var(--space-5);  /* 20px */
  min-height: 240px;
  
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  
  transition: all var(--duration-ui) var(--ease-out);
  
  /* 호버 효과 */
  &:hover {
    border-color: var(--accent-primary);
    box-shadow: var(--shadow-md);
  }
  
  /* 카드 타입별 좌측 강조선 */
  &[data-type="urgent"] {
    border-left: 3px solid var(--color-warning);
  }
  
  &[data-type="red-approval"] {
    border-left: 3px solid var(--color-danger);
  }
  
  &[data-type="next-schedule"] {
    border-left: 3px solid var(--accent-primary);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  
  &[data-status="green"] {
    background: var(--status-green-bg);
    color: var(--status-green);
  }
  
  &[data-status="yellow"] {
    background: var(--status-yellow-bg);
    color: var(--status-yellow);
  }
  
  &[data-status="red"] {
    background: var(--status-red-bg);
    color: var(--status-red);
  }
}

.card-time {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.card-title {
  font-size: var(--text-xl);  /* 22px */
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
}

.card-description {
  font-size: var(--text-base);
  color: var(--text-secondary);
  line-height: var(--leading-normal);
  flex: 1;  /* 공간 채우기 */
}

.card-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: auto;  /* 하단 정렬 */
}
```

---

## **3. Dashboard 3컬럼 카드 시스템**

### **컬럼 구조**
```html
<div class="dashboard-columns">
  <!-- Asks 컬럼 -->
  <div class="dashboard-column" data-column="asks">
    <h2 class="column-title">승인 요청 (3)</h2>
    <div class="dashboard-card" data-clickable="true">
      <div class="card-icon" data-status="red">⚠️</div>
      <div class="card-content">
        <h4 class="card-title">경비 지출 승인</h4>
        <p class="card-meta">250만원 · 2시간 전</p>
      </div>
    </div>
    <!-- 더 많은 카드... -->
  </div>
  
  <!-- Worklog 컬럼 -->
  <div class="dashboard-column" data-column="worklog">
    <h2 class="column-title">작업 내역</h2>
    <!-- 카드들... -->
  </div>
  
  <!-- Autopilot 컬럼 -->
  <div class="dashboard-column" data-column="autopilot">
    <h2 class="column-title">자동 처리됨</h2>
    <!-- 카드들... -->
  </div>
</div>
```

### **컬럼 레이아웃**
```css
.dashboard-columns {
  display: grid;
  gap: var(--space-4);
  height: calc(100vh - 64px - 48px);  /* TopNav(64) - Dock(48) */
  overflow: hidden;
  
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
    padding: var(--space-4);
  }
  
  @media (max-width: 1023px) {
    /* 모바일: 탭 UI로 전환 (별도 구현) */
    grid-template-columns: 1fr;
  }
}

.dashboard-column {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  overflow-y: auto;  /* 각 컬럼 독립 스크롤 */
  padding: var(--space-4);
  background: var(--bg-secondary);
  border-radius: var(--radius-card);
  
  /* 스크롤바 스타일링 */
  scrollbar-width: thin;
  scrollbar-color: var(--border-strong) transparent;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border-strong);
    border-radius: var(--radius-pill);
    
    &:hover {
      background: var(--text-tertiary);
    }
  }
}

.column-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  position: sticky;
  top: 0;
  background: var(--bg-secondary);
  padding-bottom: var(--space-2);
  z-index: 1;
}
```

### **카드 스타일**
```css
.dashboard-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-control);  /* 12px */
  padding: var(--space-4);
  
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  
  transition: all var(--duration-ui) var(--ease-out);
  
  /* 클릭 가능한 카드 */
  &[data-clickable="true"] {
    cursor: pointer;
    
    &:hover {
      border-color: var(--accent-primary);
      box-shadow: var(--shadow-sm);
      transform: translateY(-1px);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
}

.card-icon {
  font-size: var(--icon-lg);  /* 32px */
  flex-shrink: 0;
  
  /* 상태별 배경 */
  &[data-status="red"] {
    background: var(--color-danger-soft);
    border-radius: var(--radius-sm);
    padding: var(--space-2);
  }
  
  &[data-status="yellow"] {
    background: var(--color-warning-soft);
    border-radius: var(--radius-sm);
    padding: var(--space-2);
  }
}

.card-content {
  flex: 1;
  min-width: 0;  /* Flexbox 오버플로우 방지 */
}

.card-title {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
  
  /* 텍스트 오버플로우 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}
```

---

## **4. Sidecar 포커스 트랩**

### **HTML 구조**
```html
<aside 
  class="sidecar" 
  role="dialog" 
  aria-modal="true"
  aria-labelledby="sidecar-title"
  data-open="true"
>
  <div class="sidecar-header">
    <h2 id="sidecar-title">요약</h2>
    <button class="btn-icon" aria-label="닫기" data-action="close">
      <svg><!-- X 아이콘 --></svg>
    </button>
  </div>
  
  <div class="sidecar-content">
    <!-- 3섹션: 요약/핵심/액션 -->
  </div>
</aside>
```

### **포커스 트랩 구현**
```typescript
// /home/user/webapp/frontend/src/lib/useFocusTrap.ts

import { useEffect, useRef } from 'react';

export function useFocusTrap(isOpen: boolean, onClose: () => void) {
  const containerRef = useRef<HTMLElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen || !containerRef.current) return;

    // 이전 포커스 저장
    previousActiveElement.current = document.activeElement as HTMLElement;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Tab 키 트랩
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    // ESC 키로 닫기
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    container.addEventListener('keydown', handleTab);
    container.addEventListener('keydown', handleEscape);
    
    // 첫 번째 요소에 포커스
    firstElement?.focus();

    // 클린업: 포커스 복원
    return () => {
      container.removeEventListener('keydown', handleTab);
      container.removeEventListener('keydown', handleEscape);
      previousActiveElement.current?.focus();
    };
  }, [isOpen, onClose]);

  return containerRef;
}
```

### **사용 예시**
```typescript
// Sidecar.tsx
import { useFocusTrap } from '../lib/useFocusTrap';

function Sidecar({ isOpen, onClose }: Props) {
  const sidecarRef = useFocusTrap(isOpen, onClose);

  return (
    <aside 
      ref={sidecarRef}
      className="sidecar" 
      data-open={isOpen}
      role="dialog"
      aria-modal="true"
    >
      {/* 콘텐츠 */}
    </aside>
  );
}
```

---

## **5. Dock 상태 표시**

### **HTML 구조**
```html
<div class="dock" data-status="idle" data-longpress="false">
  <div class="dock-avatar">
    <img src="/avatar.png" alt="Nexus Assistant" />
  </div>
  <div class="dock-info">
    <span class="dock-name">NEXUS</span>
    <span class="dock-mode">대기 중</span>
  </div>
  <div class="dock-badges">
    <span class="badge" data-type="red">3</span>
    <span class="badge" data-type="yellow">5</span>
  </div>
</div>
```

### **상태별 스타일**
```css
.dock {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 48px;
  
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0 var(--space-4);
  
  background: var(--bg-primary);
  border-top: 1px solid var(--border-default);
  
  z-index: var(--z-sticky);
  
  cursor: pointer;
  transition: all var(--duration-ui) var(--ease-out);
  
  /* Idle 상태 (기본) */
  &[data-status="idle"] {
    background: var(--bg-primary);
  }
  
  /* Busy 상태 */
  &[data-status="busy"] {
    background: var(--color-warning-soft);
    border-top-color: var(--color-warning);
    
    .dock-avatar::after {
      content: '';
      position: absolute;
      inset: -2px;
      border-radius: 50%;
      border: 2px solid var(--color-warning);
      animation: pulse-warning 2s ease-in-out infinite;
    }
  }
  
  /* Alert/RED 상태 */
  &[data-status="alert"] {
    background: var(--color-danger-soft);
    border-top-color: var(--color-danger);
    
    .dock-avatar::after {
      border: 2px solid var(--color-danger);
      animation: pulse-danger 1s ease-in-out infinite;
    }
  }
}

.dock-avatar {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

@keyframes pulse-warning {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}

@keyframes pulse-danger {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.1); }
}

/* 롱프레스 진행 인디케이터 */
.dock[data-longpress="true"]::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--accent-primary);
  animation: longpress-progress 800ms linear;
}

@keyframes longpress-progress {
  from { width: 0%; }
  to { width: 100%; }
}

.dock-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dock-name {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.dock-mode {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.dock-badges {
  margin-left: auto;
  display: flex;
  gap: var(--space-2);
}

.badge {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  
  &[data-type="red"] {
    background: var(--color-danger-soft);
    color: var(--color-danger);
  }
  
  &[data-type="yellow"] {
    background: var(--color-warning-soft);
    color: var(--color-warning);
  }
}
```

---

## **6. Reduced Motion 구현**

```css
/* design-tokens.css에 이미 포함됨 */

@media (prefers-reduced-motion: reduce) {
  /* 모든 애니메이션/트랜지션 최소화 */
  :root {
    --duration-micro: 0ms;
    --duration-ui: 0ms;
    --duration-modal: 0ms;
  }
  
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  
  /* Live2D 캐릭터 애니메이션 중단 */
  .live2d-character {
    animation: none !important;
  }
  
  /* Dock 펄스 애니메이션 중단 */
  .dock[data-status="busy"] .dock-avatar::after,
  .dock[data-status="alert"] .dock-avatar::after {
    animation: none !important;
    opacity: 1 !important;
  }
  
  /* 필수 시각적 피드백만 유지 (opacity만) */
  .button:hover,
  .card:hover {
    transition: opacity var(--duration-micro) !important;
  }
}
```

---

## **7. 아이콘 시스템**

### **권장 라이브러리**
```bash
npm install lucide-react
```

### **필수 아이콘 목록 (30개)**

#### **Navigation (5개)**
- `Home` - Stage 뷰
- `LayoutDashboard` - Dashboard 뷰
- `Youtube` - YouTube 패널
- `Server` - Nodes 관리
- `Settings` - 설정

#### **Stage 제어 (5개)**
- `Mic` / `MicOff` - 음성 입력
- `Pause` / `Play` - 일시정지/재생
- `SkipForward` - 건너뛰기

#### **Actions (8개)**
- `Check` - 승인
- `X` - 거부
- `RotateCcw` - 되돌리기
- `RotateCw` - 다시 실행
- `Edit` - 수정
- `Trash2` - 삭제
- `Save` - 저장
- `Ban` - 취소

#### **Status (5개)**
- `CheckCircle` - 성공
- `AlertTriangle` - 경고
- `AlertCircle` - 위험
- `Info` - 정보
- `Loader2` - 로딩 (회전)

#### **Utility (7개)**
- `X` - 닫기
- `ChevronRight` / `ChevronDown` - 화살표
- `ExternalLink` - 외부 링크
- `Search` - 검색
- `Filter` - 필터
- `Menu` - 메뉴

### **아이콘 사용 예시**
```typescript
import { Mic, MicOff, Check, X } from 'lucide-react';

function StageControls() {
  return (
    <div className="stage-controls">
      <button className="btn-icon" aria-label="음성 입력">
        <Mic size={24} strokeWidth={1.75} />
      </button>
      <button className="btn-primary">
        <Check size={20} strokeWidth={1.75} />
        승인
      </button>
      <button className="btn-ghost">
        <X size={20} strokeWidth={1.75} />
        거부
      </button>
    </div>
  );
}
```

### **아이콘 CSS**
```css
.icon {
  /* 기본 크기 */
  width: var(--icon-md);  /* 24px */
  height: var(--icon-md);
  
  /* 색상 */
  color: var(--icon-primary);
  
  /* Stroke 규격 (LOCKED) */
  stroke-width: var(--icon-stroke);  /* 1.75px */
  
  /* 크기 변형 */
  &.icon-xs { width: var(--icon-xs); height: var(--icon-xs); }
  &.icon-sm { width: var(--icon-sm); height: var(--icon-sm); }
  &.icon-lg { width: var(--icon-lg); height: var(--icon-lg); }
  &.icon-xl { width: var(--icon-xl); height: var(--icon-xl); }
  
  /* 색상 변형 */
  &.icon-secondary { color: var(--icon-secondary); }
  &.icon-tertiary { color: var(--icon-tertiary); }
  &.icon-accent { color: var(--icon-accent); }
  &.icon-danger { color: var(--icon-danger); }
}
```

---

## **8. 온보딩 마이크로 일러스트 (P2)**

### **디자인 규칙**
- **색상**: 그레이스케일 + 포인트 accent 1곳만
- **파일 크기**: < 10KB (SVG 최적화 필수)
- **애니메이션**: < 3초, 1회만 재생
- **위치**: 온보딩 슬라이드 상단 중앙

### **예시 구조**
```html
<div class="onboarding-illustration">
  <svg width="240" height="160" viewBox="0 0 240 160">
    <!-- 그레이스케일 배경 요소 -->
    <rect fill="#F0F0F2" />
    
    <!-- 포인트 accent (1곳만) -->
    <circle fill="var(--accent-primary)" />
  </svg>
</div>
```

---

## **요약: 보완된 내용**

| 항목 | 상태 | 파일 위치 |
|------|------|-----------|
| **Icon System** | ✅ 추가 | `design-tokens.css` |
| **Live2D Character** | ✅ 추가 | `design-tokens.css` + 이 문서 |
| **Stage 3-Card Layout** | ✅ 추가 | 이 문서 |
| **Dashboard 3-Column** | ✅ 추가 | 이 문서 |
| **Sidecar Focus Trap** | ✅ 추가 | 이 문서 + `useFocusTrap.ts` |
| **Dock Status** | ✅ 추가 | 이 문서 |
| **Reduced Motion** | ✅ 이미 포함 | `design-tokens.css` |
| **Onboarding 일러스트** | 📝 가이드만 | 이 문서 |

---

**다음 단계**: 이 스펙을 기반으로 실제 컴포넌트 구현 시작
