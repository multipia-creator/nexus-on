# NEXUS 로컬 실행 체크리스트

**작성일**: 2026-02-03  
**대상 환경**: 로컬 PC (Docker Compose)  
**버전**: v7.7

---

## 📋 사전 준비 체크리스트

### 1. 시스템 요구사항

#### 필수 소프트웨어
- [ ] **Docker Desktop** 설치 완료
  - Windows: Docker Desktop for Windows
  - macOS: Docker Desktop for Mac
  - Linux: Docker Engine + Docker Compose
  - 버전: 20.10.0 이상

- [ ] **Git** 설치 완료 (선택)
  - 버전: 2.30.0 이상

#### 시스템 리소스
- [ ] **메모리**: 최소 4GB, 권장 8GB
- [ ] **디스크 공간**: 최소 10GB 여유 공간
- [ ] **포트 확인**: 다음 포트가 사용 가능한지 확인
  ```bash
  # Windows PowerShell
  netstat -ano | findstr "8000 5672 15672 6379"
  
  # macOS/Linux
  lsof -i :8000,5672,15672,6379
  ```
  - `8000`: Supervisor (FastAPI)
  - `5672`: RabbitMQ (AMQP)
  - `15672`: RabbitMQ Management UI
  - `6379`: Redis

---

## 📦 파일 준비 체크리스트

### 2. NEXUS 백엔드 파일

- [ ] **백엔드 소스 확인**
  ```bash
  cd /home/user/webapp/docs/backend_reference
  ls -la
  ```
  
  필수 파일/디렉토리:
  - [ ] `nexus_supervisor/` - Supervisor 소스
  - [ ] `agents/` - 에이전트 워커
  - [ ] `shared/` - 공통 라이브러리
  - [ ] `docker/docker-compose.nexus.yml` - Docker Compose 설정
  - [ ] `.env.example` - 환경 변수 템플릿

### 3. 환경 변수 설정

- [ ] **`.env` 파일 생성**
  ```bash
  cd /home/user/webapp/docs/backend_reference
  cp .env.example .env
  ```

- [ ] **필수 환경 변수 설정**
  
  #### 인증 (필수)
  ```bash
  NEXUS_API_KEY=dev-key-change-me-in-production
  ADMIN_API_KEY=admin-key-change-me-in-production
  ```

  #### LLM Provider (필수 - 최소 1개)
  
  **옵션 1: Anthropic Claude (권장)**
  ```bash
  LLM_PRIMARY_PROVIDER=anthropic
  ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
  ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
  LLM_REQUIRED=true
  ```

  **옵션 2: OpenAI**
  ```bash
  LLM_PRIMARY_PROVIDER=openai
  OPENAI_API_KEY=sk-YOUR_KEY_HERE
  OPENAI_MODEL=gpt-4
  LLM_REQUIRED=true
  ```

  **옵션 3: Google Gemini**
  ```bash
  LLM_PRIMARY_PROVIDER=gemini
  GEMINI_API_KEY=YOUR_KEY_HERE
  GEMINI_MODEL=gemini-3-flash-preview
  LLM_REQUIRED=true
  ```

  #### Fallback 체인 (권장)
  ```bash
  LLM_FALLBACK_PROVIDERS=gemini,openai
  ```

  #### YouTube (선택)
  ```bash
  YOUTUBE_API_KEY=YOUR_YOUTUBE_KEY_HERE
  YOUTUBE_DEFAULT_REGION=KR
  YOUTUBE_DEFAULT_LANGUAGE=ko
  ```

  #### RAG 자동 Ingest (선택)
  ```bash
  RAG_AUTO_INGEST_ENABLED=false  # 나중에 true로 변경
  RAG_AUTO_INGEST_PATH=/data/gdrive_mirror
  RAG_AUTO_INGEST_HOUR=3
  RAG_AUTO_INGEST_MINUTE=0
  ```

- [ ] **환경 변수 검증**
  ```bash
  # 필수 키 존재 확인
  grep -E "NEXUS_API_KEY|LLM_PRIMARY_PROVIDER|ANTHROPIC_API_KEY|OPENAI_API_KEY|GEMINI_API_KEY" .env
  ```

### 4. 데이터 디렉토리 준비

- [ ] **RAG 데이터 폴더 생성** (RAG 사용 시)
  ```bash
  mkdir -p data/gdrive_mirror
  ```

- [ ] **로그 디렉토리 생성**
  ```bash
  mkdir -p logs
  ```

---

## 🚀 실행 체크리스트

### 5. Docker Compose 실행

- [ ] **Docker Desktop 실행 확인**
  ```bash
  docker info
  # 오류 없이 정보가 표시되어야 함
  ```

