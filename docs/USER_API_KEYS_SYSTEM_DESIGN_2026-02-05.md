# 사용자별 API 키 관리 시스템 설계

> **작성일**: 2026-02-05  
> **작성자**: AI Assistant  
> **목적**: 사용자가 자신의 API 키를 등록하고 관리할 수 있는 시스템 구축

---

## 📋 요구사항

### 기능 요구사항
1. **사용자별 API 키 저장**
   - Google API (TTS, Gemini, YouTube, Maps, etc.)
   - OpenAI API (ChatGPT, GPT-4)
   - Anthropic API (Claude)
   - ElevenLabs API (TTS)
   - 기타 확장 가능한 구조

2. **보안 요구사항**
   - API 키 암호화 저장
   - HTTPS 통신 필수
   - 사용자 인증 필수
   - 키 노출 방지 (마스킹 표시)

3. **사용자 인터페이스**
   - 직관적인 설정 페이지
   - API 키 추가/수정/삭제
   - API 키 유효성 검증
   - 사용량 모니터링 (선택사항)

---

## 🗄️ 데이터베이스 스키마

### Cloudflare D1 (SQLite)

#### 1. users 테이블
```sql
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,                    -- UUID
  email TEXT UNIQUE NOT NULL,             -- 사용자 이메일
  username TEXT UNIQUE,                   -- 사용자명 (선택)
  password_hash TEXT,                     -- 비밀번호 해시 (간단한 인증용)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

#### 2. user_api_keys 테이블
```sql
CREATE TABLE IF NOT EXISTS user_api_keys (
  id TEXT PRIMARY KEY,                    -- UUID
  user_id TEXT NOT NULL,                  -- users.id FK
  provider TEXT NOT NULL,                 -- 'google', 'openai', 'anthropic', 'elevenlabs'
  service TEXT,                           -- 세부 서비스 (예: 'tts', 'gemini', 'gpt-4')
  api_key_encrypted TEXT NOT NULL,        -- 암호화된 API 키
  is_active BOOLEAN DEFAULT 1,            -- 활성 상태
  last_used_at DATETIME,                  -- 마지막 사용 시간
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, provider, service)      -- 사용자당 provider+service 조합은 유일
);

CREATE INDEX idx_api_keys_user_id ON user_api_keys(user_id);
CREATE INDEX idx_api_keys_provider ON user_api_keys(provider);
```

#### 3. api_key_usage 테이블 (선택사항)
```sql
CREATE TABLE IF NOT EXISTS api_key_usage (
  id TEXT PRIMARY KEY,
  api_key_id TEXT NOT NULL,
  endpoint TEXT NOT NULL,                 -- 사용된 엔드포인트
  request_count INTEGER DEFAULT 1,
  success BOOLEAN DEFAULT 1,
  error_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (api_key_id) REFERENCES user_api_keys(id) ON DELETE CASCADE
);

CREATE INDEX idx_usage_api_key_id ON api_key_usage(api_key_id);
CREATE INDEX idx_usage_created_at ON api_key_usage(created_at);
```

---

## 🔐 API 키 암호화 방식

### Web Crypto API 사용 (Cloudflare Workers 호환)

```typescript
// 암호화 키 생성 (환경 변수에서 로드)
const ENCRYPTION_KEY = await crypto.subtle.importKey(
  "raw",
  new TextEncoder().encode(env.ENCRYPTION_SECRET),
  { name: "AES-GCM", length: 256 },
  false,
  ["encrypt", "decrypt"]
);

// API 키 암호화
async function encryptApiKey(plaintext: string): Promise<string> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    ENCRYPTION_KEY,
    new TextEncoder().encode(plaintext)
  );
  
  // IV + 암호문을 Base64로 인코딩
  const combined = new Uint8Array(iv.length + encrypted.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(encrypted), iv.length);
  
  return btoa(String.fromCharCode(...combined));
}

