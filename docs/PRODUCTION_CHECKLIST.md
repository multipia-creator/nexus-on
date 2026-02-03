# NEXUS 상용화 체크리스트 (Production Checklist)

**작성일**: 2026-02-03  
**버전**: v2.0  
**대상**: 상용 서비스 배포 준비  
**관리자**: 남현우 교수

---

## 📋 체크리스트 개요

이 문서는 NEXUS를 **상용 서비스로 배포**하기 전에 확인해야 할 보안, 운영, 비용, 규정 준수 항목을 정리한 체크리스트입니다.

**체크리스트 영역**:
1. 🔐 **보안** (인증, 인가, 암호화)
2. 🏢 **테넌트 격리** (멀티테넌트 환경)
3. 📊 **로그 및 감사** (Audit Trail)
4. 💰 **비용 최적화** (태깅, 모니터링)
5. 🚦 **Rate Limiting** (API 요청 제한)
6. 🔄 **SSE 재연결 정책** (실시간 스트림)
7. 🛡️ **PII/DLP** (개인정보 보호)
8. ✅ **RED 승인 (Two-Phase Commit)** (고위험 작업)
9. 💾 **데이터 저장소** (In-memory → Redis/Postgres)
10. 🚀 **운영 및 배포** (CI/CD, 모니터링)

---

## 🔐 1. 보안 (Security)

### **1.1 웹 사용자 인증 (Authentication)**

현재 상태: ❌ 미구현 (Tenant 헤더만 사용)

**필수 구현**:
- [ ] **JWT 기반 인증** 또는 **OAuth 2.0** 구현
  - 로그인 엔드포인트: `POST /auth/login`
  - 토큰 발급: Access Token (15분) + Refresh Token (7일)
  - 토큰 검증 미들웨어: `@app.middleware("http")`
- [ ] **사용자 세션 관리**
  - Redis/Postgres에 세션 저장
  - 로그아웃 시 세션 무효화
- [ ] **비밀번호 보안**
  - bcrypt/Argon2 해싱 (최소 12 rounds)
  - 비밀번호 복잡도 정책 (8자 이상, 특수문자 포함)
- [ ] **MFA (Multi-Factor Authentication)** (선택)
  - TOTP (Google Authenticator) 지원

**구현 예시**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/protected")
async def protected_route(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}
```

---

### **1.2 디바이스 토큰 수명 및 회전 (Device Token Lifecycle)**

현재 상태: ⚠️ 영구 토큰 (만료 없음)

**필수 구현**:
- [ ] **토큰 만료 시간 설정**
  - Access Token: 7일
  - Refresh Token: 30일
- [ ] **토큰 회전 (Rotation)**
  - Refresh Token으로 새 Access Token 발급
  - 엔드포인트: `POST /devices/token/refresh`
- [ ] **토큰 폐기 (Revocation)**
  - 디바이스 삭제 시 토큰 즉시 무효화
  - Blacklist (Redis) 사용
- [ ] **토큰 저장소**
  - In-memory → Redis (TTL 지원)

**구현 예시**:
```python
# Device Token with Expiration
device_token = {
    "device_id": "dev_123",
    "token": "abc123...",
    "issued_at": "2026-02-03T10:00:00Z",
    "expires_at": "2026-02-10T10:00:00Z",  # 7일 후
    "refresh_token": "xyz789...",
    "refresh_expires_at": "2026-03-05T10:00:00Z"  # 30일 후
}

