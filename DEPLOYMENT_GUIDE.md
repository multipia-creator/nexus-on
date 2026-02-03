# 🚀 Cloudflare Pages 배포 가이드

## **1. 사전 준비**

### **Cloudflare API 키 설정**
1. Deploy 탭으로 이동
2. Cloudflare API 토큰 생성: https://dash.cloudflare.com/profile/api-tokens
   - Template: "Edit Cloudflare Workers"
   - Permissions: 
     - Account - Cloudflare Pages - Edit
     - Zone - Workers Routes - Edit
3. API 키를 Deploy 탭에 저장

### **환경 변수 설정**
```bash
export CLOUDFLARE_API_TOKEN="your-api-token-here"
```

---

## **2. 배포 명령**

### **Option A: Wrangler CLI (권장)**

```bash
cd /home/user/webapp/frontend

# 1. 빌드 (이미 완료)
npm run build

# 2. Cloudflare Pages 프로젝트 생성 (최초 1회만)
npx wrangler pages project create webapp \
  --production-branch main \
  --compatibility-date 2024-01-01

# 3. 배포
npx wrangler pages deploy dist --project-name webapp

# 4. 배포 URL 확인
# https://webapp.pages.dev
# 또는 https://main.webapp.pages.dev
```

### **Option B: Cloudflare Dashboard (수동)**

1. https://dash.cloudflare.com/pages 접속
2. "Create a project" 클릭
3. "Upload assets" 선택
4. `frontend/dist/` 폴더의 모든 파일을 업로드
5. 프로젝트 이름: `webapp`
6. "Deploy site" 클릭

---

## **3. 환경 변수 설정 (배포 후)**

Cloudflare Dashboard에서 환경 변수를 설정하세요:

```bash
# Production 환경
VITE_API_BASE=https://your-backend.com
```

또는 Wrangler CLI:

```bash
npx wrangler pages secret put VITE_API_BASE --project-name webapp
# 값 입력: https://your-backend.com
```

---

## **4. 커스텀 도메인 설정 (선택)**

```bash
npx wrangler pages domain add example.com --project-name webapp
```

---

## **5. 배포 확인**

### **Health Check**
```bash
# Frontend 접속
curl https://webapp.pages.dev

# API Base URL 확인 (브라우저 콘솔)
# import.meta.env.VITE_API_BASE
```

### **기능 테스트**
1. Dashboard 접속: https://webapp.pages.dev
2. Nodes 뷰 전환 (Dock 클릭)
3. 페어링 코드 생성 테스트
4. YouTube 검색 테스트 (Demo 모드)

---

## **6. Rollback (이전 버전으로 복구)**

```bash
# 배포 목록 확인
npx wrangler pages deployments list --project-name webapp

# 특정 배포로 롤백
npx wrangler pages rollback <deployment-id> --project-name webapp
```

---

## **7. 트러블슈팅**

### **문제 1: API 키 인증 실패**
```bash
# API 키 검증
npx wrangler whoami

# 예상 출력:
# Getting User settings...
# 👋 You are logged in with an API Token
```

### **문제 2: 빌드 파일 없음**
```bash
# 빌드 재실행
cd /home/user/webapp/frontend
npm run build

# dist/ 확인
ls -lh dist/
```

### **문제 3: CORS 오류**
- Backend API에 CORS 헤더 추가 필요
- `Access-Control-Allow-Origin: *` 또는 특정 도메인

### **문제 4: 환경 변수 미적용**
- Cloudflare Pages는 `VITE_*` 접두사 환경 변수만 클라이언트에 노출
- 빌드 시점에 주입되므로 변경 후 재빌드 필요

---

## **8. 자동 배포 설정 (CI/CD)**

### **GitHub Actions 예시**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: cd frontend && npm ci && npm run build
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: webapp
          directory: frontend/dist
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

---

## **9. 현재 상태**

### **빌드 완료**
- ✅ Frontend: `dist/` (196KB)
- ✅ Git 커밋: `bc499a9` - SaaS + Windows Node E2E 구현
- ✅ 백업: https://www.genspark.ai/api/files/s/ji1pPLeA

### **배포 대기**
- ⚠️ Cloudflare API 키 필요
- ⚠️ `setup_cloudflare_api_key` 실행 필요

---

## **10. 다음 단계**

1. **Deploy 탭에서 Cloudflare API 키 설정**
2. **`setup_cloudflare_api_key` 실행** (자동 환경 변수 설정)
3. **`npx wrangler pages deploy dist --project-name webapp` 실행**
4. **배포 URL 확인** (https://webapp.pages.dev)
5. **기능 테스트** (페어링, YouTube, RAG)

---

## **11. 참고 자료**

- Cloudflare Pages 문서: https://developers.cloudflare.com/pages/
- Wrangler CLI 문서: https://developers.cloudflare.com/workers/wrangler/
- Vite 환경 변수: https://vitejs.dev/guide/env-and-mode.html

---

**작성일**: 2026-02-03
**프로젝트**: webapp (SaaS + Windows Node)
**백업 URL**: https://www.genspark.ai/api/files/s/ji1pPLeA
