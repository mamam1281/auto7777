"""
데이터 무결성 검증 테스트
"""
import pytest
import psycopg2
import random
from datetime import datetime, timedelta

def test_data_type_integrity(db_connection, clean_tables, create_test_user):
    """
    데이터 타입 무결성: 적절한 타입의 데이터가 저장되고 검색되는지 검증
    """
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    # 액션 생성 - 다양한 타입의 데이터
    timestamp = datetime.now()
    value = 123.45
    
    with db_connection.cursor() as cur:
        cur.execute("""
            INSERT INTO user_actions (user_id, action_type, timestamp, value)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, "LOGIN", timestamp, value))
        action_id = cur.fetchone()[0]
        db_connection.commit()
    
    # 데이터 검색 및 타입 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT user_id, action_type, timestamp, value FROM user_actions WHERE id = %s", (action_id,))
        result = cur.fetchone()
        
        # 타입 검증
        assert isinstance(result['user_id'], int), f"user_id는 정수여야 하지만 {type(result['user_id'])}입니다."
        assert isinstance(result['action_type'], str), f"action_type은 문자열이어야 하지만 {type(result['action_type'])}입니다."
        assert isinstance(result['timestamp'], datetime), f"timestamp는 datetime이어야 하지만 {type(result['timestamp'])}입니다."
        assert isinstance(result['value'], float), f"value는 실수여야 하지만 {type(result['value'])}입니다."
        
        # 값 검증
        assert result['user_id'] == user_id, f"user_id가 {user_id}이어야 하지만 {result['user_id']}입니다."
        assert result['action_type'] == "LOGIN", f"action_type이 LOGIN이어야 하지만 {result['action_type']}입니다."
        # PostgreSQL은 마이크로초 단위로 저장하므로 근사값 비교
        assert abs((result['timestamp'] - timestamp).total_seconds()) < 0.001, \
               f"timestamp가 {timestamp}에 가까워야 하지만 {result['timestamp']}입니다."
        assert result['value'] == value, f"value가 {value}여야 하지만 {result['value']}입니다."


def test_null_constraints(db_connection, clean_tables):
    """
    NULL 제약 조건: NOT NULL로 지정된 컬럼에는 NULL 값이 허용되지 않아야 함
    """
    with db_connection.cursor() as cur:
        # 필수 필드가 누락된 사용자 생성 시도
        with pytest.raises(psycopg2.errors.NotNullViolation):
            cur.execute("""
                INSERT INTO users (site_id, nickname, password_hash, invite_code)
                VALUES (%s, %s, %s, %s)
            """, ("site_null_test", None, "hash", "ABC123"))  # nickname이 NULL
            db_connection.commit()
        db_connection.rollback()
        
        # 필수 필드가 누락된 액션 생성 시도
        with db_connection.cursor() as cur:
            # 유효한 사용자 생성
            cur.execute("""
                INSERT INTO users (site_id, nickname, password_hash, invite_code, created_at, rank)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, ("site_null_test", "user_null_test", "hash", "ABC123", datetime.now(), "STANDARD"))
            user_id = cur.fetchone()[0]
            db_connection.commit()
            
            # timestamp가 NULL인 액션 생성 시도
            with pytest.raises(psycopg2.errors.NotNullViolation):
                cur.execute("""
                    INSERT INTO user_actions (user_id, action_type, timestamp, value)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, "LOGIN", None, 1.0))  # timestamp가 NULL
                db_connection.commit()
            db_connection.rollback()


def test_data_consistency_across_tables(db_connection, clean_tables, create_test_user, 
                                      create_user_segment, create_user_action):
    """
    테이블 간 데이터 일관성: 관련 테이블 간의 데이터가 일관성을 유지해야 함
    """
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    # 세그먼트와 액션 생성
    segment_id = create_user_segment(user_id, rfm_group="Whale")
    for i in range(3):
        create_user_action(user_id, action_type="LOGIN")
    
    # 사용자 정보 업데이트
    with db_connection.cursor() as cur:
        cur.execute("UPDATE users SET rank = %s WHERE id = %s", ("VIP", user_id))
        db_connection.commit()
    
    # 각 테이블 조회 및 데이터 일관성 검증
    with db_connection.cursor() as cur:
        # 사용자 조회
        cur.execute("SELECT rank FROM users WHERE id = %s", (user_id,))
        user_rank = cur.fetchone()['rank']
        
        # 세그먼트 조회
        cur.execute("SELECT rfm_group FROM user_segments WHERE user_id = %s", (user_id,))
        segment_rfm_group = cur.fetchone()['rfm_group']
        
        # 액션 조회
        cur.execute("SELECT COUNT(*) FROM user_actions WHERE user_id = %s AND action_type = %s", (user_id, "LOGIN"))
        action_count = cur.fetchone()[0]
    
    # 데이터 일관성 검증
    assert user_rank == "VIP", f"사용자 랭크가 VIP여야 하지만 {user_rank}입니다."
    assert segment_rfm_group == "Whale", f"세그먼트 RFM 그룹이 Whale이어야 하지만 {segment_rfm_group}입니다."
    assert action_count == 3, f"로그인 액션 수가 3이어야 하지만 {action_count}입니다."


def test_data_aggregation_integrity(db_connection, clean_tables, create_test_user, create_user_action):
    """
    데이터 집계 무결성: 집계 함수(SUM, COUNT 등)의 결과가 정확한지 검증
    """
    # 여러 사용자 생성
    users = []
    for i in range(3):
        user = create_test_user(nickname=f"agg_user_{i}")
        users.append(user)
    
    # 각 사용자에 대한 액션 생성
    action_counts = {
        "LOGIN": [5, 3, 7],
        "SLOT_SPIN": [10, 8, 6],
        "GACHA_SPIN": [2, 4, 3],
    }
    
    for i, user in enumerate(users):
        for action_type, counts in action_counts.items():
            for _ in range(counts[i]):
                create_user_action(user['id'], action_type=action_type, value=random.uniform(1, 100))
    
    # 집계 쿼리 실행 및 결과 검증
    with db_connection.cursor() as cur:
        # 액션 유형별 총 개수
        cur.execute("""
            SELECT action_type, COUNT(*) as count
            FROM user_actions
            GROUP BY action_type
            ORDER BY action_type
        """)
        
        action_totals = {}
        for row in cur.fetchall():
            action_totals[row['action_type']] = row['count']
        
        # 사용자별 액션 개수
        cur.execute("""
            SELECT u.nickname, COUNT(a.id) as action_count
            FROM users u
            LEFT JOIN user_actions a ON u.id = a.user_id
            WHERE u.nickname LIKE 'agg_user_%'
            GROUP BY u.nickname
            ORDER BY u.nickname
        """)
        
        user_action_counts = {}
        for row in cur.fetchall():
            user_action_counts[row['nickname']] = row['action_count']
        
        # 액션 값의 평균
        cur.execute("""
            SELECT AVG(value) as avg_value
            FROM user_actions
        """)
        avg_value = cur.fetchone()['avg_value']
    
    # 검증
    # 액션 유형별 총 개수
    expected_login_count = sum(action_counts["LOGIN"])
    expected_slot_spin_count = sum(action_counts["SLOT_SPIN"])
    expected_gacha_spin_count = sum(action_counts["GACHA_SPIN"])
    
    assert action_totals["LOGIN"] == expected_login_count, \
           f"LOGIN 액션 수가 {expected_login_count}여야 하지만 {action_totals['LOGIN']}입니다."
    assert action_totals["SLOT_SPIN"] == expected_slot_spin_count, \
           f"SLOT_SPIN 액션 수가 {expected_slot_spin_count}여야 하지만 {action_totals['SLOT_SPIN']}입니다."
    assert action_totals["GACHA_SPIN"] == expected_gacha_spin_count, \
           f"GACHA_SPIN 액션 수가 {expected_gacha_spin_count}여야 하지만 {action_totals['GACHA_SPIN']}입니다."
    
    # 사용자별 액션 개수
    for i, user in enumerate(users):
        expected_count = sum([action_counts[action_type][i] for action_type in action_counts])
        actual_count = user_action_counts[user['nickname']]
        assert actual_count == expected_count, \
               f"사용자 {user['nickname']}의 액션 수가 {expected_count}여야 하지만 {actual_count}입니다."
    
    # 액션 값의 평균 (1-100 사이의 값이므로 대략적인 범위만 검증)
    assert 1 <= avg_value <= 100, f"액션 값의 평균이 1-100 사이여야 하지만 {avg_value}입니다."


def test_batch_update_integrity(db_connection, clean_tables, create_test_user, create_user_action):
    """
    배치 업데이트 무결성: 대량의 레코드를 한 번에 업데이트할 때 데이터 무결성이 유지되어야 함
    """
    # 여러 사용자 생성
    users = []
    for i in range(5):
        user = create_test_user(nickname=f"batch_user_{i}")
        users.append(user)
    
    # 각 사용자에 대한 액션 생성
    for user in users:
        for _ in range(10):
            create_user_action(user['id'], action_type="LOGIN", value=1.0)
    
    # 배치 업데이트 수행
    with db_connection.cursor() as cur:
        cur.execute("BEGIN")
        # LOGIN 액션의 값을 두 배로 증가
        cur.execute("""
            UPDATE user_actions
            SET value = value * 2
            WHERE action_type = 'LOGIN'
        """)
        # 업데이트된 행 수 확인
        cur.execute("SELECT COUNT(*) FROM user_actions WHERE action_type = 'LOGIN' AND value = 2.0")
        updated_count = cur.fetchone()[0]
        db_connection.commit()
    
    # 배치 업데이트 결과 검증
    assert updated_count == 10 * 5, f"50개의 행이 업데이트되어야 하지만 {updated_count}개가 업데이트되었습니다."
    
    # 각 사용자별로 업데이트 결과 확인
    with db_connection.cursor() as cur:
        for user in users:
            cur.execute("""
                SELECT COUNT(*) as count, AVG(value) as avg_value
                FROM user_actions
                WHERE user_id = %s AND action_type = 'LOGIN'
            """, (user['id'],))
            result = cur.fetchone()
            
            assert result['count'] == 10, \
                   f"사용자 {user['nickname']}의 LOGIN 액션 수가 10이어야 하지만 {result['count']}입니다."
            assert result['avg_value'] == 2.0, \
                   f"사용자 {user['nickname']}의 LOGIN 액션 평균 값이 2.0이어야 하지만 {result['avg_value']}입니다."
