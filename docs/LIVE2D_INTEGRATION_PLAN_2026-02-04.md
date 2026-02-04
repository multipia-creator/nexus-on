# NEXUS-ON Live2D 통합 계획서

**작성일**: 2026-02-04  
**작성자**: AI 개발자 (Claude)  
**프로젝트**: NEXUS-ON Live2D Character AI Assistant  
**목표**: 마케팅 사이트와 실제 서비스에 Live2D 캐릭터 완전 통합

---

## 📋 현재 상황 분석

### ✅ 완료된 사항
1. **설계 문서 완성**
   - `MARKETING_SITE_CONCEPT_LIVE2D_2026-02-04.md`
   - `COMPONENT_SPECS_v1_1.md` (Live2D 규격 포함)
   - `WORLD_CLASS_REDESIGN_STRATEGY_2026-02-04.md`

2. **마케팅 사이트 구조**
   - 7개 페이지 완성 (홈/소개/모듈/가격/대시보드/캔버스/로그인)
   - 한영 전환 기능
   - NEXUS UI v2.0 디자인 시스템
   - Live2D 플레이스홀더 포함

3. **기술 스택 준비**
   - Backend: FastAPI (Python)
   - Frontend: TypeScript + Vite
   - 프론트엔드 프레임워크: 현재 없음 (Vanilla JS/TS)

### ❌ 미완성 사항
1. **Live2D 모델 파일 없음**
   - `.moc3` 파일 (모델 데이터)
   - `.model3.json` (모델 설정)
   - `.motion3.json` (애니메이션 데이터)
   - 텍스처 파일들 (PNG)

2. **Live2D SDK 미설치**
   - Live2D Cubism SDK for Web 미포함
   - JavaScript 통합 코드 없음

3. **애니메이션 상태 연동 없음**
   - 페이지별 상태 전환 로직 없음
   - SSE 이벤트 연동 없음

---

## 🎯 Live2D 통합 전략 (3가지 옵션)

### **Option A: 완전 통합 (실제 Live2D 모델 사용)** ⭐ 권장
**장점**:
- 프리미엄 경험 제공
- 완전한 브랜드 정체성
- 5가지 애니메이션 상태 완전 구현

**단점**:
- 모델 제작/구매 필요 (비용/시간)
- 복잡한 SDK 통합
- 성능 최적화 필요

**예상 시간**: 
- 모델 준비: 1-2주 (외주) 또는 $200-500 (구매)
- SDK 통합: 6-8시간
- 애니메이션 연동: 4-6시간
- **총 소요**: 2-3주

---

### **Option B: 플레이스홀더 애니메이션 (GIF/WebM)** ✅ 빠른 시작
**장점**:
- 즉시 구현 가능 (< 2시간)
- 낮은 복잡도
- 90% 비주얼 효과 달성

**단점**:
- 실시간 상호작용 불가
- 파일 크기 큰 편
- "진짜" Live2D가 아님

**예상 시간**:
- 애니메이션 GIF/WebM 준비: 1시간
- 상태별 플레이스홀더 구현: 1시간
- **총 소요**: 2시간

---

### **Option C: 하이브리드 접근 (단계별 구현)** 🎯 추천
**장점**:
- 즉시 데모 가능 (Option B)
- 추후 실제 Live2D로 교체 (Option A)
- 리스크 분산

**단점**:
- 중복 작업 일부 발생

**예상 시간**:
- Phase 1 (플레이스홀더): 2시간
- Phase 2 (실제 Live2D): 2-3주
- **총 소요**: 2시간 + 2-3주

---

## 📐 Option A 상세 구현 계획 (완전 통합)

### **Step 1: Live2D 모델 준비 (1-2주)**

