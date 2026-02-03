# NEXUS Docker Compose 가이드

**작성일**: 2026-02-03  
**버전**: v2.0  
**대상**: Full-stack 배포 (Frontend + Backend)

---

## 📦 Docker Compose 구성

### **서비스 구성**:
1. **Frontend** (Nginx + React)
   - 포트: 8080 (기본), 3000 (개발), 80 (운영)
   - 빌드 시점에 `VITE_API_BASE` 환경 변수 주입
   - SPA 라우팅 지원 (nginx `try_files`)

2. **Backend** (FastAPI)
   - 포트: 8000 (기본, 개발), 내부 네트워크만 (운영)
   - CORS 설정 자동 구성
   - Health check: `/health`

3. **네트워크**:
   - `nexus-network` (bridge 모드)
   - 서비스 간 통신: `http://backend:8000`, `http://frontend:80`

---

## 🚀 실행 방법

### **1️⃣ 기본 실행 (빠른 시작)**

```bash
# 프로젝트 루트에서 실행
cd /home/user/webapp

# 컨테이너 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 접속
# Frontend: http://localhost:8080
# Backend: http://localhost:8000
```

**종료**:
```bash
docker-compose down
```

---

### **2️⃣ 개발 환경 (Hot Reload)**

개발 환경에서는 Backend 소스 코드를 볼륨 마운트하여 Hot Reload를 지원합니다.

```bash
# 개발 환경 실행
docker-compose -f docker-compose.dev.yml up --build

# 접속
# Frontend: http://localhost:3000
# Backend: http://localhost:8000 (Hot Reload 지원)

# 종료
docker-compose -f docker-compose.dev.yml down
```

**특징**:
- ✅ Backend Hot Reload (`--reload` 플래그)
- ✅ Backend 소스 코드 볼륨 마운트 (`./backend:/app`)
- ✅ CORS: `http://localhost:3000` 허용
- ✅ 개발 포트: Frontend 3000, Backend 8000

---

### **3️⃣ 운영 환경 (Production)**

운영 환경에서는 Backend를 외부에 노출하지 않고, Frontend를 통해서만 접근합니다.

```bash
# 운영 환경 실행
docker-compose -f docker-compose.prod.yml up -d

# 접속
# Frontend: http://localhost (포트 80)
# Backend: 외부 노출 안 됨 (내부 네트워크만)

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 종료
docker-compose -f docker-compose.prod.yml down
```

**특징**:
- ✅ Backend 외부 노출 안 됨 (보안 강화)
- ✅ Frontend가 포트 80에서 실행
- ✅ `restart: unless-stopped` (자동 재시작)
- ✅ Health check 주기: 30초

---

## 🔧 환경 변수 설정

### **방법 1: .env 파일 사용**

`.env` 파일 생성:
```bash
cp .env.example .env
```

`.env` 내용:
```env
# Backend CORS
CORS_ORIGINS=http://localhost:8080,http://localhost:3000

# Frontend (빌드 시점에 사용)
VITE_API_BASE=http://localhost:8000
VITE_DEMO_MODE=false

# Docker Compose
COMPOSE_PROJECT_NAME=nexus
```

### **방법 2: Docker Compose 파일에서 직접 설정**

`docker-compose.yml`에서 환경 변수를 직접 수정:
```yaml
services:
  backend:
    environment:
      - CORS_ORIGINS=http://yourdomain.com
  
  frontend:
    build:
      args:
        VITE_API_BASE: http://backend:8000
        VITE_DEMO_MODE: "false"
```

---

## 🔍 서비스 상태 확인

### **컨테이너 상태**:
```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 상세 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### **Health Check**:
```bash
# Backend Health Check
curl http://localhost:8000/health

# Frontend Health Check
curl http://localhost:8080/health
```

### **네트워크 확인**:
```bash
# 네트워크 목록
docker network ls | grep nexus

# 네트워크 상세
docker network inspect nexus_nexus-network
```

---

## 🐛 트러블슈팅

### **문제 1: "Connection refused" (Backend 연결 실패)**

**증상**: Frontend에서 Backend API 호출 시 연결 실패

**원인**: 
1. Backend 컨테이너가 시작되지 않음
2. `VITE_API_BASE` 설정 오류

**해결**:
```bash
# 1. Backend 상태 확인
docker-compose ps backend

# 2. Backend 로그 확인
docker-compose logs backend

# 3. Health Check
curl http://localhost:8000/health