- [ ] **이미지 빌드 및 컨테이너 시작**
  ```bash
  cd /home/user/webapp/docs/backend_reference
  docker compose -f docker/docker-compose.nexus.yml up --build
  ```

  **예상 출력**:
  ```
  [+] Building ...
  [+] Running 4/4
   ✔ Network nexus_default    Created
   ✔ Container nexus-redis-1  Started
   ✔ Container nexus-rabbitmq-1  Started
   ✔ Container nexus-supervisor-1  Started
  ```

- [ ] **컨테이너 상태 확인** (새 터미널)
  ```bash
  docker compose -f docker/docker-compose.nexus.yml ps
  ```

  **모든 컨테이너가 "Up" 상태여야 함**:
  ```
  NAME                    STATUS
  nexus-supervisor-1      Up
  nexus-rabbitmq-1        Up
  nexus-redis-1           Up
  nexus-student-worker-1  Up (있는 경우)
  ```

### 6. 서비스 헬스체크

- [ ] **Supervisor 헬스체크**
  ```bash
  curl http://localhost:8000/health
  ```
  
  **예상 응답**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-02-03T...",
    "services": {
      "redis": "ok",
      "rabbitmq": "ok"
    }
  }
  ```

- [ ] **RabbitMQ Management UI**
  - URL: http://localhost:15672
  - Username: `guest`
  - Password: `guest`
  - [ ] 로그인 성공 확인
  - [ ] Queues 탭에서 `nexus.tasks` 큐 존재 확인

- [ ] **Redis 연결 확인**
  ```bash
  docker exec -it nexus-redis-1 redis-cli ping
  # "PONG" 응답 확인
  ```

### 7. UI 접속

- [ ] **웹 브라우저에서 UI 열기**
  - URL: http://localhost:8000/ui
  - [ ] 페이지 로드 성공
  - [ ] 콘솔 오류 없음 (F12 개발자 도구 확인)
  - [ ] SSE 연결 성공 메시지 확인

---

## 🔧 트러블슈팅 체크리스트

### 8. 일반적인 문제 해결

#### 문제 1: 포트 충돌
```bash
# 증상: "port is already allocated" 오류

# 해결:
# Windows
netstat -ano | findstr "8000"
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

#### 문제 2: Docker 메모리 부족
```bash
# 증상: 컨테이너가 반복 재시작

# 해결:
# Docker Desktop → Settings → Resources
# Memory를 최소 4GB로 증가
```

#### 문제 3: 환경 변수 누락
```bash
# 증상: "LLM_REQUIRED=true but no provider configured" 오류

# 해결:
# .env 파일에서 최소 1개 LLM Provider 설정 확인
grep -E "ANTHROPIC_API_KEY|OPENAI_API_KEY|GEMINI_API_KEY" .env
```

#### 문제 4: Redis/RabbitMQ 연결 실패
```bash
# 증상: "Connection refused" 오류

# 해결:
docker compose -f docker/docker-compose.nexus.yml down
docker compose -f docker/docker-compose.nexus.yml up --build
```

---

## 🧹 종료 및 정리 체크리스트

### 9. 정상 종료

- [ ] **컨테이너 중지**
  ```bash
  docker compose -f docker/docker-compose.nexus.yml down
  ```

- [ ] **데이터 보존 확인**
  - Redis 데이터는 재시작 시 유지됨
  - RabbitMQ 메시지는 durable 설정 시 유지됨

### 10. 완전 초기화 (필요 시)

- [ ] **모든 데이터 삭제**
  ```bash
  docker compose -f docker/docker-compose.nexus.yml down -v
  # -v 옵션: 볼륨까지 삭제
  ```

- [ ] **이미지 삭제**
  ```bash
  docker images | grep nexus
  docker rmi <IMAGE_ID>
  ```

---

## ✅ 최종 체크리스트

### 실행 성공 기준

- [ ] Docker Compose 실행 완료
- [ ] 모든 컨테이너 "Up" 상태
- [ ] `/health` 엔드포인트 정상 응답
- [ ] UI 페이지 로드 성공
- [ ] SSE 스트림 연결 성공
- [ ] 브라우저 콘솔에 오류 없음

### 다음 단계

실행이 성공하면 다음 문서를 참조하세요:
- **스모크 테스트**: `NEXUS_SMOKE_TEST_SCENARIOS.md`
- **오류 수정**: `NEXUS_ERROR_FIXES.md`
- **구현 지시서**: `NEXUS_IMPLEMENTATION_INSTRUCTIONS.md`

---

**작성자**: Claude Code Agent  
**최종 검토**: 2026-02-03
