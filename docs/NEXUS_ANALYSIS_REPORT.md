# NEXUS 프로젝트 분석 보고서

**작성일**: 2026-02-03  
**작성자**: Claude Code Agent  
**목적**: NEXUS AllInOne Archive v1 분석 및 Cloudflare Pages 통합 방안

---

## 📦 아카이브 구조

### 업로드된 파일
- **파일명**: `NEXUS_AllInOne_Archive_v1_20260203.zip` (80MB)
- **압축 해제 위치**: `/home/user/nexus_archive/`

### 핵심 컴포넌트

#### 1. **최종 런타임 (v7.7)**
- **위치**: `artifacts/NEXUS_Final_ClaudeSonnet45_LocalServer_v7.7.zip`
- **설명**: 로컬 상주형 캐릭터 비서 + 자율 에이전트 데모
- **기술 스택**:
  - Backend: **Python FastAPI** + Redis + RabbitMQ + PostgreSQL
  - LLM: Claude Sonnet 4.5, Gemini, OpenAI (멀티 게이트웨이)
  - UI: SSE 스트림 기반 단일 소스 업데이트
  - RAG: 로컬 미러 폴더 기반 인덱싱

#### 2. **추가 아티팩트** (28개 파일)
- 설계 문서, 시뮬레이션 팩, 통합본, 참고자료
- YouTube 통합, HWP 정규화, LLM 게이트웨이 등

---

## 🏗️ NEXUS 시스템 아키텍처 (v7.7 기준)

### A. **백엔드 구조** (Python FastAPI)

```
nexus_backend_p0/
├── nexus_supervisor/          # 메인 Supervisor (FastAPI)
│   ├── app.py                 # 메인 애플리케이션
│   ├── routers/               # API 라우터
│   │   ├── agent_reports.py  # SSE 스트림 (/agent/reports/stream)
│   │   ├── approvals.py       # Two-phase commit (/approvals/*)
│   │   ├── sidecar.py         # 사이드카 명령 (/sidecar/command)
│   │   └── health.py          # 헬스체크
│   └── services/              # 비즈니스 로직
│
├── agents/                    # 에이전트 워커들
│   ├── excel_kakao/           # 엑셀/카카오 처리 에이전트
│   └── youtube/               # YouTube 검색/재생 에이전트
│
├── shared/                    # 공통 라이브러리
│   ├── llm_client.py          # LLM 통합 클라이언트
│   ├── llm_router.py          # 멀티 LLM 라우팅
│   ├── task_store.py          # Redis 기반 태스크 저장소
│   ├── mq_utils.py            # RabbitMQ 유틸리티
│   ├── metrics.py             # Prometheus 메트릭
│   ├── errors.py              # 에러 택소노미
│   ├── security.py            # 보안/인증
│   └── ...
│
├── tools/                     # 운영 도구
│   ├── finops_report.py       # FinOps 리포트
│   ├── anomaly_watch.py       # 이상치 탐지
│   └── rehearsal_*.py         # 리허설 도구
│
├── docker/                    # Docker 설정
│   └── docker-compose.nexus.yml
│
└── requirements.txt           # Python 의존성
```

### B. **핵심 기능**

#### 1. SSE 스트림 기반 UI 업데이트
- **불변 계약**: UI 갱신의 단일 소스는 `/agent/reports/stream`
- **이벤트 타입**:
  - `snapshot`: 초기 상태
  - `report`: 상태 변경 알림
- **리플레이**: `Last-Event-ID` 또는 `cursor` 기반

#### 2. Two-Phase Commit (위험 작업)
- **RED 작업**: 외부 공유/전송은 승인 없이 실행 불가
- **프로세스**:
  1. 작업 요청 → `202 Accepted`
  2. Ask(승인 요청) 생성 → SSE로 UI 전달
  3. 사용자 승인 → `/approvals/{ask_id}/decide`
  4. 실행 완료 → SSE로 결과 전달