# Redis TTL
redis.setex(f"device_token:{device_id}", 604800, token)  # 7일
```

---

### **1.3 HTTPS 및 암호화**

현재 상태: ❌ HTTP 사용 (로컬 개발)

**필수 구현**:
- [ ] **HTTPS 적용** (프로덕션)
  - Let's Encrypt 또는 AWS ACM 인증서
  - Nginx/Cloudflare를 통한 SSL Termination
- [ ] **암호화 통신**
  - TLS 1.2 이상
  - 안전한 Cipher Suite (AES-256-GCM)
- [ ] **민감 데이터 암호화**
  - Device Token: 데이터베이스 저장 시 암호화
  - 환경 변수: AWS Secrets Manager / HashiCorp Vault

---

## 🏢 2. 테넌트 격리 (Multi-Tenancy Isolation)

현재 상태: ✅ 헤더 기반 테넌트 분리 (`x-org-id`, `x-project-id`)

**필수 강화**:
- [ ] **데이터베이스 레벨 격리**
  - Tenant ID를 모든 테이블에 추가
  - Row-Level Security (Postgres) 또는 Partitioning
  - 쿼리에 `WHERE tenant_id = ?` 자동 추가 (ORM 미들웨어)
- [ ] **API 레벨 격리**
  - 모든 엔드포인트에서 Tenant ID 검증
  - Cross-Tenant 접근 차단
- [ ] **SSE 스트림 격리**
  - Tenant별 별도 채널 (Redis Pub/Sub)
  - `session_id`에 Tenant ID 포함
- [ ] **Rate Limiting 격리**
  - Tenant별 독립적인 Rate Limit
- [ ] **로그 격리**
  - 로그에 Tenant ID 필수 포함
  - Tenant별 로그 조회 API

**구현 예시**:
```python
# Tenant Middleware
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    org_id = request.headers.get("x-org-id")
    project_id = request.headers.get("x-project-id")
    if not org_id or not project_id:
        return JSONResponse(status_code=400, content={"detail": "Missing tenant headers"})
    request.state.tenant_id = f"{org_id}:{project_id}"
    response = await call_next(request)
    return response

# Query with Tenant ID
def get_devices(tenant_id: str):
    return db.query(Device).filter(Device.tenant_id == tenant_id).all()
```

---

## 📊 3. 로그 및 감사 (Logging & Audit Trail)

현재 상태: ⚠️ 기본 로깅만 (Uvicorn 로그)

**필수 구현**:
- [ ] **구조화된 로깅**
  - JSON 포맷 로그 (ELK/Datadog 호환)
  - 필수 필드: `timestamp`, `level`, `tenant_id`, `user_id`, `correlation_id`, `message`
- [ ] **감사 로그 (Audit Log)**
  - 모든 중요 작업 기록:
    - 사용자 로그인/로그아웃
    - 디바이스 페어링/삭제
    - 고위험 명령 (RED 승인)
    - 데이터 조회/수정/삭제
  - 엔드포인트: `GET /audit/logs`
- [ ] **로그 보관 정책**
  - 30일: Hot Storage (빠른 조회)
  - 1년: Cold Storage (아카이브)
  - GDPR 준수: 사용자 요청 시 삭제
- [ ] **로그 모니터링**
  - 에러 로그 알림 (Slack/PagerDuty)
  - 이상 패턴 감지 (Rate Limit 초과, 인증 실패 증가)

**구현 예시**:
```python
import structlog

logger = structlog.get_logger()

# Audit Log
@app.post("/devices/pairing/confirm_by_code")
async def confirm_pairing(req: PairingConfirmByCodeReq):
    device_id = await device_store.confirm_pairing(req.pairing_code)
    
    # Audit Log
    logger.info(
        "device_pairing_confirmed",
        tenant_id=request.state.tenant_id,
        user_id=request.state.user_id,
        device_id=device_id,
        pairing_code=req.pairing_code,
        action="device_pairing",
        result="success"
    )
    
    return {"device_id": device_id}
