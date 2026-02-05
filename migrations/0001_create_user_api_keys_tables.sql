-- Migration: 0001_create_user_api_keys_tables
-- Created: 2026-02-05
-- Description: 사용자별 API 키 관리 시스템 초기 스키마

-- ============================================================================
-- 1. users 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,                                    -- UUID
  email TEXT UNIQUE NOT NULL,                             -- 사용자 이메일
  username TEXT UNIQUE,                                   -- 사용자명 (선택)
  password_hash TEXT,                                     -- 비밀번호 해시
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================================================
-- 2. user_api_keys 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_api_keys (
  id TEXT PRIMARY KEY,                                    -- UUID
  user_id TEXT NOT NULL,                                  -- users.id FK
  provider TEXT NOT NULL,                                 -- 'google', 'openai', 'anthropic', 'elevenlabs'
  service TEXT,                                           -- 세부 서비스 (예: 'tts', 'gemini', 'gpt-4')
  api_key_encrypted TEXT NOT NULL,                        -- 암호화된 API 키
  is_active BOOLEAN DEFAULT 1,                            -- 활성 상태
  last_used_at DATETIME,                                  -- 마지막 사용 시간
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, provider, service)                      -- 사용자당 provider+service 조합은 유일
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_provider ON user_api_keys(provider);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON user_api_keys(is_active);

-- ============================================================================
-- 3. api_key_usage 테이블 (사용량 추적)
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_key_usage (
  id TEXT PRIMARY KEY,
  api_key_id TEXT NOT NULL,
  endpoint TEXT NOT NULL,                                 -- 사용된 엔드포인트
  request_count INTEGER DEFAULT 1,
  success BOOLEAN DEFAULT 1,
  error_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (api_key_id) REFERENCES user_api_keys(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_usage_api_key_id ON api_key_usage(api_key_id);
CREATE INDEX IF NOT EXISTS idx_usage_created_at ON api_key_usage(created_at);

-- ============================================================================
-- 4. sessions 테이블 (간단한 세션 관리)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,                                    -- Session ID
  user_id TEXT NOT NULL,
  token TEXT UNIQUE NOT NULL,                             -- Session token
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- ============================================================================
-- 테스트 데이터 (개발용)
-- ============================================================================

-- 테스트 사용자 생성 (비밀번호: test123)
INSERT OR IGNORE INTO users (id, email, username, password_hash) VALUES 
  ('user-test-001', 'test@nexus.ai', 'testuser', '$2a$10$dummy.hash.for.test.purposes');

-- 테스트 API 키 (실제로는 암호화되어야 함)
INSERT OR IGNORE INTO user_api_keys (id, user_id, provider, service, api_key_encrypted, is_active) VALUES 
  ('key-test-001', 'user-test-001', 'google', 'tts', 'encrypted_google_api_key_here', 1),
  ('key-test-002', 'user-test-001', 'openai', 'gpt-4', 'encrypted_openai_api_key_here', 1);
