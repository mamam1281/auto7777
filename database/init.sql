-- Casino-Club F2P Database Schema
-- 초기 데이터베이스 스키마 및 기본 데이터 설정

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nickname VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    invite_code VARCHAR(20) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- 게임 관련 필드
    regular_coins BIGINT DEFAULT 1000,
    premium_gems INTEGER DEFAULT 0,
    play_xp INTEGER DEFAULT 0,
    
    -- 등급 및 상태
    vip_tier VARCHAR(20) DEFAULT 'STANDARD' CHECK (vip_tier IN ('STANDARD', 'VIP', 'PREMIUM')),
    battlepass_level INTEGER DEFAULT 1,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    
    -- 활성화 상태
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false
);

-- 사용자 세그먼트 테이블 (RFM 분석용)
CREATE TABLE IF NOT EXISTS user_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rfm_group VARCHAR(20) DEFAULT 'New' CHECK (rfm_group IN ('Whale', 'High_Engaged', 'Medium', 'Low', 'At_Risk', 'New')),
    ltv_score DECIMAL(10,2) DEFAULT 0.00,
    risk_profile VARCHAR(20) DEFAULT 'Low' CHECK (risk_profile IN ('Low', 'Medium', 'High')),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 액션 로그 테이블
CREATE TABLE IF NOT EXISTS user_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    action_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255)
);

-- 리워드 시스템 테이블
CREATE TABLE IF NOT EXISTS user_rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    reward_type VARCHAR(50) NOT NULL,
    reward_amount INTEGER NOT NULL,
    reward_data JSONB DEFAULT '{}',
    claimed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_action VARCHAR(50)
);

-- 가챠 시스템 로그
CREATE TABLE IF NOT EXISTS gacha_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    gacha_type VARCHAR(50) NOT NULL,
    cost_gems INTEGER NOT NULL,
    result_items JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 상점 거래 로그
CREATE TABLE IF NOT EXISTS shop_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL,
    item_id VARCHAR(100) NOT NULL,
    cost_gems INTEGER,
    cost_coins BIGINT,
    transaction_type VARCHAR(20) DEFAULT 'purchase' CHECK (transaction_type IN ('purchase', 'refund')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 배틀패스 상태 테이블
CREATE TABLE IF NOT EXISTS battlepass_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    season_id INTEGER NOT NULL,
    current_level INTEGER DEFAULT 1,
    current_xp INTEGER DEFAULT 0,
    is_premium BOOLEAN DEFAULT false,
    premium_purchased_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, season_id)
);

-- 알림 시스템 테이블
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);

-- JWT 토큰 블랙리스트 (로그아웃/보안)
CREATE TABLE IF NOT EXISTS token_blacklist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    blacklisted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 업데이트 트리거 생성 (updated_at 자동 업데이트)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- 기본 데이터 삽입 (개발용)
INSERT INTO users (nickname, email, invite_code, vip_tier, regular_coins, premium_gems) 
VALUES 
    ('admin', 'admin@casino-club.com', 'ADMIN001', 'PREMIUM', 100000, 1000),
    ('test_user', 'test@example.com', 'TEST001', 'STANDARD', 5000, 100),
    ('vip_user', 'vip@example.com', 'VIP001', 'VIP', 50000, 500)
ON CONFLICT (nickname) DO NOTHING;

-- 사용자 세그먼트 기본 데이터
INSERT INTO user_segments (user_id, rfm_group, ltv_score, risk_profile)
SELECT id, 'New', 0.00, 'Low' FROM users
ON CONFLICT DO NOTHING;

-- 배틀패스 시즌 1 기본 상태
INSERT INTO battlepass_status (user_id, season_id, current_level, current_xp)
SELECT id, 1, 1, 0 FROM users
ON CONFLICT (user_id, season_id) DO NOTHING;

-- 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_invite_code ON users(invite_code);
CREATE INDEX IF NOT EXISTS idx_users_vip_tier ON users(vip_tier);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 사용자 액션 인덱스
CREATE INDEX IF NOT EXISTS idx_user_actions_user_timestamp ON user_actions(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_user_actions_type ON user_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_user_actions_session ON user_actions(session_id);

-- 리워드 인덱스
CREATE INDEX IF NOT EXISTS idx_user_rewards_user_type ON user_rewards(user_id, reward_type);

-- 가챠 로그 인덱스  
CREATE INDEX IF NOT EXISTS idx_gacha_log_user_timestamp ON gacha_log(user_id, timestamp);

-- 상점 거래 인덱스
CREATE INDEX IF NOT EXISTS idx_shop_transactions_user_timestamp ON shop_transactions(user_id, timestamp);

-- 배틀패스 인덱스
CREATE INDEX IF NOT EXISTS idx_battlepass_status_user_season ON battlepass_status(user_id, season_id);

-- 알림 인덱스
CREATE INDEX IF NOT EXISTS idx_notifications_user_created ON notifications(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read);

-- 토큰 블랙리스트 인덱스
CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist(token_jti);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_user ON token_blacklist(user_id);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires ON token_blacklist(expires_at);

-- 통계 수집 활성화
ANALYZE users;
ANALYZE user_segments;
ANALYZE user_actions;
ANALYZE user_rewards;