```

---

## 💰 4. 비용 최적화 (Cost Optimization)

현재 상태: ❌ 비용 태깅 없음

**필수 구현**:
- [ ] **리소스 태깅**
  - 모든 클라우드 리소스에 태그 추가:
    - `Environment`: `production` / `staging` / `dev`
    - `Service`: `nexus-backend` / `nexus-frontend`
    - `Tenant`: `{org_id}:{project_id}`
    - `CostCenter`: `engineering`
- [ ] **비용 모니터링**
  - Tenant별 비용 추적 (AWS Cost Explorer, Cloudflare Analytics)
  - API 호출 횟수, SSE 연결 시간, 데이터 전송량 측정
- [ ] **비용 알림**
  - 예산 초과 시 알림 (Slack/Email)
  - Tenant별 Quota 설정
- [ ] **리소스 최적화**
  - Auto-Scaling (Peak 시간대만)
  - Idle 리소스 자동 종료 (Dev 환경)

**구현 예시**:
```python
# Usage Tracking
usage_tracker = {
    "tenant_id": "org1:proj1",
    "api_calls": 1523,
    "sse_connections": 45,
    "sse_duration_seconds": 18900,  # 5.25시간
    "data_transfer_mb": 320,
    "cost_usd": 0.85,
    "period": "2026-02-03"
}

# Quota Enforcement
@app.middleware("http")
async def quota_middleware(request: Request, call_next):
    tenant_id = request.state.tenant_id
    usage = await get_tenant_usage(tenant_id)
    if usage["api_calls"] > QUOTA_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Quota exceeded"})
    response = await call_next(request)
    await increment_usage(tenant_id, "api_calls")
    return response
```

---

## 🚦 5. Rate Limiting

현재 상태: ❌ 미구현

**필수 구현**:
- [ ] **API Rate Limiting**
  - Tenant별: 1000 req/min
  - User별: 100 req/min
  - Device별: 50 req/min
- [ ] **SSE 연결 제한**
  - Tenant별: 최대 100개 동시 연결
  - Session별: 1개 연결
- [ ] **Rate Limit 알고리즘**
  - Token Bucket (추천) 또는 Sliding Window
  - Redis 기반 카운터
- [ ] **Rate Limit 헤더**
  - `X-RateLimit-Limit`: 제한
  - `X-RateLimit-Remaining`: 남은 횟수
  - `X-RateLimit-Reset`: 초기화 시간

**구현 예시**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/devices")
@limiter.limit("100/minute")
async def list_devices(request: Request):
    return device_store.list_devices()
```

---

## 🔄 6. SSE 재연결 정책

현재 상태: ✅ Last-Event-ID 지원

**필수 강화**:
- [ ] **재연결 정책**
  - 자동 재연결: 최대 5회
  - Backoff: 1s → 2s → 4s → 8s → 16s
  - 영구 실패 시 사용자에게 알림
- [ ] **연결 타임아웃**
  - Idle 연결: 5분 후 자동 종료
  - Ping 이벤트: 30초마다 전송
- [ ] **연결 복구**
  - Last-Event-ID로 미수신 이벤트 재전송
  - 최대 1000개 이벤트 버퍼 (초과 시 스냅샷 재전송)
- [ ] **연결 모니터링**
  - 동시 연결 수 모니터링
  - 비정상 연결 감지 및 차단

**구현 예시**:
```typescript
// Frontend: SSE 재연결
const connectSSE = (retries = 0) => {
  const eventSource = new EventSource(url);
  
  eventSource.onerror = () => {
    eventSource.close();
    if (retries < 5) {
      const backoff = Math.pow(2, retries) * 1000; // 1s, 2s, 4s, 8s, 16s
      setTimeout(() => connectSSE(retries + 1), backoff);
    } else {
      alert("Connection failed. Please refresh the page.");
    }
  };
};
```

---

## 🛡️ 7. PII/DLP (개인정보 보호)

현재 상태: ⚠️ 개인정보 처리 정책 없음

**필수 구현**:
- [ ] **PII 식별**
  - 개인정보: 이메일, 전화번호, IP 주소, Device ID
  - 민감정보: 비밀번호, 토큰, API Key
- [ ] **PII 암호화**
  - 저장: AES-256 암호화
  - 전송: HTTPS
  - 로그: PII 마스킹 (`user@example.com` → `u***@e***.com`)
- [ ] **PII 접근 제어**
  - 관리자만 PII 조회 가능
  - 감사 로그 기록
- [ ] **DLP (Data Loss Prevention)**
  - API 응답에서 민감정보 필터링
  - 로그에 토큰/비밀번호 출력 금지
