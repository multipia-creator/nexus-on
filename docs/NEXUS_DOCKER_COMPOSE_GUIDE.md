# NEXUS Docker Compose 가이드

**작성일**: 2026-02-03  
**버전**: v2.0  
**대상**: Full-stack 배포 (Frontend + Backend)

---

## 📦 Docker Compose 개요

NEXUS는 **3가지 Docker Compose 설정**을 제공합니다:

1. **docker-compose.yml** - 기본 설정 (Quick Start)
2. **docker-compose.dev.yml** - 개발 환경 (Hot Reload)
3. **docker-compose.prod.yml** - 운영 환경 (보안 강화)

---

## 🚀 빠른 시작

### **Quick Start (기본 설정)**

```bash
# 프로젝트 루트에서 실행
docker-compose up -d

# 접속
# Frontend: http://localhost:8080
# Backend:  http://localhost:8000

# 로그 확인
docker-compose logs -f

# 종료
docker-compose down
```

**특징**:
- ✅ Frontend: 포트 8080 (Nginx + React)
- ✅ Backend: 포트 8000 (FastAPI)
- ✅ Health check 자동 실행
- ✅ CORS 자동 설정

---

## 🛠️ 개발 환경 (Hot Reload)

### **docker-compose.dev.yml**

**Hot Reload 지원** - 코드 변경 시 자동 재시작:

```bash
# 개발 모드 실행
docker-compose -f docker-compose.dev.yml up --build

# 접속
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000 (Hot Reload)
```

**특징**:
- ✅ Backend Hot Reload: 소스 코드 마운트 (`./backend:/app`)
- ✅ Frontend: 빌드 후 정적 서빙
- ✅ CORS: `http://localhost:3000` 허용
- ✅ Health check: 10초 간격

**개발 워크플로우**:
1. `docker-compose -f docker-compose.dev.yml up` 실행
2. Backend 코드 수정 → 자동 재시작 (Uvicorn `--reload`)
3. Frontend 코드 수정 → 재빌드 필요 (`docker-compose build frontend`)

---

## 🌐 운영 환경 (보안 강화)

### **docker-compose.prod.yml**

**보안 강화** - Backend 외부 노출 안 됨:

```bash
# 운영 모드 실행 (Detached)
docker-compose -f docker-compose.prod.yml up -d

# 접속
# Frontend: http://localhost (포트 80)
# Backend:  내부 네트워크만 (외부 접근 불가)

# 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 종료
docker-compose -f docker-compose.prod.yml down
```

**특징**:
- ✅ Backend: 외부 노출 안 됨 (`expose: 8000`, `ports` 없음)
- ✅ Frontend: 포트 80 (프로덕션)
- ✅ Health check: 30초 간격
- ✅ Restart policy: `unless-stopped`

**보안 장점**:
- 🔒 Backend는 Frontend를 통해서만 접근 가능
- 🔒 Docker 내부 네트워크 격리
- 🔒 외부 공격 표면 최소화

---

## 📋 서비스 구성

### **1. Backend (FastAPI)**

**이미지**: `python:3.11-slim` 기반  
**포트**: 8000 (내부) / 8000 (외부, dev/default만)  
**환경 변수**:
- `CORS_ORIGINS`: CORS 허용 도메인
- `PYTHONUNBUFFERED=1`: 즉시 로그 출력

**Health Check**:
```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"NEXUS v2 Backend","version":"1.2.0"}
```

**Hot Reload** (dev 모드):
- 소스 코드 마운트: `./backend:/app`
- Uvicorn `--reload` 플래그

---

### **2. Frontend (Nginx + React)**

**이미지**: `node:18-alpine` (빌드) + `nginx:alpine` (서빙)  
**포트**: 
- 3000 (dev)
- 8080 (default)
- 80 (prod)

**빌드 인자** (ARG):
- `VITE_API_BASE`: Backend URL
  - dev: `http://backend:8000`
  - default: `http://localhost:8000`
  - prod: `http://backend:8000`
- `VITE_DEMO_MODE`: 데모 모드 (`false` 기본)

**Health Check**:
```bash
curl http://localhost:8080/health
# OK
```

---

## 🔧 환경 변수 설정

### **방법 1: .env 파일 사용**

`.env.example`을 `.env`로 복사하고 수정:

```bash
cp .env.example .env
```

`.env`:
```env
# Backend
CORS_ORIGINS=http://localhost:8080,http://localhost:3000

# Frontend (for docker-compose build)
VITE_API_BASE=http://localhost:8000
VITE_DEMO_MODE=false

# Docker Compose
COMPOSE_PROJECT_NAME=nexus
```

### **방법 2: 빌드 시 ARG 전달**

```bash
docker-compose build --build-arg VITE_API_BASE=http://backend:8000
```

---

## 🐛 트러블슈팅

### **문제 1: Backend 연결 실패 (CORS 에러)**

**증상**: 브라우저 Console에 CORS 에러

**원인**: `CORS_ORIGINS`에 Frontend URL이 없음

**해결**:
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

---