#### 3. 멀티 LLM 게이트웨이
- **지원 프로바이더**:
  - Anthropic (Claude Sonnet 4.5) - 기본
  - Google (Gemini)
  - OpenAI (GPT-4)
  - OpenRouter
  - ZAI (GLM-4.7)
- **Fallback 체인**: 실패 시 자동 폴백
- **Circuit Breaker**: Redis 기반 장애 격리
- **FinOps**: 실시간 비용 추적 및 예산 관리

#### 4. 관측성 & 운영
- **Prometheus 메트릭**: `/metrics` 엔드포인트
- **DLQ (Dead Letter Queue)**: 실패 메시지 재처리
- **Retry 정책**: 5s → 30s → 5m (총 3회)
- **보안**: API Key + HMAC 서명 + PII 마스킹

---

## ⚠️ Cloudflare Pages 호환성 분석

### **현재 NEXUS 백엔드의 한계**

NEXUS v7.7 백엔드는 **Cloudflare Pages에 직접 배포 불가능**합니다:

| 요구사항 | NEXUS v7.7 | Cloudflare Pages | 호환성 |
|---------|-----------|-----------------|--------|
| 런타임 | Python FastAPI | JavaScript/TypeScript Workers | ❌ 불가 |
| 데이터베이스 | PostgreSQL (로컬) | Cloudflare D1 (SQLite) | ❌ 불가 |
| 메시지 큐 | RabbitMQ | Workers Queue | ❌ 불가 |
| 캐시/저장소 | Redis | Cloudflare KV | ❌ 불가 |
| 장시간 프로세스 | 백그라운드 워커 | 10ms CPU 제한 | ❌ 불가 |
| SSE 스트림 | Long-running connection | Edge에서 제한적 | ⚠️ 제한적 |
| 파일 시스템 | 로컬 파일 읽기/쓰기 | 불가 | ❌ 불가 |

---

## 🎯 통합 전략 제안

### **전략 A: 하이브리드 아키텍처 (추천)**

```
┌─────────────────────────────────────────┐
│   Cloudflare Pages (프론트엔드)          │
│   - Next.js UI                          │
│   - Hono API 프록시 (BFF)                │
│   - 정적 자산 서빙                        │
└─────────────┬───────────────────────────┘
              │ HTTPS/WebSocket
              ↓
┌─────────────────────────────────────────┐
│   외부 백엔드 서버 (Python FastAPI)      │
│   - Heroku / Railway / Render           │
│   - 또는 VPS (Linode, DigitalOcean)     │
│   - NEXUS v7.7 그대로 실행              │
│   - PostgreSQL + Redis + RabbitMQ       │
└─────────────────────────────────────────┘
```

**장점**:
- NEXUS 백엔드를 수정 없이 그대로 사용
- Cloudflare Pages는 UI와 BFF만 담당
- 백엔드는 Python 생태계 그대로 활용

**단점**:
- 외부 서버 비용 발생
- 인프라 관리 필요

---

### **전략 B: Cloudflare 네이티브 재구현**

NEXUS의 핵심 기능을 Cloudflare 스택으로 재작성:

```
┌─────────────────────────────────────────┐
│   Cloudflare Pages (Hono + TypeScript)  │
│   - API 엔드포인트                       │
│   - D1 Database (SQLite)                │
│   - KV (캐시/세션)                      │
│   - Queues (비동기 작업)                 │
│   - Workers AI (선택)                   │
└─────────────────────────────────────────┘
```

**필요한 작업**:
1. **Python → TypeScript 포팅**
   - FastAPI → Hono
   - PostgreSQL → Cloudflare D1
   - Redis → Cloudflare KV
   - RabbitMQ → Cloudflare Queues

2. **기능 단순화**
   - SSE → Polling 또는 WebSocket (제한적)
   - 장시간 작업 → Queue Workers
   - 파일 저장 → R2 Storage

