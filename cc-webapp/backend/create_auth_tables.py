#!/usr/bin/env python3
"""
Advanced Authentication System Tables Creation Script
Created: 2025-07-30
Purpose: PostgreSQL에 고급 인증 시스템 테이블 생성
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        # 환경변수에서 데이터베이스 정보 가져오기
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'casino_club'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        
        print(f"Connecting to PostgreSQL at {db_config['host']}:{db_config['port']}")
        print(f"Database: {db_config['database']}")
        print(f"User: {db_config['user']}")
        
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def execute_sql_script():
    """SQL 스크립트 실행"""
    
    # SQL 스크립트 내용
    sql_script = """
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
"""
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🚀 Creating advanced authentication tables...")
        
        # SQL 스크립트를 개별 명령으로 분리하여 실행
        commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        for i, command in enumerate(commands, 1):
            if command:
                try:
                    print(f"📝 Executing command {i}/{len(commands)}...")
                    cursor.execute(command)
                    print(f"✅ Command {i} executed successfully")
                except Exception as e:
                    print(f"⚠️ Warning in command {i}: {e}")
                    # 일부 명령은 실패할 수 있음 (예: 이미 존재하는 컬럼 추가)
                    continue
        
        # 테이블 생성 확인
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('user_sessions', 'login_attempts', 'blacklisted_tokens');
        """)
        
        created_tables = cursor.fetchall()
        print(f"\n✅ Created tables: {[table[0] for table in created_tables]}")
        
        # Users 테이블의 새로운 컬럼 확인
        cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name IN ('last_login_at', 'login_count', 'failed_login_attempts', 'account_locked_until');
        """)
        
        new_columns = cursor.fetchall()
        print(f"✅ Added user columns: {[col[0] for col in new_columns]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Advanced Authentication System Tables Created Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error executing SQL script: {e}")
        conn.close()
        return False

def verify_tables():
    """생성된 테이블 검증"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("\n🔍 Verifying created tables...")
        
        # 테이블 목록 확인
        cursor.execute("""
        SELECT 
            table_name,
            (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public' 
        AND table_name IN ('users', 'user_sessions', 'login_attempts', 'blacklisted_tokens')
        ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\n📊 Table Overview:")
        for table_name, column_count in tables:
            print(f"  - {table_name}: {column_count} columns")
        
        # 인덱스 확인
        cursor.execute("""
        SELECT indexname, tablename 
        FROM pg_indexes 
        WHERE tablename IN ('user_sessions', 'login_attempts', 'blacklisted_tokens')
        AND schemaname = 'public'
        ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        print(f"\n🗂️ Created indexes: {len(indexes)}")
        for index_name, table_name in indexes:
            print(f"  - {table_name}.{index_name}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🔐 Advanced Authentication System Setup")
    print("=" * 60)
    
    # 테이블 생성
    if execute_sql_script():
        # 테이블 검증
        verify_tables()
        
        print("\n" + "=" * 60)
        print("✅ Setup completed successfully!")
        print("🚀 You can now start the FastAPI server with advanced authentication")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ Setup failed!")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
