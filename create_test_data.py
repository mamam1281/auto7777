# 개선된 샘플 데이터 생성 스크립트 (2025-07-29)
# 현실적인 데이터 및 테스트 시나리오 생성

import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import DictCursor
import sys
import os
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 데이터베이스 연결 설정
DB_CONFIG = {
    'dbname': 'cc_webapp',
    'user': 'cc_user',
    'password': 'cc_password',
    'host': 'localhost',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=DictCursor)
def create_sample_users(conn, num_users=10):
    users = []
    with conn.cursor() as cur:
        for i in range(num_users):
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            cur.execute("""
                INSERT INTO users (site_id, nickname, phone_number, password_hash, 
                                 invite_code, created_at, rank)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, nickname
            """, (
                f"site_{i}", 
                f"user_{i}", 
                f"010-0000-00{i:02d}",
                "hash",
                "ABC123",
                created_at,
                random.choice(["STANDARD", "PREMIUM", "VIP"])
            ))
            users.append(cur.fetchone())
        conn.commit()
    return users

def create_sample_segments(conn, users):
    with conn.cursor() as cur:
        for user in users:
            cur.execute("""
                INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
                VALUES (%s, %s, %s, %s)
            """, (
                user['id'],
                random.choice(["Whale", "High Engaged", "Medium", "Low/At-risk"]),
                random.choice(["Low", "Medium", "High"]),
                f"segment_{user['nickname']}"
            ))
        conn.commit()

def create_sample_actions(conn, users, actions_per_user=5):
    with conn.cursor() as cur:
        for user in users:
            for _ in range(actions_per_user):
                timestamp = datetime.utcnow() - timedelta(hours=random.randint(0, 100))
                cur.execute("""
                    INSERT INTO user_actions (user_id, action_type, timestamp, value)
                    VALUES (%s, %s, %s, %s)
                """, (
                    user['id'],
                    random.choice(["LOGIN", "SLOT_SPIN", "GACHA_SPIN"]),
                    timestamp,
                    random.uniform(0, 100)
                ))
        conn.commit()

def create_tables(conn):
    with conn.cursor() as cur:
        # users 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                site_id VARCHAR(255) NOT NULL,
                nickname VARCHAR(255) UNIQUE NOT NULL,
                phone_number VARCHAR(20),
                password_hash VARCHAR(255),
                invite_code VARCHAR(50),
                created_at TIMESTAMP NOT NULL,
                rank VARCHAR(20) CHECK (rank IN ('STANDARD', 'PREMIUM', 'VIP'))
            );
            
            -- 인덱스 생성
            CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
            CREATE INDEX IF NOT EXISTS idx_users_rank ON users(rank);
            CREATE INDEX IF NOT EXISTS idx_users_invite_code ON users(invite_code);
        """)
        
        # user_segments 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_segments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                rfm_group VARCHAR(50) CHECK (rfm_group IN ('Whale', 'High Engaged', 'Medium', 'Low/At-risk')),
                risk_profile VARCHAR(20) CHECK (risk_profile IN ('Low', 'Medium', 'High')),
                name VARCHAR(255)
            );
            
            -- 인덱스 생성
            CREATE INDEX IF NOT EXISTS idx_user_segments_user_id ON user_segments(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_segments_rfm_group ON user_segments(rfm_group);
            CREATE INDEX IF NOT EXISTS idx_user_segments_risk_profile ON user_segments(risk_profile);
        """)
        
        # user_actions 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                action_type VARCHAR(50) CHECK (action_type IN ('LOGIN', 'SLOT_SPIN', 'GACHA_SPIN')),
                timestamp TIMESTAMP NOT NULL,
                value FLOAT
            );
            
            -- 인덱스 생성
            CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_actions_action_type ON user_actions(action_type);
            CREATE INDEX IF NOT EXISTS idx_user_actions_timestamp ON user_actions(timestamp);
            CREATE INDEX IF NOT EXISTS idx_user_actions_user_action_type ON user_actions(user_id, action_type);
            CREATE INDEX IF NOT EXISTS idx_user_actions_user_timestamp ON user_actions(user_id, timestamp);
        """)
        conn.commit()

def main():
    conn = get_connection()
    try:
        logger.info("Creating tables if they don't exist...")
        create_tables(conn)
        
        logger.info("Creating sample users...")
        users = create_sample_users(conn)
        
        logger.info("Creating user segments...")
        create_sample_segments(conn, users)
        
        logger.info("Creating user actions...")
        create_sample_actions(conn, users)
        
        logger.info("샘플 데이터 생성 완료!")
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