3. **LLM 통합**
   - 외부 API 호출 (OpenAI, Anthropic 등)
   - 토큰을 Cloudflare Secrets로 관리

**장점**:
- 완전한 서버리스 (비용 효율적)
- 글로벌 엣지 배포
- Cloudflare 생태계 활용

**단점**:
- 대규모 코드 재작성 필요 (수주~수개월)
- Python 라이브러리 포팅 어려움
- SSE 스트림 제한적

---

### **전략 C: 최소 MVP (빠른 프로토타입)**

NEXUS의 일부 기능만 Cloudflare Pages에 구현:

**구현 범위**:
- ✅ 기본 UI 레이아웃
- ✅ OpenAI/Anthropic API 직접 호출
- ✅ 간단한 대화 인터페이스
- ✅ D1 기반 대화 히스토리
- ❌ 복잡한 에이전트 로직
- ❌ RAG/YouTube 통합
- ❌ Two-phase commit

**장점**:
- 빠른 구현 (1~2주)
- Cloudflare Pages 완전 활용

**단점**:
- NEXUS 고급 기능 제외
- 단순 챗봇 수준

---

## 📋 권장 로드맵

### **Phase 1: 분석 및 의사결정 (1일)** ✅ 현재
1. [x] NEXUS 아카이브 분석 완료
2. [x] Cloudflare Pages 호환성 검토 완료
3. [ ] 교수님과 전략 논의 필요

### **Phase 2: 프로토타입 구현 (1주)**
**전략 A 선택 시**:
- Cloudflare Pages에 프론트엔드 + BFF 구현
- NEXUS 백엔드는 별도 서버에 배포

**전략 B 선택 시**:
- 핵심 API 엔드포인트부터 TypeScript로 포팅 시작

**전략 C 선택 시**:
- 기본 UI + OpenAI API 통합 MVP

### **Phase 3: 통합 및 테스트 (2주)**
- 선택한 전략에 따라 구현 완료
- 테스트 및 디버깅

---

## 💡 즉시 실행 가능한 옵션

### **옵션 1: 로컬에서 NEXUS v7.7 실행**
```bash
cd /home/user/nexus_archive/artifacts/nexus_v7.7/nexus_backend_p0
cp .env.example .env
# .env 파일 편집 (API 키 설정)
bash deploy/nexus_deploy.sh
```

- 포트: 8000 (Supervisor), 15672 (RabbitMQ)
- UI: http://localhost:8000/ui

### **옵션 2: Cloudflare Pages에 간단한 챗봇 MVP**
- 현재 `/home/user/webapp` 프로젝트에 구현
- OpenAI/Anthropic API 활용
- 1~2일 내 완성 가능

---

## 🤔 교수님께 드리는 질문

1. **배포 환경 선호도**:
   - A) Cloudflare Pages만 사용 (서버리스)
   - B) Cloudflare Pages + 외부 백엔드 서버 (하이브리드)
   - C) 로컬 개발 환경만 사용

2. **기능 범위**:
   - A) NEXUS v7.7 전체 기능 유지 (복잡)
   - B) 핵심 기능만 선택적 구현 (중간)
   - C) 간단한 AI 챗봇 MVP (단순)

3. **우선순위**:
   - 빠른 프로토타입 vs. 완전한 기능 구현
   - 비용 최소화 vs. 성능/기능 극대화

4. **Python 코드 활용**:
   - Python 백엔드를 별도 서버에 그대로 배포
   - TypeScript로 재작성
   - 핵심 로직만 참고

---

## 📚 참고 문서 위치

- **백엔드 레퍼런스**: `/home/user/webapp/docs/backend_reference/`
- **설계 문서**: `/home/user/webapp/docs/design/`
- **아카이브 README**: `/home/user/webapp/docs/ARCHIVE_README.md`

---

**다음 단계**: 교수님의 의견을 듣고 구체적인 구현 방향을 결정하겠습니다.
