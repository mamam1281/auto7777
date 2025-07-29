"""
참조 무결성 테스트 (FK 제약조건 검증)
"""
import pytest
import psycopg2
from psycopg2.errors import ForeignKeyViolation, UniqueViolation, CheckViolation

# 각 테스트는 clean_tables 픽스처를 사용하여 매번 테이블을 초기화합니다.

def test_user_segment_fk_constraint(db_connection, clean_tables):
    """user_segments 테이블의 user_id 외래키 제약 조건 검증"""
    # 존재하지 않는 사용자 ID로 세그먼트 생성 시도
    non_existent_user_id = 9999
    with db_connection.cursor() as cur:
        # ForeignKeyViolation 예외가 발생해야 함
        with pytest.raises(ForeignKeyViolation):
            cur.execute("""
                INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
                VALUES (%s, %s, %s, %s)
            """, (
                non_existent_user_id,  # 존재하지 않는 사용자 ID
                "Whale", 
                "High",
                "test_segment"
            ))
            db_connection.commit()


def test_user_action_fk_constraint(db_connection, clean_tables):
    """user_actions 테이블의 user_id 외래키 제약 조건 검증"""
    # 존재하지 않는 사용자 ID로 액션 생성 시도
    non_existent_user_id = 9999
    with db_connection.cursor() as cur:
        # ForeignKeyViolation 예외가 발생해야 함
        with pytest.raises(ForeignKeyViolation):
            cur.execute("""
                INSERT INTO user_actions (user_id, action_type, timestamp, value)
                VALUES (%s, %s, %s, %s)
            """, (
                non_existent_user_id,  # 존재하지 않는 사용자 ID
                "LOGIN", 
                '2025-07-29 10:00:00',
                1.0
            ))
            db_connection.commit()


def test_user_on_delete_cascade(db_connection, clean_tables, create_test_user, 
                            create_user_segment, create_user_action, 
                            get_user_segments, get_user_actions):
    """사용자 삭제 시 관련 세그먼트와 액션도 함께 삭제되는지 확인 (ON DELETE CASCADE)"""
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    # 세그먼트와 액션 생성
    segment_id = create_user_segment(user_id)
    action_id = create_user_action(user_id)
    
    # 세그먼트와 액션이 생성되었는지 확인
    segments = get_user_segments(user_id)
    actions = get_user_actions(user_id)
    assert len(segments) == 1, "세그먼트가 생성되지 않았습니다."
    assert len(actions) == 1, "액션이 생성되지 않았습니다."
    
    # 사용자 삭제
    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db_connection.commit()
    
    # 세그먼트와 액션도 삭제되었는지 확인
    segments = get_user_segments(user_id)
    actions = get_user_actions(user_id)
    assert len(segments) == 0, "사용자 삭제 후에도 세그먼트가 남아있습니다."
    assert len(actions) == 0, "사용자 삭제 후에도 액션이 남아있습니다."


def test_unique_constraints(db_connection, clean_tables, create_test_user):
    """고유 제약 조건(Unique Constraint) 검증"""
    # 사용자 생성
    nickname = f"unique_user_{pytest.app_global_counter}"
    pytest.app_global_counter += 1
    user = create_test_user(nickname=nickname)
    
    # 동일한 닉네임으로 다른 사용자 생성 시도 - UniqueViolation 예외가 발생해야 함
    with pytest.raises(UniqueViolation):
        create_test_user(nickname=nickname)


def test_check_constraints_user_rank(db_connection, clean_tables):
    """사용자 등급(rank) 체크 제약 조건 검증"""
    with db_connection.cursor() as cur:
        # 유효한 등급으로 사용자 생성
        cur.execute("""
            INSERT INTO users (site_id, nickname, password_hash, invite_code, created_at, rank)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "site_valid", 
            "user_valid_rank", 
            "hash",
            "ABC123",
            '2025-07-29 10:00:00',
            "VIP"  # 유효한 등급
        ))
        db_connection.commit()
        
        # 유효하지 않은 등급으로 사용자 생성 시도 - CheckViolation 예외가 발생해야 함
        with pytest.raises(CheckViolation):
            cur.execute("""
                INSERT INTO users (site_id, nickname, password_hash, invite_code, created_at, rank)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                "site_invalid", 
                "user_invalid_rank", 
                "hash",
                "ABC123",
                '2025-07-29 10:00:00',
                "INVALID_RANK"  # 유효하지 않은 등급
            ))
            db_connection.commit()


def test_check_constraints_segment_rfm(db_connection, clean_tables, create_test_user):
    """세그먼트 RFM 그룹 체크 제약 조건 검증"""
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    with db_connection.cursor() as cur:
        # 유효한 RFM 그룹으로 세그먼트 생성
        cur.execute("""
            INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
            VALUES (%s, %s, %s, %s)
        """, (
            user_id,
            "Whale",  # 유효한 RFM 그룹
            "Medium",
            "valid_segment"
        ))
        db_connection.commit()
        
        # 유효하지 않은 RFM 그룹으로 세그먼트 생성 시도 - CheckViolation 예외가 발생해야 함
        with pytest.raises(CheckViolation):
            cur.execute("""
                INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
                VALUES (%s, %s, %s, %s)
            """, (
                user_id,
                "INVALID_GROUP",  # 유효하지 않은 RFM 그룹
                "Medium",
                "invalid_segment"
            ))
            db_connection.commit()


def test_check_constraints_action_type(db_connection, clean_tables, create_test_user):
    """액션 타입 체크 제약 조건 검증"""
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    with db_connection.cursor() as cur:
        # 유효한 액션 타입으로 액션 생성
        cur.execute("""
            INSERT INTO user_actions (user_id, action_type, timestamp, value)
            VALUES (%s, %s, %s, %s)
        """, (
            user_id,
            "LOGIN",  # 유효한 액션 타입
            '2025-07-29 10:00:00',
            1.0
        ))
        db_connection.commit()
        
        # 유효하지 않은 액션 타입으로 액션 생성 시도 - CheckViolation 예외가 발생해야 함
        with pytest.raises(CheckViolation):
            cur.execute("""
                INSERT INTO user_actions (user_id, action_type, timestamp, value)
                VALUES (%s, %s, %s, %s)
            """, (
                user_id,
                "INVALID_ACTION",  # 유효하지 않은 액션 타입
                '2025-07-29 10:00:00',
                1.0
            ))
            db_connection.commit()


# 파이썬 모듈 로드 시점에 글로벌 카운터 추가 (중복 테스트 시 사용)
# 테스트가 여러 번 실행되어도 카운터가 중복되지 않도록 처리
if not hasattr(pytest, "app_global_counter"):
    pytest.app_global_counter = 1
