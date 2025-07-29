"""
데이터베이스 무결성 테스트를 위한 Pytest 픽스처
"""
import os
import pytest
import psycopg2
from psycopg2.extras import DictCursor
import time
from datetime import datetime, timedelta
import random
import threading

# 테스트 데이터베이스 연결 설정
DB_CONFIG = {
    'dbname': 'cc_webapp',
    'user': 'cc_user',
    'password': 'cc_password',
    'host': 'localhost',
    'port': 5432
}


@pytest.fixture(scope="session")
def db_connection():
    """테스트 전체에서 사용할 DB 연결을 제공하는 픽스처"""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=DictCursor)
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def clean_tables(db_connection):
    """각 테스트마다 테이블을 초기화하는 픽스처"""
    # 트랜잭션이 실패한 경우 롤백을 먼저 시도
    try:
        db_connection.rollback()
    except:
        pass
        
    # 테이블 비우기 (테스트 시작 전)
    try:
        with db_connection.cursor() as cur:
            cur.execute("DELETE FROM user_actions")
            cur.execute("DELETE FROM user_segments")
            cur.execute("DELETE FROM users")
            db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f"Clean up before test failed: {e}")
        
    yield
    
    # 테이블 비우기 (테스트 종료 후)
    try:
        db_connection.rollback()  # 혹시 모를 실패한 트랜잭션 처리
        with db_connection.cursor() as cur:
            cur.execute("DELETE FROM user_actions")
            cur.execute("DELETE FROM user_segments")
            cur.execute("DELETE FROM users")
            db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f"Clean up after test failed: {e}")


@pytest.fixture
def create_test_user(db_connection):
    """테스트 사용자를 생성하는 픽스처"""
    def _create_user(nickname=None, rank="STANDARD"):
        nickname = nickname or f"test_user_{int(time.time() * 1000)}"
        with db_connection.cursor() as cur:
            cur.execute("""
                INSERT INTO users (site_id, nickname, phone_number, password_hash, 
                               invite_code, created_at, rank)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, nickname
            """, (
                f"site_{nickname}", 
                nickname, 
                f"010-0000-0000",
                "test_hash",
                "TEST123",
                datetime.now(),
                rank
            ))
            user = cur.fetchone()
            db_connection.commit()
            return user
    return _create_user


@pytest.fixture
def create_user_segment(db_connection):
    """사용자 세그먼트를 생성하는 픽스처"""
    def _create_segment(user_id, rfm_group="Medium", risk_profile="Medium"):
        with db_connection.cursor() as cur:
            cur.execute("""
                INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                user_id,
                rfm_group,
                risk_profile,
                f"segment_for_user_{user_id}"
            ))
            segment_id = cur.fetchone()[0]
            db_connection.commit()
            return segment_id
    return _create_segment


@pytest.fixture
def create_user_action(db_connection):
    """사용자 액션을 생성하는 픽스처"""
    def _create_action(user_id, action_type="LOGIN", value=1.0):
        with db_connection.cursor() as cur:
            cur.execute("""
                INSERT INTO user_actions (user_id, action_type, timestamp, value)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                user_id,
                action_type,
                datetime.now(),
                value
            ))
            action_id = cur.fetchone()[0]
            db_connection.commit()
            return action_id
    return _create_action


@pytest.fixture
def get_user_actions(db_connection):
    """특정 사용자의 액션을 조회하는 픽스처"""
    def _get_actions(user_id):
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT * FROM user_actions
                WHERE user_id = %s
                ORDER BY timestamp DESC
            """, (user_id,))
            return cur.fetchall()
    return _get_actions


@pytest.fixture
def get_user_segments(db_connection):
    """특정 사용자의 세그먼트를 조회하는 픽스처"""
    def _get_segments(user_id):
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT * FROM user_segments
                WHERE user_id = %s
            """, (user_id,))
            return cur.fetchall()
    return _get_segments


@pytest.fixture
def concurrent_threads():
    """여러 스레드를 동시에 실행하는 헬퍼 픽스처"""
    def _run_concurrently(func, args_list, num_threads=None):
        num_threads = num_threads or len(args_list)
        threads = []
        results = [None] * len(args_list)
        exceptions = [None] * len(args_list)
        
        def worker(idx, func, args):
            try:
                results[idx] = func(*args)
            except Exception as e:
                exceptions[idx] = e
        
        for i, args in enumerate(args_list):
            t = threading.Thread(target=worker, args=(i, func, args))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        return results, exceptions
    
    return _run_concurrently