- [ ] **GDPR 준수**
  - 사용자 데이터 다운로드 API
  - 사용자 데이터 삭제 API (Right to be Forgotten)

**구현 예시**:
```python
# PII Masking
def mask_email(email: str) -> str:
    parts = email.split("@")
    return f"{parts[0][0]}***@{parts[1][0]}***.{parts[1].split('.')[-1]}"

# GDPR: Data Export
@app.get("/users/{user_id}/data")
async def export_user_data(user_id: str):
    user_data = await db.get_user_data(user_id)
    # Audit log
    logger.info("user_data_exported", user_id=user_id)
    return user_data

# GDPR: Data Deletion
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    await db.delete_user(user_id)
    logger.info("user_deleted", user_id=user_id)
    return {"status": "deleted"}
```

---

## ✅ 8. RED 승인 (Two-Phase Commit)

현재 상태: ⚠️ AgentReport에 `approval_level` 필드만 존재

**필수 구현**:
- [ ] **RED 승인 워크플로우**
  - Phase 1: 명령 제안 → `approval_level="red"` 리포트 전송
  - Phase 2: 사용자 승인 → `POST /approvals/{approval_id}/decide`
  - Phase 3: 승인 후 명령 실행 → 결과 리포트 전송
- [ ] **승인 엔드포인트**
  - `GET /approvals`: 대기 중인 승인 목록
  - `POST /approvals/{approval_id}/decide`: 승인/거부
  - `GET /approvals/{approval_id}`: 승인 상태 조회
- [ ] **승인 정책**
  - RED: 필수 승인 (예: 파일 삭제, 시스템 설정 변경)
  - YELLOW: 선택 승인 (예: 파일 쓰기)
  - GREEN: 자동 승인 (예: 파일 읽기)
- [ ] **승인 타임아웃**
  - 승인 대기: 최대 5분
  - 타임아웃 시 자동 거부
- [ ] **승인 로그**
  - 모든 승인 요청/결과 감사 로그 기록

**구현 예시**:
```python
# Phase 1: Propose Command
@app.post("/sidecar/command")
async def propose_command(req: CommandReq):
    if req.risk_level == "high":
        approval_id = await create_approval(req)
        # Send RED report
        report = AgentReport(
            meta={"approval_level": "red", ...},
            ask=[{"question": "Allow file deletion?", "type": "confirm"}]
        )
        await sse_broadcast(report)
        return {"status": "pending_approval", "approval_id": approval_id}
    else:
        await execute_command(req)
        return {"status": "accepted"}

# Phase 2: User Approval
@app.post("/approvals/{approval_id}/decide")
async def decide_approval(approval_id: str, decision: str):
    approval = await get_approval(approval_id)
    if decision == "approve":
        await execute_command(approval.command)
        logger.info("approval_granted", approval_id=approval_id)
    else:
        logger.info("approval_denied", approval_id=approval_id)
    return {"status": decision}
```

---

## 💾 9. 데이터 저장소 전환

현재 상태: ⚠️ In-memory (서버 재시작 시 데이터 손실)

**필수 전환**:
- [ ] **Redis (권장)**
  - 용도: SSE 이벤트 버퍼, Device Token, Rate Limit 카운터
  - 장점: 빠른 읽기/쓰기, TTL 지원, Pub/Sub
  - 설정: `redis://localhost:6379`
- [ ] **PostgreSQL (권장)**
  - 용도: 사용자, 디바이스, 감사 로그, 승인 기록
  - 장점: ACID, 관계형 데이터, 복잡한 쿼리
  - 설정: `postgresql://user:pass@localhost:5432/nexus`
- [ ] **마이그레이션 계획**
  - Phase 1: Redis 연동 (SSE 이벤트, Device Token)
  - Phase 2: Postgres 연동 (User, Device, Audit Log)
  - Phase 3: In-memory 제거

