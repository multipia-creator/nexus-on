# NEXUS Frontend 배포 가이드

**작성일**: 2026-02-03  
**버전**: v2.0  
**대상**: Frontend 웹앱 배포 (백엔드 없이 데모 모드 지원)

---

## 📦 배포 패키징 완료 항목

- [x] Dockerfile (Multi-stage build)
- [x] nginx.conf (SPA fallback 포함)
- [x] .dockerignore (최적화)
- [x] Docker 빌드/실행 스크립트 (`package.json`)
- [x] Cloudflare Pages 설정 (`wrangler.jsonc`)
- [x] README 배포 가이드 섹션 추가
- [x] 데모 모드 환경 변수 지원

---

## 🚀 배포 방식 3가지

### 1️⃣ Cloudflare Pages (권장)

**장점**: 무료, 빠른 글로벌 CDN, 환경 변수 관리 용이, SPA 라우팅 자동 지원

#### **단계별 배포**:

```bash
# 1. 빌드
cd /home/user/webapp/frontend
npm run build

# 2. Wrangler 설치 및 로그인
npm install -g wrangler
wrangler login

# 3. Pages 프로젝트 생성
wrangler pages project create nexus-frontend --production-branch main

# 4. 배포 (데모 모드)
wrangler pages deploy dist --project-name nexus-frontend

# 5. 환경 변수 설정 (데모 모드)
wrangler pages secret put VITE_DEMO_MODE --project-name nexus-frontend
# 입력: true

# 6. 환경 변수 설정 (프로덕션 - 실제 백엔드)
wrangler pages secret put VITE_API_BASE --project-name nexus-frontend
# 입력: https://api.yourdomain.com
```

#### **배포 URL**:
- Production: `https://nexus-frontend.pages.dev`
- Branch: `https://main.nexus-frontend.pages.dev`

#### **데모 모드 검증**:
1. https://nexus-frontend.pages.dev 접속
2. 브라우저 DevTools → Network 탭 → API 호출 없음 확인
3. SSE Mock 스트림 동작 확인 (Console에 "🎭 [DEMO]" 로그)
4. Devices 버튼 클릭 → 3개 Mock 디바이스 표시 확인

---

### 2️⃣ Docker + Nginx

**장점**: 자체 서버 배포, 완전한 환경 제어, K8s/ECS 호환

#### **로컬 테스트**:

```bash
cd /home/user/webapp/frontend

# 이미지 빌드
docker build -t nexus-frontend:latest .

# 데모 모드로 실행
docker run -p 8080:80 -e VITE_DEMO_MODE=true nexus-frontend:latest

# 접속: http://localhost:8080
```

#### **프로덕션 배포 (Docker Compose)**:

`docker-compose.yml`:
```yaml
version: '3.8'
services:
  frontend:
    image: nexus-frontend:latest
    ports:
      - "80:80"
    environment:
      - VITE_DEMO_MODE=true  # 데모 모드
      # - VITE_API_BASE=https://api.yourdomain.com  # 실제 백엔드 URL
    restart: unless-stopped
```

실행:
```bash
docker-compose up -d
```

#### **검증**:
```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs <container_id>

# 접속 테스트
curl http://localhost:8080
```

---

### 3️⃣ Vercel/Netlify

**장점**: GitHub 연동 자동 배포, 무료 티어, Zero Config

#### **Vercel 배포**:

```bash
# CLI 설치
npm install -g vercel

# 배포
cd /home/user/webapp/frontend
vercel --prod
```

**환경 변수** (Vercel Dashboard):
- `VITE_DEMO_MODE=true` (데모 모드)
- `VITE_API_BASE=https://api.yourdomain.com` (프로덕션)

#### **Netlify 배포**:

```bash
# CLI 설치
npm install -g netlify-cli

# 배포
cd /home/user/webapp/frontend
npm run build
netlify deploy --prod --dir=dist
```

**환경 변수** (Netlify Dashboard):
- `VITE_DEMO_MODE=true`
- `VITE_API_BASE=https://api.yourdomain.com`

---

## 🔐 배포 체크리스트

### **데모 모드 배포**:
- [ ] `npm run build` 성공 (0 errors)
- [ ] `VITE_DEMO_MODE=true` 환경 변수 설정
- [ ] 빌드 결과 `dist/` 디렉토리 생성 확인
- [ ] 배포 후 브라우저 DevTools Network 탭에서 API 호출 없음 확인
- [ ] SSE Mock 스트림 동작 (Console에 "🎭 [DEMO]" 로그)
- [ ] Devices Mock 데이터 (3개 디바이스) 표시 확인
- [ ] UI 모든 기능 동작 확인 (AssistantStage, Dashboard, Sidecar)

