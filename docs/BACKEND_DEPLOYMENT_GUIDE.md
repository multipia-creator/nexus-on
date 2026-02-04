# NEXUS-ON 백엔드 배포 가이드

**작성일**: 2026-02-04  
**대상**: 백엔드 마케팅 사이트 (FastAPI + 마케팅 페이지)

---

## **배포 상황**

- **프론트엔드**: ✅ Cloudflare Pages 배포 완료 (https://webapp-zrq.pages.dev/)
- **백엔드**: ⏳ 로컬에서만 실행 중 (http://localhost:8000/)
- **목표**: 백엔드 마케팅 사이트를 외부에서 접근 가능하도록 배포

---

## **배포 옵션 3가지**

### **Option A: Render.com (권장) ⭐**

**장점**:
- 무료 플랜 제공 (750시간/월)
- Docker 지원
- 자동 배포 (GitHub 연동)
- PostgreSQL, Redis 무료 제공
- HTTPS 자동

**단점**:
- 무료 플랜은 15분 비활성 후 슬립
- 콜드 스타트 약 30초

**배포 단계**:
```bash
# 1. Render.com 계정 생성
# https://render.com/

# 2. GitHub 저장소 연결
# Dashboard → New → Web Service → Connect GitHub

# 3. 설정
Service Name: nexus-backend
Branch: main
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn nexus_supervisor.app:app --host 0.0.0.0 --port 8000

# 4. 환경 변수 설정 (Environment Variables)
NEXUS_API_KEY=your-secret-key
REDIS_URL=redis://red-xxxxx:6379
ANTHROPIC_API_KEY=your-anthropic-key
```

**예상 URL**: `https://nexus-backend.onrender.com/`

---

### **Option B: Railway.app**

**장점**:
- 매우 간단한 배포
- 무료 $5 크레딧/월
- Docker, Redis, PostgreSQL 지원
- GitHub 연동
- HTTPS 자동

**단점**:
- 무료 크레딧 소진 후 유료
- 약 $10/월

**배포 단계**:
```bash
# 1. Railway 계정 생성
# https://railway.app/

# 2. GitHub 저장소 연결
# New Project → Deploy from GitHub

# 3. 설정
Root Directory: backend
Start Command: uvicorn nexus_supervisor.app:app --host 0.0.0.0 --port $PORT

# 4. 환경 변수 설정
NEXUS_API_KEY=your-secret-key
REDIS_URL=${{Redis.REDIS_URL}}  # Railway 자동 주입
ANTHROPIC_API_KEY=your-anthropic-key
```

**예상 URL**: `https://nexus-backend-production.up.railway.app/`

---

### **Option C: Fly.io**

**장점**:
- 무료 플랜 (3개 VM, 256MB RAM)
- Docker Native
- 글로벌 엣지 배포
- PostgreSQL, Redis 제공

**단점**:
- CLI 필수
- 약간 복잡한 설정

**배포 단계**:
```bash
# 1. Fly CLI 설치
curl -L https://fly.io/install.sh | sh

# 2. 로그인
fly auth login

# 3. 앱 생성
cd /home/user/webapp/backend
fly launch --name nexus-backend --region nrt

# 4. Redis 추가
fly redis create

# 5. 배포
fly deploy

# 6. 환경 변수 설정
fly secrets set NEXUS_API_KEY=your-secret-key
fly secrets set ANTHROPIC_API_KEY=your-anthropic-key
```

**예상 URL**: `https://nexus-backend.fly.dev/`

---

## **비교표**

| 항목 | Render.com | Railway.app | Fly.io |
|------|-----------|-------------|--------|
| **무료 플랜** | ✅ 750시간/월 | 💵 $5 크레딧/월 | ✅ 3 VM |
| **Redis** | ✅ 무료 | ✅ 무료 | ✅ 무료 |
| **Docker 지원** | ✅ | ✅ | ✅ |
| **GitHub 연동** | ✅ | ✅ | ⚠️ CLI |
| **콜드 스타트** | ~30초 | ~10초 | ~5초 |
| **HTTPS** | ✅ 자동 | ✅ 자동 | ✅ 자동 |
| **복잡도** | ⭐ 쉬움 | ⭐⭐ 중간 | ⭐⭐⭐ 어려움 |
| **추천도** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## **권장 사항**

### **즉시 시작: Option A (Render.com)** 🚀

**이유**:
1. 완전 무료 (슬립 모드만 단점)
2. GitHub 연동 자동 배포
3. 설정 매우 간단
4. Redis 무료 제공
5. 마케팅 사이트 용도로 충분

**배포 시간**: 약 15분

---

## **배포 후 작업**

### 1. 프론트엔드에서 백엔드 API 연결
```typescript
// frontend/src/devices/api.ts
const BACKEND_URL = 'https://nexus-backend.onrender.com'
```

### 2. CORS 설정 확인
```python
# backend/nexus_supervisor/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://webapp-zrq.pages.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 환경 변수 설정
- `NEXUS_API_KEY`
- `REDIS_URL` (Render 자동 제공)
- `ANTHROPIC_API_KEY` (선택)
- `YOUTUBE_API_KEY` (선택)

---

## **최소 배포 (마케팅 사이트만)**

마케팅 페이지만 먼저 배포하려면:

```bash
# 1. requirements.txt 최소화
fastapi==0.110.0
uvicorn[standard]==0.27.1
redis==5.0.1
pydantic==2.6.1

# 2. 환경 변수 최소화
NEXUS_API_KEY=demo-key-only
REDIS_URL=redis://localhost:6379  # 마케팅 페이지는 Redis 불필요

# 3. Start Command
uvicorn nexus_supervisor.app:app --host 0.0.0.0 --port 8000
```

---

## **다음 단계 선택**

교수님, 어떤 방식으로 진행할까요?

1. **Option A (Render.com)** - 지금 바로 배포 (15분)
2. **Option B (Railway.app)** - 더 빠른 성능 원하시면
3. **Option C (Fly.io)** - CLI 사용 편하시면
4. **나중에** - 로컬에서만 사용

추천: **Option A**로 즉시 배포하겠습니다! 👍