# 4. 재빌드 (환경 변수 변경 시)
docker-compose down
docker-compose up --build
```

---

### **문제 2: CORS 에러**

**증상**: 브라우저 Console에 "CORS policy" 에러

**원인**: Backend CORS 설정에 Frontend 도메인이 없음

**해결**:
1. `.env` 파일 수정:
   ```env
   CORS_ORIGINS=http://localhost:8080,http://localhost:3000,http://yourdomain.com
   ```

2. Backend 재시작:
   ```bash
   docker-compose restart backend
   ```

---

### **문제 3: 환경 변수 미적용**

**증상**: `VITE_API_BASE` 설정이 적용되지 않음

**원인**: Vite 환경 변수는 **빌드 시점**에 임베드됨

**해결**:
```bash
# 캐시 제거 후 재빌드
docker-compose down
docker-compose build --no-cache frontend
docker-compose up
```

---

### **문제 4: "Cannot connect to backend" (Docker 내부 네트워크)**

**증상**: Frontend에서 `http://backend:8000` 호출 시 실패

**원인**: 브라우저는 Docker 내부 네트워크를 알 수 없음

**해결**:
- **개발 환경**: `VITE_API_BASE=http://localhost:8000` (외부 접근)
- **운영 환경**: Backend를 Nginx Proxy로 노출하거나, API Gateway 사용

---

### **문제 5: 빌드 실패 ("npm ci failed")**

**증상**: Frontend 빌드 중 npm 에러

**원인**: `package-lock.json` 불일치

**해결**:
```bash
# Frontend 디렉토리에서 로컬 빌드 테스트
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build

# 성공 후 Docker 빌드
cd ..
docker-compose build frontend
```

---

## 📊 Docker Compose 파일 비교

| 항목 | docker-compose.yml | docker-compose.dev.yml | docker-compose.prod.yml |
|------|-------------------|------------------------|-------------------------|
| **Frontend 포트** | 8080 | 3000 | 80 |
| **Backend 포트** | 8000 (외부 노출) | 8000 (외부 노출) | 내부만 (노출 안 됨) |
| **Backend Hot Reload** | ❌ | ✅ | ❌ |
| **볼륨 마운트** | ❌ | ✅ (backend 소스) | ❌ |
| **재시작 정책** | `unless-stopped` | ❌ (수동) | `unless-stopped` |
| **Health Check 주기** | 30s | 10s | 30s |
| **용도** | 빠른 시작, 테스트 | 개발, 디버깅 | 프로덕션 |

---

## 🎯 권장 사용 시나리오

### **로컬 개발**:
```bash
# Backend만 수정하는 경우
docker-compose -f docker-compose.dev.yml up backend

# 로컬에서 Frontend 실행 (Hot Reload 더 빠름)
cd frontend
npm run dev
```

### **통합 테스트**:
```bash
# Full-stack 통합 테스트
docker-compose up --build

# Device Pairing 흐름 테스트
# 1. http://localhost:8080 접속
# 2. Windows Companion 실행
# 3. 페어링 코드 입력
```

### **프로덕션 배포**:
```bash
# 운영 환경 배포
docker-compose -f docker-compose.prod.yml up -d

# 헬스 체크
curl http://localhost/health
curl http://backend:8000/health  # 내부 네트워크
```

---

## 📚 관련 문서

1. **README.md** - 프로젝트 전체 가이드
2. **docs/NEXUS_DEPLOYMENT_GUIDE.md** - 배포 가이드
3. **frontend/Dockerfile** - Frontend Dockerfile
4. **backend/Dockerfile** - Backend Dockerfile
5. **docker-compose.yml** - 기본 Compose 설정
6. **docker-compose.dev.yml** - 개발 환경 Compose
7. **docker-compose.prod.yml** - 운영 환경 Compose

---

## 🔐 보안 고려사항

### **개발 환경**:
- ✅ Backend Hot Reload 지원 (빠른 개발)
- ⚠️ Backend가 외부 노출됨 (포트 8000)
- ⚠️ 소스 코드 볼륨 마운트

### **운영 환경**:
- ✅ Backend 외부 노출 안 됨 (보안 강화)
- ✅ `restart: unless-stopped` (고가용성)
- ✅ Health Check 주기 최적화 (30s)
- ⚠️ HTTPS 별도 설정 필요 (Nginx SSL 또는 Reverse Proxy)

---

## 🚀 다음 단계

1. ✅ **로컬 테스트**: `docker-compose up` 실행 후 동작 확인
2. ⏳ **HTTPS 설정**: Nginx SSL 인증서 추가 또는 Reverse Proxy (Traefik, Caddy)
3. ⏳ **데이터 영속성**: Redis/Postgres 컨테이너 추가
4. ⏳ **모니터링**: Prometheus + Grafana 추가
5. ⏳ **CI/CD**: GitHub Actions로 자동 빌드/배포

---

**작성자**: 남현우 교수  
**프로젝트**: NEXUS v2  
**도메인**: nexus  
**최종 업데이트**: 2026-02-03