#### **방법 1: 외주 제작** (권장)
**플랫폼**:
- [Live2D公式クリエイター募集](https://www.live2d.com/creator/)
- Fiverr: "Live2D Character" 검색
- BOOTH (일본): Live2D 모델 판매

**스펙 요청사항**:
```yaml
model_specs:
  resolution: 280x320px (Desktop), 140x160px (Mobile)
  format: Live2D Cubism 4.x (최신)
  textures: PNG, 2048x2048 이하
  animations:
    - idle: 2-3초 루프 (깜빡임, 호흡)
    - listening: 1.5초 고개 끄덕임
    - thinking: 반복 시선 이동 (좌→우→좌)
    - speaking: 립싱크 (모음 a/i/u/e/o)
    - busy: idle + 노란 Glow (후처리)
  parameters:
    - ParamAngleX: -30 ~ 30 (고개 좌우)
    - ParamAngleY: -30 ~ 30 (고개 상하)
    - ParamEyeLOpen/ParamEyeROpen: 0 ~ 1 (눈 깜빡임)
    - ParamMouthOpenY: 0 ~ 1 (입 열림)
  file_structure:
    - model.moc3 (모델 데이터)
    - model.model3.json (설정 파일)
    - textures/ (PNG 이미지들)
    - motions/ (motion3.json 파일들)
```

**예산**:
- 기본 모델: $200-400
- 커스텀 디자인: $500-1000
- 5개 애니메이션 포함

**납기**: 1-2주

---

#### **방법 2: 기존 모델 구매/라이선스**
**추천 사이트**:
- [BOOTH](https://booth.pm/ko/search/Live2D): 일본 최대 Live2D 마켓
- [ArtStation](https://www.artstation.com/marketplace/game-dev/characters/2d): 2D 캐릭터
- [Unity Asset Store](https://assetstore.unity.com/): Live2D 패키지

**검색 키워드**:
```
- "Live2D Cubism model ready"
- "Live2D character commercial license"
- "Live2D assistant character"
```

**주의사항**:
- ✅ 상업용 라이선스 확인 필수
- ✅ Cubism 4.x 버전 확인
- ✅ 애니메이션 모션 포함 여부
- ✅ 파라미터 개수 (최소 10개 이상)

---

### **Step 2: Live2D SDK 통합 (6-8시간)**

#### **2.1 SDK 설치**

**방법 1: npm 패키지** (권장)
```bash
cd /home/user/webapp/frontend
npm install --save pixi-live2d-display
npm install --save pixi.js
```

**방법 2: CDN**
```html
<!-- Live2D Cubism SDK for Web -->
<script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.5.0/dist/index.min.js"></script>
```

---

#### **2.2 기본 통합 코드**

**파일 위치**: `/home/user/webapp/frontend/src/lib/live2d.ts`

```typescript
// live2d.ts
import * as PIXI from 'pixi.js';
import { Live2DModel } from 'pixi-live2d-display';

// Live2D 모델 타입
export type Live2DState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'busy';

// Live2D 매니저 클래스
export class Live2DManager {
  private app: PIXI.Application;
  private model: Live2DModel | null = null;
  private currentState: Live2DState = 'idle';
  private container: HTMLElement;

  constructor(containerId: string) {
    this.container = document.getElementById(containerId)!;
    
    // PIXI Application 초기화
    this.app = new PIXI.Application({
      width: 280,
      height: 320,
      transparent: true,
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
    });

    this.container.appendChild(this.app.view as HTMLCanvasElement);
  }

  // 모델 로드
  async loadModel(modelPath: string): Promise<void> {
    try {
      this.model = await Live2DModel.from(modelPath);
      
      // 모델 크기 조정
      this.model.scale.set(0.5);
      this.model.position.set(140, 160);
      
      // 스테이지에 추가
      this.app.stage.addChild(this.model);
      
      // 기본 상태 설정
      this.setState('idle');
      
      console.log('Live2D model loaded successfully');
    } catch (error) {
      console.error('Failed to load Live2D model:', error);
      throw error;
    }
  }

  // 상태 전환
  setState(state: Live2DState): void {
    if (!this.model) {
      console.warn('Model not loaded yet');
      return;
    }

    this.currentState = state;

    // 모션 재생
    switch (state) {
      case 'idle':
        this.model.motion('idle', 0, PIXI.Live2DMotionPriority.IDLE);
        break;
      
      case 'listening':
        this.model.motion('listening', 0, PIXI.Live2DMotionPriority.NORMAL);
        break;
      
      case 'thinking':
        this.model.motion('thinking', 0, PIXI.Live2DMotionPriority.NORMAL);
        break;
      
      case 'speaking':
        this.model.motion('speaking', 0, PIXI.Live2DMotionPriority.FORCE);
        break;
      
      case 'busy':
        // Busy는 Idle + Glow (CSS로 처리)
        this.model.motion('idle', 0, PIXI.Live2DMotionPriority.IDLE);
        this.container.setAttribute('data-status', 'busy');
        break;
    }

    console.log(`Live2D state changed: ${state}`);
  }

  // 립싱크 (음성 입력 시)
  startLipSync(audioContext: AudioContext): void {
    // TODO: 음성 입력 분석 → 립싱크 파라미터 업데이트
    // 현재는 Speaking 애니메이션으로 대체
    this.setState('speaking');
  }

  // 마우스 추적 (선택 사항)
  enableMouseTracking(): void {
    if (!this.model) return;

    this.container.addEventListener('mousemove', (e) => {
      const rect = this.container.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2; // -1 ~ 1
      const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2; // -1 ~ 1

      // 파라미터 업데이트 (고개 방향)
      this.model!.internalModel.coreModel.setParameterValueById(
        'ParamAngleX',
        x * 30 // -30 ~ 30도
      );
      this.model!.internalModel.coreModel.setParameterValueById(
        'ParamAngleY',
        y * 30
      );
    });
  }

  // 정리
  destroy(): void {
    if (this.model) {
      this.app.stage.removeChild(this.model);
      this.model.destroy();
    }
    this.app.destroy(true, { children: true });
  }
}
```

---

#### **2.3 페이지별 통합 예시**

**파일 위치**: `/home/user/webapp/frontend/src/pages/landing.ts`

```typescript
// landing.ts
import { Live2DManager } from '../lib/live2d';

// 페이지 로드 시
document.addEventListener('DOMContentLoaded', async () => {
  const live2d = new Live2DManager('live2d-container');

  try {
    // 모델 로드
    await live2d.loadModel('/models/nexus-assistant/model.model3.json');
    
    // 마우스 추적 활성화
    live2d.enableMouseTracking();
    
    // 페이지 스크롤에 따라 상태 변경
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      
      if (scrollY < 500) {
        live2d.setState('idle');
      } else if (scrollY < 1000) {
        live2d.setState('listening');
      } else if (scrollY < 1500) {
        live2d.setState('thinking');
      } else {
        live2d.setState('speaking');
      }
    });
  } catch (error) {
    console.error('Failed to initialize Live2D:', error);
    // 폴백: 플레이스홀더 표시
    showPlaceholder();
  }
});

function showPlaceholder() {
  const container = document.getElementById('live2d-container')!;
  container.innerHTML = `
    <div class="live2d-placeholder">
      <img src="/images/character-idle.gif" alt="NEXUS Assistant" />
    </div>
  `;
}
```

---

### **Step 3: 페이지별 상태 연동 (4-6시간)**

#### **페이지별 Live2D 상태 매핑**

| 페이지 | 초기 상태 | 인터랙션 | 비고 |
|--------|-----------|----------|------|
| **Landing (/)** | `idle` | 스크롤 시 상태 변경 | Hero에서 `listening` 전환 |
| **Intro (/intro)** | `listening` | 섹션별 상태 변경 | "Why NEXUS?" 읽는 느낌 |
| **Modules (/modules)** | `speaking` | 모듈 카드 호버 시 반응 | 모듈 소개하는 느낌 |
| **Pricing (/pricing)** | `thinking` | 플랜 선택 시 `idle` | 가격 고민하는 느낌 |
| **Dashboard (/dashboard-preview)** | `busy` | SSE 이벤트 시뮬레이션 | 작업 중인 느낌 |
| **Canvas (/canvas-preview)** | `thinking` | 편집 시 `speaking` | 제안하는 느낌 |
| **Login (/login)** | `idle` | 입력 시 `listening` | 인사하는 느낌 |

---

#### **SSE 이벤트 연동 (실제 서비스)**

```typescript
// sse-live2d-sync.ts
import { Live2DManager } from '../lib/live2d';

export function connectSSEToLive2D(live2d: Live2DManager) {
  const eventSource = new EventSource('/agent/reports/stream');

  eventSource.addEventListener('task.created', (e) => {
    live2d.setState('listening');
    console.log('Task created, character listening...');
  });

  eventSource.addEventListener('task.thinking', (e) => {
    live2d.setState('thinking');
    console.log('LLM generating response...');
  });

  eventSource.addEventListener('task.speaking', (e) => {
    live2d.setState('speaking');
    console.log('Character speaking...');
  });

  eventSource.addEventListener('task.completed', (e) => {
    live2d.setState('idle');
    console.log('Task completed, back to idle');
  });

  eventSource.addEventListener('approval.required', (e) => {
    live2d.setState('busy'); // RED approval - Glow
    console.log('Approval required!');
  });

  eventSource.onerror = () => {
    console.error('SSE connection lost');
    live2d.setState('idle');
  };

  return eventSource;
}
```

---

### **Step 4: 성능 최적화 (2-3시간)**

#### **4.1 모바일 반응형**

```css
/* live2d.css */
#live2d-container {
  position: fixed;
  z-index: 1000;
  
  /* Desktop: 우측 상단 */
  @media (min-width: 1024px) {
    top: 20px;
    right: 20px;
    width: 280px;
    height: 320px;
  }
  
  /* Mobile: 하단 우측, 50% 축소 */
  @media (max-width: 1023px) {
    bottom: 20px;
    right: 20px;
    width: 140px;
    height: 160px;
  }
  
  /* GPU 가속 */
  will-change: transform;
  transform: translateZ(0);
}

/* Busy 상태 Glow */
#live2d-container[data-status="busy"] {
  filter: drop-shadow(0 0 20px rgba(234, 179, 8, 0.6));
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  #live2d-container {
    animation: none !important;
  }
}
```

---

#### **4.2 로딩 최적화**

```typescript
// lazy-load-live2d.ts
export async function lazyLoadLive2D(containerId: string) {
  // Intersection Observer로 뷰포트 진입 시 로드
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(async (entry) => {
      if (entry.isIntersecting) {
        // 동적 import로 번들 사이즈 절감
        const { Live2DManager } = await import('../lib/live2d');
        const live2d = new Live2DManager(containerId);
        await live2d.loadModel('/models/nexus-assistant/model.model3.json');
        observer.disconnect();
      }
    });
  });

  const container = document.getElementById(containerId);
  if (container) {
    observer.observe(container);
  }
}
```

---

#### **4.3 60fps 유지**

```typescript
// performance-monitor.ts
export function monitorLive2DPerformance(live2d: Live2DManager) {
  let frameCount = 0;
  let lastTime = performance.now();

  function checkFPS() {
    frameCount++;
    const currentTime = performance.now();
    
    if (currentTime >= lastTime + 1000) {
      const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
      
      // FPS < 30이면 품질 하락
      if (fps < 30) {
        console.warn(`Low FPS detected: ${fps}fps, reducing quality...`);
        reduceQuality();
      }
      
      frameCount = 0;
      lastTime = currentTime;
    }
    
    requestAnimationFrame(checkFPS);
  }

  checkFPS();
}

function reduceQuality() {
  // 텍스처 해상도 하락 또는 애니메이션 비활성화
  const container = document.getElementById('live2d-container')!;
  container.style.display = 'none'; // 극단적 케이스
}
```

---

## 📐 Option B 상세 구현 계획 (플레이스홀더)

### **Step 1: 애니메이션 GIF/WebM 준비 (1시간)**

#### **필요한 파일 (5개)**
```
/public/images/character/
├── idle.webm (또는 .gif)          # 2-3초 루프
├── listening.webm                 # 1.5초 고개 끄덕임
├── thinking.webm                  # 좌우 시선 이동
├── speaking.webm                  # 입 움직임
└── busy.webm                      # idle + 노란 Glow
```

#### **제작 방법**
1. **AI 생성** (추천):
   - [RunwayML](https://runwayml.com/): "AI character animation"
   - [Synthesia](https://www.synthesia.io/): "Avatar animation"
   - Midjourney → Animated by Runway

2. **일러스트 + After Effects**:
   - 정적 캐릭터 일러스트 (PNG)
   - After Effects로 미세 애니메이션
   - WebM으로 export

3. **무료 리소스**:
   - [Mixamo](https://www.mixamo.com/): 3D 캐릭터 → 2D 렌더링
   - [LottieFiles](https://lottiefiles.com/): JSON 애니메이션

---

### **Step 2: 플레이스홀더 구현 (1시간)**

**파일 위치**: `/home/user/webapp/frontend/src/lib/live2d-placeholder.ts`

```typescript
// live2d-placeholder.ts
export type Live2DState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'busy';

export class Live2DPlaceholder {
  private container: HTMLElement;
  private videoElement: HTMLVideoElement;
  private currentState: Live2DState = 'idle';

  constructor(containerId: string) {
    this.container = document.getElementById(containerId)!;
    this.videoElement = document.createElement('video');
    this.videoElement.className = 'live2d-video';
    this.videoElement.loop = true;
    this.videoElement.muted = true;
    this.videoElement.autoplay = true;
    this.videoElement.playsInline = true; // 모바일 inline 재생
    
    this.container.appendChild(this.videoElement);
    
    // 기본 상태 설정
    this.setState('idle');
  }

  setState(state: Live2DState): void {
    this.currentState = state;
    const videoPath = `/images/character/${state}.webm`;
    
    // 비디오 소스 변경
    this.videoElement.src = videoPath;
    this.videoElement.play().catch(err => {
      console.warn('Failed to play video:', err);
      // 폴백: 정적 이미지
      this.showStaticImage(state);
    });

    // Busy 상태 Glow
    if (state === 'busy') {
      this.container.setAttribute('data-status', 'busy');
    } else {
      this.container.removeAttribute('data-status');
    }

    console.log(`Live2D placeholder state: ${state}`);
  }

  private showStaticImage(state: Live2DState): void {
    // 비디오 재생 실패 시 정적 이미지로 폴백
    const img = document.createElement('img');
    img.src = `/images/character/${state}.png`;
    img.alt = `NEXUS Assistant - ${state}`;
    this.container.innerHTML = '';
    this.container.appendChild(img);
  }

  destroy(): void {
    this.videoElement.pause();
    this.videoElement.src = '';
    this.container.innerHTML = '';
  }
}
```

---

### **Step 3: 페이지별 적용 (30분)**

**파일 위치**: `/home/user/webapp/backend/nexus_supervisor/public_pages_v2.py` (수정)

```python
# Hero Section에 Live2D 컨테이너 추가
def render_landing_page(lang: str = 'ko') -> str:
    return f'''
<!DOCTYPE html>
<html lang="{lang}">
<head>
    <!-- ... 기존 head ... -->
    <script type="module">
        import {{ Live2DPlaceholder }} from '/static/js/live2d-placeholder.js';
        
        document.addEventListener('DOMContentLoaded', () => {{
            const live2d = new Live2DPlaceholder('live2d-container');
            
            // 스크롤 이벤트
            window.addEventListener('scroll', () => {{
                const scrollY = window.scrollY;
                if (scrollY < 500) live2d.setState('idle');
                else if (scrollY < 1000) live2d.setState('listening');
                else live2d.setState('thinking');
            }});
        }});
    </script>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero-world-class">
        <!-- Live2D Container -->
        <div id="live2d-container" class="live2d-character">
            <!-- 플레이스홀더 비디오/이미지 들어갈 위치 -->
        </div>
        
        <!-- Hero Content -->
        <div class="hero-content">
            <h1>Your AI Character Assistant<br>That Never Sleeps</h1>
            <!-- ... -->
        </div>
    </section>
</body>
</html>
    '''
```

---

## 🎯 Option C 하이브리드 구현 계획 (추천)

### **Phase 1: 즉시 플레이스홀더 구현 (2시간)**
✅ Option B 전체 구현
- 5개 애니메이션 GIF/WebM 준비
- 페이지별 상태 연동
- **즉시 데모 가능**

### **Phase 2: 실제 Live2D 준비 (병행, 1-2주)**
⏳ Live2D 모델 제작/구매
- 외주 발주 또는 마켓플레이스 구매
- 애니메이션 5개 제작
- 라이선스 확보

### **Phase 3: Live2D SDK 교체 (6-8시간)**
⏳ Option A 전체 구현
- SDK 통합
- 플레이스홀더 → 실제 모델 교체
- 성능 최적화

---

## 📊 각 옵션 비교표

| 항목 | Option A (완전) | Option B (플레이스홀더) | Option C (하이브리드) |
|------|-----------------|-------------------------|------------------------|
| **즉시 데모** | ❌ (2-3주 후) | ✅ (2시간 내) | ✅ (2시간 내) |
| **프리미엄 경험** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (최종) |
| **개발 시간** | 2-3주 | 2시간 | 2시간 + 2-3주 |
| **비용** | $200-500 | $0-50 | $200-500 |
| **기술 복잡도** | 높음 | 낮음 | 중간 |
| **상호작용** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ (최종) |
| **유지보수** | 중간 | 쉬움 | 중간 |

---

## 🚀 즉시 실행 계획 (Option C 권장)

### **오늘 (2026-02-04) - 2시간**
1. ✅ 애니메이션 GIF 5개 준비 (AI 생성 또는 무료 리소스)
2. ✅ `Live2DPlaceholder` 클래스 구현
3. ✅ 7개 페이지에 플레이스홀더 적용
4. ✅ 테스트 & 배포

**산출물**:
- `/home/user/webapp/public/images/character/` (5개 파일)
- `/home/user/webapp/frontend/src/lib/live2d-placeholder.ts`
- 7개 페이지 Live2D 플레이스홀더 작동

---

### **이번 주 (2026-02-05 ~ 2026-02-07) - 모델 준비**
1. ⏳ Live2D 모델 외주 발주 (Fiverr/BOOTH)
2. ⏳ 스펙 전달 (위 `model_specs` 참고)
3. ⏳ 1차 검수 (Idle 애니메이션)

---

### **다음 주 (2026-02-10 ~ 2026-02-14) - SDK 통합**
1. ⏳ Live2D SDK 설치 (`pixi-live2d-display`)
2. ⏳ `Live2DManager` 클래스 구현
3. ⏳ 플레이스홀더 → 실제 모델 교체
4. ⏳ 성능 최적화 (60fps)
5. ⏳ 최종 테스트 & 배포

---

## 📝 필요한 리소스

### **Option A (완전 통합)**
- Live2D 모델 파일 (.moc3, .model3.json)
- 애니메이션 모션 파일 (5개 .motion3.json)
- 텍스처 이미지 (PNG)
- Live2D Cubism SDK for Web (무료)

### **Option B (플레이스홀더)**
- 애니메이션 GIF 또는 WebM (5개)
- 또는 정적 PNG 이미지 (5개)

### **Option C (하이브리드)**
- Option B 리소스 (즉시)
- Option A 리소스 (추후)

---

## 🎯 교수님께 질문

**이 중 어떤 옵션으로 진행하시겠습니까?**

### **Option A**: 완전 Live2D 통합 (2-3주 소요, 프리미엄)
- 외주 발주 또는 모델 구매 필요
- 완벽한 브랜드 경험
- 시간 투자 필요

### **Option B**: 플레이스홀더만 (2시간 소요, 빠름) ⚡
- 즉시 데모 가능
- 90% 비주얼 효과
- 향후 교체 가능

### **Option C**: 하이브리드 (2시간 + 2-3주, 추천) ⭐
- 즉시 플레이스홀더로 시작
- 병행하여 실제 모델 준비
- 단계적 업그레이드

---

**교수님, 결정해 주시면 바로 시작하겠습니다!**

---

**문서 위치**: `/home/user/webapp/docs/LIVE2D_INTEGRATION_PLAN_2026-02-04.md`  
**GitHub**: https://github.com/multipia-creator/nexus-on  
**작성일**: 2026-02-04