**구현 예시**:
```python
# Redis Connection
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

# Store Device Token
await redis_client.setex(f"device_token:{device_id}", 604800, token)

# PostgreSQL Connection
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/nexus")

# Store User
async with AsyncSession(engine) as session:
    user = User(email="user@example.com", name="Alice")
    session.add(user)
    await session.commit()
```

---

## 🚀 10. 운영 및 배포

현재 상태: ⚠️ 수동 배포 (Docker Compose)

**필수 구현**:
- [ ] **CI/CD 파이프라인**
  - GitHub Actions / GitLab CI
  - 자동 테스트 (Unit, Integration, E2E)
  - 자동 배포 (Staging → Production)
- [ ] **모니터링**
  - 메트릭: CPU, 메모리, API 지연시간, SSE 연결 수
  - APM: Datadog / New Relic / Prometheus + Grafana
  - 알림: 에러율 5% 초과, API 지연 1초 초과
- [ ] **헬스 체크**
  - `/health`: 기본 헬스 체크
  - `/health/ready`: 데이터베이스 연결 확인
  - `/health/live`: 프로세스 살아있음
- [ ] **백업 및 복구**
  - 데이터베이스: 일 1회 자동 백업
  - 백업 보관: 30일
  - 복구 테스트: 월 1회
- [ ] **롤백 계획**
  - Blue-Green Deployment
  - 이전 버전으로 즉시 롤백 가능

---

## 📋 체크리스트 우선순위

### **🔴 High Priority (즉시 구현)**
1. ✅ JWT 기반 웹 사용자 인증
2. ✅ Device Token 만료 및 회전
3. ✅ HTTPS 적용 (프로덕션)
4. ✅ Redis/Postgres 전환 (In-memory 제거)
5. ✅ Rate Limiting (API + SSE)
6. ✅ 구조화된 로깅 및 감사 로그

### **🟡 Medium Priority (3개월 내)**
1. ⚠️ RED 승인 워크플로우 구현
2. ⚠️ PII 암호화 및 GDPR 준수
3. ⚠️ 비용 태깅 및 모니터링
4. ⚠️ SSE 재연결 정책 강화
5. ⚠️ CI/CD 파이프라인 구축

### **🟢 Low Priority (6개월 내)**
1. ℹ️ MFA (Multi-Factor Authentication)
2. ℹ️ DLP (Data Loss Prevention)
3. ℹ️ 백업 및 복구 자동화
4. ℹ️ 이상 패턴 감지 (AI 기반)

---

## 📚 참고 문서

- [NEXUS_DOCKER_COMPOSE_GUIDE.md](./NEXUS_DOCKER_COMPOSE_GUIDE.md) - Docker Compose 가이드
- [NEXUS_DEPLOYMENT_GUIDE.md](./NEXUS_DEPLOYMENT_GUIDE.md) - 배포 가이드
- [NEXUS_ERROR_FIXES.md](./NEXUS_ERROR_FIXES.md) - 오류 수정 가이드

---

## 🎓 교수님께

**체크리스트 작성 완료!**

**포함 항목**:
✅ 1. 보안 (JWT, Device Token, HTTPS)  
✅ 2. 테넌트 격리 (DB, API, SSE)  
✅ 3. 로그 및 감사 (구조화 로깅, Audit Trail)  
✅ 4. 비용 최적화 (태깅, Quota)  
✅ 5. Rate Limiting (API, SSE)  
✅ 6. SSE 재연결 정책 (Backoff, 복구)  
✅ 7. PII/DLP (암호화, GDPR)  
✅ 8. RED 승인 (Two-Phase Commit)  
✅ 9. 데이터 저장소 (Redis, Postgres)  
✅ 10. 운영 및 배포 (CI/CD, 모니터링)  

**우선순위**:
- 🔴 High: 인증, Token 관리, HTTPS, Redis/Postgres, Rate Limit, 로깅
- 🟡 Medium: RED 승인, PII, 비용, SSE 재연결, CI/CD
- 🟢 Low: MFA, DLP, 백업, AI 감지

**다음 단계**: Git 커밋 및 최종 정리
