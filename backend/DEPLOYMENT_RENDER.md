# 🚀 NEXUS Backend 배포 가이드 (Render.com)

> 작성일: 2026-02-05  
> 목적: Backend FastAPI 서버를 Render.com에 무료 배포

---

## 📋 사전 준비

1. **GitHub 계정** (이미 있음: https://github.com/multipia-creator/nexus-on)
2. **Render.com 계정** (무료 가입: https://render.com)
3. **배포 파일 준비 완료** ✅
   - `render.yaml` (자동 배포 설정)
   - `Procfile` (실행 명령)
   - `runtime.txt` (Python 3.12.11)
   - `requirements.txt` (의존성)

---

## 🎯 배포 단계

### Step 1: GitHub에 배포 파일 푸시 (자동 실행됨)

```bash
cd /home/user/webapp/backend
git add render.yaml Procfile runtime.txt
git commit -m "🚀 Add Render.com deployment config"
git push origin main
```

### Step 2: Render.com에서 서비스 생성

1. **Render.com 로그인**
   - https://render.com 접속
   - GitHub 계정으로 로그인

2. **New Web Service 생성**
   - Dashboard → "New +" → "Web Service"
   - Repository 선택: `multipia-creator/nexus-on`
   - Branch: `main`

3. **서비스 설정**
   ```
   Name: nexus-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: uvicorn nexus_supervisor.app:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **환경 변수 설정** (선택사항)
   ```
   PORT: (자동 생성)
   PYTHON_VERSION: 3.12.11
   
   # TTS API Keys (나중에 추가 가능)
   ELEVENLABS_API_KEY: (ElevenLabs API 키)
   GOOGLE_APPLICATION_CREDENTIALS: (Google Cloud 서비스 계정 JSON)
   
   # LLM API Keys (나중에 추가 가능)
   ANTHROPIC_API_KEY: (Claude API 키)
   OPENAI_API_KEY: (OpenAI API 키)
   GOOGLE_API_KEY: (Gemini API 키)
   ```

5. **Deploy 클릭**
   - 자동 빌드 시작 (~5-10분)
   - 배포 완료 후 URL 확인 (예: `https://nexus-backend.onrender.com`)

---

## ✅ 배포 확인

### Health Check
```bash
curl https://nexus-backend.onrender.com/health
```

**기대 응답:**
```json
{
  "status": "degraded",
  "time": "2026-02-05T04:45:28+00:00",
  "llm_provider": "gemini",
  "redis_ok": false,
  "rabbit_ok": false
}
```

### 마케팅 페이지 테스트
```bash
# Landing Page
curl https://nexus-backend.onrender.com/

# Intro Page
curl https://nexus-backend.onrender.com/intro

# Developer Profile
curl https://nexus-backend.onrender.com/developer
```

---

## 🔧 Frontend 연동

배포 완료 후, **Frontend의 BACKEND_URL을 업데이트**합니다:

```typescript
// /home/user/webapp/src/index.tsx
const BACKEND_URL = 'https://nexus-backend.onrender.com'
```

그 후 Frontend를 재배포:

```bash
cd /home/user/webapp
npm run build
npx wrangler pages deploy dist --project-name nexus-3bm
```

---

## 📊 배포 후 상태

| 항목 | 상태 | URL |
|------|------|-----|
| Backend (Render.com) | 🟡 배포 중 | https://nexus-backend.onrender.com |
| Frontend (Cloudflare) | ✅ 작동 | https://nexus-3bm.pages.dev |
| GitHub Repo | ✅ 최신 | https://github.com/multipia-creator/nexus-on |

---

## ⚠️ 주의사항

1. **무료 플랜 제한**
   - 15분 비활성 시 자동 슬립
   - 첫 요청 시 깨우기 (~30초 소요)
   - 750시간/월 무료 사용

2. **Redis/RabbitMQ**
   - 현재 미연결 상태 (`redis_ok: false`, `rabbit_ok: false`)
   - 필요 시 별도 설정 (Redis Labs, CloudAMQP)

3. **TTS API 키**
   - 배포 후 Render Dashboard에서 수동 추가
   - Environment → Add Environment Variable

---

## 🎉 완료 후 최종 URL

**프로덕션 URL:**
```
Frontend: https://nexus-3bm.pages.dev
Backend: https://nexus-backend.onrender.com
```

**테스트 페이지:**
- Landing: https://nexus-3bm.pages.dev/
- Intro: https://nexus-3bm.pages.dev/intro
- Developer: https://nexus-3bm.pages.dev/developer
- Live2D Test: https://nexus-3bm.pages.dev/live2d-test

---

## 📞 문제 해결

### 배포 실패 시
1. Render Dashboard → Logs 확인
2. 빌드 로그에서 에러 메시지 확인
3. requirements.txt 의존성 확인

### 503 에러 시
- 무료 플랜은 15분 후 슬립 모드
- 첫 요청 시 ~30초 대기 (자동 깨우기)

---

**작성자:** Claude AI  
**마지막 업데이트:** 2026-02-05
