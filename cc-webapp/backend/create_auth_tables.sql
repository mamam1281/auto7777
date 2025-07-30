-- Advanced Authentication System Tables
-- Created: 2025-07-30
-- Purpose: 고급 인증 시스템을 위한 테이블 생성

-- 1. User 테이블에 로그인 관련 필드 추가 (기존 테이블 수정)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP;

-- 2. UserSession 테이블 생성 (사용자 세션 관리)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jti VARCHAR(255) NOT NULL UNIQUE,
    token_type VARCHAR(20) NOT NULL DEFAULT 'access',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    device_info JSONB
);

-- 3. LoginAttempt 테이블 생성 (로그인 시도 추적)
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ip_address VARCHAR(45) NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),
    user_agent TEXT
);

-- 4. BlacklistedToken 테이블 생성 (토큰 블랙리스트)
CREATE TABLE IF NOT EXISTS blacklisted_tokens (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(255) NOT NULL UNIQUE,
    token_type VARCHAR(20) NOT NULL DEFAULT 'access',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    reason VARCHAR(100)
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_jti ON user_sessions(jti);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);

CREATE INDEX IF NOT EXISTS idx_login_attempts_user_id ON login_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_address ON login_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_attempts_attempted_at ON login_attempts(attempted_at);

CREATE INDEX IF NOT EXISTS idx_blacklisted_tokens_jti ON blacklisted_tokens(jti);
CREATE INDEX IF NOT EXISTS idx_blacklisted_tokens_user_id ON blacklisted_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_blacklisted_tokens_expires_at ON blacklisted_tokens(expires_at);

-- 데이터 정합성을 위한 제약 조건
ALTER TABLE user_sessions 
ADD CONSTRAINT chk_token_type CHECK (token_type IN ('access', 'refresh'));

ALTER TABLE blacklisted_tokens 
ADD CONSTRAINT chk_blacklist_token_type CHECK (token_type IN ('access', 'refresh'));

-- 기본 데이터 설정 (기존 사용자들의 login_count 초기화)
UPDATE users SET login_count = 0 WHERE login_count IS NULL;
UPDATE users SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL;

-- 완료 메시지
SELECT 'Advanced Authentication Tables Created Successfully!' as status;