// API 키 복호화
async function decryptApiKey(ciphertext: string): Promise<string> {
  const combined = Uint8Array.from(atob(ciphertext), c => c.charCodeAt(0));
  const iv = combined.slice(0, 12);
  const encrypted = combined.slice(12);
  
  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    ENCRYPTION_KEY,
    encrypted
  );
  
  return new TextDecoder().decode(decrypted);
}
```

---

## 🔌 Backend API 엔드포인트

### 기본 경로: `/api/settings/api-keys`

#### 1. GET /api/settings/api-keys
사용자의 모든 API 키 조회 (마스킹됨)

**Request**:
```
GET /api/settings/api-keys
Authorization: Bearer <session_token>
```

**Response**:
```json
{
  "success": true,
  "api_keys": [
    {
      "id": "key-uuid-1",
      "provider": "google",
      "service": "tts",
      "api_key_masked": "AIzaSy***************dwbmA",
      "is_active": true,
      "last_used_at": "2026-02-05T00:00:00Z",
      "created_at": "2026-02-04T10:00:00Z"
    },
    {
      "id": "key-uuid-2",
      "provider": "openai",
      "service": "gpt-4",
      "api_key_masked": "sk-proj-***************",
      "is_active": true,
      "last_used_at": null,
      "created_at": "2026-02-04T11:00:00Z"
    }
  ]
}
```

#### 2. POST /api/settings/api-keys
새 API 키 등록

**Request**:
```json
{
  "provider": "google",
  "service": "tts",
  "api_key": "AIzaSyAmteZ8s0n0OdfYahj77m8DkULsn4dwbmA"
}
```

**Response**:
```json
{
  "success": true,
  "message": "API key added successfully",
  "api_key": {
    "id": "key-uuid-1",
    "provider": "google",
    "service": "tts",
    "api_key_masked": "AIzaSy***************dwbmA",
    "is_active": true
  }
}
```

#### 3. PUT /api/settings/api-keys/:id
API 키 수정

**Request**:
```json
{
  "api_key": "AIzaSyNEW_API_KEY_HERE",
  "is_active": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "API key updated successfully"
}
```

#### 4. DELETE /api/settings/api-keys/:id
API 키 삭제

**Response**:
```json
{
  "success": true,
  "message": "API key deleted successfully"
}
```

#### 5. POST /api/settings/api-keys/:id/verify
API 키 유효성 검증

**Response**:
```json
{
  "success": true,
  "valid": true,
  "message": "API key is valid",
  "quota_remaining": "95%"
}
```

---

## 🎨 프론트엔드 UI 설계

### 설정 페이지 경로: `/settings`

#### 레이아웃 구조
```
┌─────────────────────────────────────────────┐
│ 🔧 설정                                      │
├─────────────────────────────────────────────┤
│                                             │
│  📱 사이드바                    📄 메인 영역 │
│  ┌───────────┐                 ┌──────────┐│
│  │ 프로필    │                 │ API 키   ││
│  │ API 키 ✓  │                 │ 관리     ││
│  │ 알림      │                 │          ││
│  │ 보안      │                 │  [+추가] ││
│  └───────────┘                 │          ││
│                                 │ ┌──────┐ ││
│                                 │ │Google│ ││
│                                 │ └──────┘ ││
│                                 │ ┌──────┐ ││
│                                 │ │OpenAI│ ││
│                                 │ └──────┘ ││
│                                 └──────────┘│
└─────────────────────────────────────────────┘
```

#### API 키 카드 컴포넌트
```html
<div class="api-key-card">
  <div class="provider-icon">🔑</div>
  <div class="provider-info">
    <h3>Google Cloud API</h3>
    <p>Text-to-Speech, Gemini, YouTube</p>
  </div>
  <div class="key-display">
    <code>AIzaSy***************dwbmA</code>
    <button class="btn-show">👁️</button>
  </div>
  <div class="key-status">
    <span class="badge-active">✅ 활성</span>
    <span class="last-used">마지막 사용: 2시간 전</span>
  </div>
  <div class="key-actions">
    <button class="btn-verify">검증</button>
    <button class="btn-edit">수정</button>
    <button class="btn-delete">삭제</button>
  </div>