### **문제 2: Frontend가 Backend를 찾지 못함**

**증상**: API 호출 실패, "Network Error"

**원인**: `VITE_API_BASE`가 잘못 설정됨

**해결**:
- **Docker 내부 통신**: `VITE_API_BASE=http://backend:8000`
- **브라우저에서 호출**: `VITE_API_BASE=http://localhost:8000`

**권장**: 기본 설정 사용 (`http://localhost:8000`)

---

### **문제 3: 빌드 실패 ("Cannot find module")**

**증상**: `npm run build` 실패

**원인**: 의존성 미설치

**해결**:
```bash
# 캐시 제거 후 재빌드
docker-compose build --no-cache
```

---

### **문제 4: Health check 실패**

**증상**: 컨테이너가 unhealthy 상태

**원인**: 서비스가 시작되지 않음

**해결**:
```bash
# 로그 확인
docker-compose logs backend
docker-compose logs frontend

# 컨테이너 상태 확인
docker-compose ps
```

---

## 🔍 유용한 명령어

### **서비스 관리**:
```bash
# 전체 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d backend

# 서비스 재시작
docker-compose restart backend

# 서비스 중지
docker-compose stop

# 서비스 제거 (볼륨 포함)
docker-compose down -v
```

### **로그 확인**:
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend

# 최근 100줄
docker-compose logs --tail=100
```

### **빌드**:
```bash
# 전체 재빌드
docker-compose build --no-cache

# 특정 서비스 재빌드
docker-compose build frontend

# 빌드 후 실행
docker-compose up --build
```

### **상태 확인**:
```bash
# 서비스 상태
docker-compose ps

# Health check
curl http://localhost:8000/health  # Backend
curl http://localhost:8080/health  # Frontend
```

---

## 🎯 실행 시나리오

### **시나리오 1: 로컬 개발 (Hot Reload)**

```bash
# 개발 모드 실행
docker-compose -f docker-compose.dev.yml up

# 접속: http://localhost:3000
# Backend 코드 수정 → 자동 재시작
# Frontend 코드 수정 → docker-compose build frontend 필요
```

---

### **시나리오 2: 프로덕션 테스트 (로컬)**

```bash
# 운영 모드 실행
docker-compose -f docker-compose.prod.yml up -d

# 접속: http://localhost
# Backend는 외부 노출 안 됨
# Frontend를 통해서만 접근
```

---

### **시나리오 3: CI/CD 배포**

```bash
# 1. 빌드
docker-compose build --no-cache

# 2. 이미지 태그
docker tag nexus-frontend:latest myregistry/nexus-frontend:v2.0
docker tag nexus-backend:latest myregistry/nexus-backend:v2.0

# 3. 푸시
docker push myregistry/nexus-frontend:v2.0
docker push myregistry/nexus-backend:v2.0

# 4. 운영 서버에서 Pull & Run
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 네트워크 구조

```
┌─────────────────────────────────────────┐
│         Docker Network (nexus-network)  │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │───▶│   Backend    │  │
│  │  (Nginx)     │    │  (FastAPI)   │  │
│  │  Port: 8080  │    │  Port: 8000  │  │
│  └──────────────┘    └──────────────┘  │
│         │                               │
└─────────┼───────────────────────────────┘
          │
          ▼
     Browser (http://localhost:8080)
```

**특징**:
- Frontend와 Backend는 같은 Docker 네트워크 내에서 통신
- 브라우저는 Frontend(8080)로 접근
- Frontend는 Backend(8000)로 API 호출
- CORS 설정으로 브라우저 접근 허용

---

## 🔐 보안 체크리스트

### **개발 환경**:
- [ ] Backend 포트 8000 외부 노출 (로컬 개발만)
- [ ] CORS: `http://localhost:3000` 허용
- [ ] Health check 활성화

### **운영 환경**:
- [ ] Backend 외부 노출 안 됨 (`expose` only)
- [ ] CORS: Frontend 도메인만 허용
- [ ] HTTPS 사용 (리버스 프록시)
- [ ] 환경 변수에 민감 정보 없음
- [ ] Restart policy: `unless-stopped`

---

## 📚 참고 문서

- [README.md](../README.md) - 프로젝트 전체 가이드
- [NEXUS_DEPLOYMENT_GUIDE.md](./NEXUS_DEPLOYMENT_GUIDE.md) - 배포 가이드
- [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) - 상용화 체크리스트

---

## 🎓 교수님께

**완료된 작업**:
✅ 3가지 Docker Compose 설정 (dev/default/prod)  
✅ Backend Dockerfile (FastAPI)  
✅ Frontend Dockerfile (Multi-stage build)  
✅ Health check 엔드포인트 추가  
✅ CORS 자동 설정  
✅ Hot Reload 지원 (dev 모드)  
✅ 보안 강화 (prod 모드, Backend 외부 노출 안 됨)  

**즉시 실행 가능**:
```bash
docker-compose up -d
# 접속: http://localhost:8080
```

**다음 단계**: 상용화 체크리스트 작성 (PRODUCTION_CHECKLIST.md)