### **프로덕션 모드 배포**:
- [ ] Backend API 배포 완료 (HTTPS 필수)
- [ ] Backend CORS 설정 (`CORS_ORIGINS`에 프론트엔드 도메인 추가)
- [ ] `VITE_API_BASE` 환경 변수에 Backend URL 설정
- [ ] SSE 연결 테스트 (`/agent/reports/stream`)
- [ ] Device Pairing 흐름 End-to-End 테스트
- [ ] HTTPS 사용 (Cloudflare/Vercel/Netlify는 자동 지원)

---

## 📊 배포 파일 구조

### **빌드 결과** (`frontend/dist/`):
```
dist/
├── index.html              # 메인 HTML (엔트리 포인트)
├── assets/
│   ├── index-{hash}.js     # 번들된 JavaScript
│   └── index-{hash}.css    # 번들된 CSS
└── vite.svg                # Favicon
```

### **Docker 이미지 구조**:
```
/usr/share/nginx/html/
├── index.html
├── assets/
│   ├── index-{hash}.js
│   └── index-{hash}.css
└── vite.svg

/etc/nginx/conf.d/default.conf  # Nginx 설정 (SPA fallback)
```

---

## 🐛 트러블슈팅

### **문제 1: "404 Not Found" (SPA 라우팅)**

**증상**: `/dashboard` 경로 직접 접속 시 404 에러

**원인**: SPA 라우팅이 설정되지 않음

**해결**:
- **Cloudflare Pages**: 자동 지원 (설정 불필요)
- **Docker + Nginx**: `nginx.conf`에 `try_files $uri $uri/ /index.html;` 추가됨 (이미 완료)
- **Vercel/Netlify**: `vercel.json` 또는 `_redirects` 파일 추가:

`vercel.json`:
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

`_redirects` (Netlify):
```
/*    /index.html   200
```

---

### **문제 2: 환경 변수가 적용되지 않음**

**증상**: `VITE_DEMO_MODE=true` 설정했는데 실제 API 호출 발생

**원인**: Vite 환경 변수는 **빌드 시점**에 번들에 임베드됨

**해결**:
1. 환경 변수를 설정한 후 **반드시 재빌드**:
   ```bash
   npm run build
   ```
2. Docker의 경우 **빌드 시점**에 `ARG`로 주입:
   ```dockerfile
   ARG VITE_DEMO_MODE=true
   ENV VITE_DEMO_MODE=$VITE_DEMO_MODE
   RUN npm run build
   ```

---

### **문제 3: CORS 에러**

**증상**: 브라우저 Console에 "CORS policy" 에러

**원인**: Backend에서 Frontend 도메인을 허용하지 않음

**해결**:
1. Backend `CORS_ORIGINS` 환경 변수에 프론트엔드 도메인 추가:
   ```bash
   export CORS_ORIGINS="https://nexus-frontend.pages.dev,http://localhost:5173"
   ```
2. Backend 재시작

---

### **문제 4: 빌드 실패 ("Cannot find module")**

**증상**: `npm run build` 실패, "Cannot find module 'xxx'"

**원인**: 의존성 미설치

**해결**:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 🎯 권장 배포 전략

### **단계별 배포 전략**:

1. **Phase 1: 데모 모드 배포 (즉시 가능)**
   - Cloudflare Pages 배포
   - `VITE_DEMO_MODE=true` 설정
   - Backend 불필요
   - 목적: SaaS 데모, 프레젠테이션, 유저 피드백 수집

2. **Phase 2: Backend 개발 병행**
   - Backend FastAPI 개발 (SSE, Device API)
   - 로컬 테스트 (`http://localhost:8000`)
   - Frontend `VITE_DEMO_MODE=false` 모드로 연동 테스트

3. **Phase 3: 프로덕션 배포**
   - Backend 배포 (AWS/GCP/Cloudflare Workers)
   - Frontend `VITE_API_BASE` 설정
   - HTTPS, CORS, 환경 변수 설정
   - Device Pairing 흐름 End-to-End 테스트

---

## 📚 참고 문서

- [NEXUS_DEMO_MODE_GUIDE.md](./NEXUS_DEMO_MODE_GUIDE.md) - 데모 모드 상세 가이드
- [README.md](../README.md) - 프로젝트 전체 가이드
- [NEXUS_V2_SETUP_CHECKLIST.md](./NEXUS_V2_SETUP_CHECKLIST.md) - 실행 체크리스트

---

## 📞 문의 및 지원

- **프로젝트 관리자**: 남현우 교수
- **도메인**: nexus
- **Git 저장소**: `/home/user/webapp/.git`
- **문서 위치**: `/home/user/webapp/docs/`

---

**배포 완료 후 다음 단계**:
1. ✅ Frontend 배포 완료 (Cloudflare Pages / Docker / Vercel)
2. ⏳ Backend 개발 및 배포 (선택)
3. ⏳ Device Pairing 흐름 End-to-End 테스트
4. ⏳ 프로덕션 환경 설정 (HTTPS, CORS, 환경 변수)