</div>
```

---

## 🔄 API 키 사용 흐름

### 1. 사용자 요청 시 동적 키 사용
```typescript
// 예: TTS 생성 요청
app.post('/api/tts/generate', async (c) => {
  const { env, user } = c;
  
  // 1. 사용자 API 키 조회
  const userApiKey = await getUserApiKey(env.DB, user.id, 'google', 'tts');
  
  // 2. 사용자 키가 있으면 사용, 없으면 시스템 기본 키 사용
  const apiKey = userApiKey 
    ? await decryptApiKey(userApiKey.api_key_encrypted)
    : env.GOOGLE_CLOUD_API_KEY;
  
  // 3. TTS 생성
  const result = await generateTTS(text, apiKey);
  
  // 4. 사용 기록 업데이트
  if (userApiKey) {
    await updateApiKeyUsage(env.DB, userApiKey.id);
  }
  
  return c.json(result);
});
```

### 2. Fallback 우선순위
```
1. 사용자 개인 API 키 (우선)
2. 시스템 기본 API 키 (폴백)
3. 대체 Provider (최종 폴백)
```

---

## 🛡️ 보안 고려사항

### 1. 인증/인가
- 간단한 세션 기반 인증 (Cloudflare KV 사용)
- JWT 토큰 (선택사항)
- 각 요청마다 사용자 인증 확인

### 2. API 키 보호
- 데이터베이스에 암호화 저장
- 프론트엔드에서 마스킹 표시
- HTTPS 필수
- 키 노출 시 즉시 폐기 권장

### 3. Rate Limiting
- 사용자당 API 호출 제한
- Cloudflare Rate Limiting 활용

### 4. 감사 로그
- API 키 생성/수정/삭제 기록
- 비정상적인 사용 패턴 모니터링

---

## 📊 지원 Provider 목록

### 초기 버전 (v0.1)
```typescript
const SUPPORTED_PROVIDERS = {
  google: {
    name: "Google Cloud",
    icon: "🔵",
    services: ["tts", "gemini", "youtube", "maps", "translate"],
    keyFormat: /^AIzaSy[A-Za-z0-9_-]{33}$/
  },
  openai: {
    name: "OpenAI",
    icon: "🟢",
    services: ["gpt-4", "gpt-3.5-turbo", "dall-e", "whisper"],
    keyFormat: /^sk-[A-Za-z0-9]{48,}$/
  },
  anthropic: {
    name: "Anthropic",
    icon: "🟣",
    services: ["claude-3", "claude-2"],
    keyFormat: /^sk-ant-[A-Za-z0-9_-]+$/
  },
  elevenlabs: {
    name: "ElevenLabs",
    icon: "🔊",
    services: ["tts", "voice-clone"],
    keyFormat: /^sk_[a-f0-9]{64}$/
  }
};
```

---

## 🚀 구현 단계

### Phase 1: 기본 인프라 (1-2일)
- [x] 데이터베이스 스키마 설계
- [ ] D1 마이그레이션 파일 작성
- [ ] 암호화/복호화 유틸리티 구현
- [ ] 기본 인증 시스템 구현

### Phase 2: Backend API (2-3일)
- [ ] CRUD 엔드포인트 구현
- [ ] API 키 검증 로직
- [ ] 사용자별 키 조회 로직
- [ ] Fallback 메커니즘 구현

### Phase 3: Frontend UI (2-3일)
- [ ] 설정 페이지 레이아웃
- [ ] API 키 카드 컴포넌트
- [ ] 추가/수정/삭제 폼
- [ ] 유효성 검증 UI

### Phase 4: 통합 및 테스트 (1-2일)
- [ ] TTS 서비스 통합
- [ ] LLM 서비스 통합
- [ ] End-to-End 테스트
- [ ] 보안 검토

---

## 📈 향후 확장 계획

### v0.2 (추가 기능)
- API 사용량 대시보드
- 비용 추적 (provider별 요금 계산)
- API 키 만료 알림
- 팀 공유 기능

### v0.3 (고급 기능)
- OAuth 통합
- 다중 사용자 관리
- API 키 템플릿
- 자동 로테이션

---

## 🔗 참고 자료

- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

---

**작성 완료**: 2026-02-05  
**다음 단계**: 데이터베이스 마이그레이션 파일 작성
