"""
ACID 트랜잭션 및 동시성 제어 테스트
"""
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_SERIALIZABLE
from psycopg2.errors import SerializationFailure
import threading
import time
import random
from datetime import datetime

def test_transaction_atomicity(db_connection, clean_tables, create_test_user):
    """
    트랜잭션의 원자성(Atomicity) 검증: 
    트랜잭션 내의 모든 작업이 성공하거나 모두 실패해야 함
    """
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    with db_connection.cursor() as cur:
        try:
            # 트랜잭션 시작
            cur.execute("BEGIN")
            
            # 첫 번째 작업: 세그먼트 생성
            cur.execute("""
                INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
                VALUES (%s, %s, %s, %s)
            """, (user_id, "Whale", "High", "test_segment"))
            
            # 두 번째 작업: 잘못된 SQL 구문으로 에러 발생
            cur.execute("""
                INSERT INTO non_existent_table (column1, column2)
                VALUES (1, 2)
            """)
            
            # 커밋 - 이 부분은 실행되지 않아야 함
            db_connection.commit()
        except Exception as e:
            # 에러 발생 시 롤백
            db_connection.rollback()
    
    # 세그먼트가 생성되지 않았는지 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM user_segments WHERE user_id = %s", (user_id,))
        count = cur.fetchone()[0]
        assert count == 0, "트랜잭션이 롤백되어야 하지만 세그먼트가 생성되었습니다."


def test_transaction_consistency(db_connection, clean_tables, create_test_user):
    """
    트랜잭션의 일관성(Consistency) 검증: 
    제약 조건이 트랜잭션 전후에 유지되어야 함
    """
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    # 초기 상태 확인 - 사용자 랭크 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT rank FROM users WHERE id = %s", (user_id,))
        initial_rank = cur.fetchone()[0]
        assert initial_rank == "STANDARD", "초기 사용자 랭크가 STANDARD가 아닙니다."
    
    # 트랜잭션 내에서 유효한 랭크로 업데이트 - 성공해야 함
    with db_connection.cursor() as cur:
        cur.execute("BEGIN")
        cur.execute("UPDATE users SET rank = %s WHERE id = %s", ("VIP", user_id))
        db_connection.commit()
    
    # 랭크가 업데이트되었는지 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT rank FROM users WHERE id = %s", (user_id,))
        updated_rank = cur.fetchone()[0]
        assert updated_rank == "VIP", "사용자 랭크가 VIP로 업데이트되지 않았습니다."
    
    # 트랜잭션 내에서 유효하지 않은 랭크로 업데이트 시도 - 실패해야 함
    with db_connection.cursor() as cur:
        cur.execute("BEGIN")
        try:
            cur.execute("UPDATE users SET rank = %s WHERE id = %s", ("INVALID_RANK", user_id))
            db_connection.commit()
            assert False, "유효하지 않은 랭크로 업데이트가 성공하면 안됩니다."
        except Exception:
            db_connection.rollback()
    
    # 랭크가 여전히 VIP인지 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT rank FROM users WHERE id = %s", (user_id,))
        final_rank = cur.fetchone()[0]
        assert final_rank == "VIP", "사용자 랭크가 여전히 VIP여야 합니다."


def test_transaction_isolation(db_connection, clean_tables, create_test_user):
    """
    트랜잭션의 격리성(Isolation) 검증: 
    동시 트랜잭션이 서로에게 영향을 미치지 않아야 함
    """
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    # 두 개의 연결 생성
    conn1 = psycopg2.connect(**{
        'dbname': 'cc_webapp',
        'user': 'cc_user',
        'password': 'cc_password',
        'host': 'localhost',
        'port': 5432
    })
    conn1.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
    
    conn2 = psycopg2.connect(**{
        'dbname': 'cc_webapp',
        'user': 'cc_user',
        'password': 'cc_password',
        'host': 'localhost',
        'port': 5432
    })
    conn2.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
    
    try:
        # 첫 번째 연결에서 트랜잭션 시작하고 데이터 변경
        with conn1.cursor() as cur1:
            cur1.execute("BEGIN")
            cur1.execute("UPDATE users SET rank = %s WHERE id = %s", ("VIP", user_id))
            
            # 두 번째 연결에서 데이터 읽기 시도 - READ_COMMITTED에서는 변경 전 데이터를 봐야 함
            with conn2.cursor() as cur2:
                cur2.execute("SELECT rank FROM users WHERE id = %s", (user_id,))
                rank_before_commit = cur2.fetchone()[0]
                assert rank_before_commit == "STANDARD", "커밋되지 않은 변경 사항이 다른 트랜잭션에 보입니다."
            
            # 첫 번째 트랜잭션 커밋
            conn1.commit()
            
            # 두 번째 연결에서 다시 데이터 읽기 - 이제 변경된 데이터를 봐야 함
            with conn2.cursor() as cur2:
                cur2.execute("SELECT rank FROM users WHERE id = %s", (user_id,))
                rank_after_commit = cur2.fetchone()[0]
                assert rank_after_commit == "VIP", "커밋된 변경 사항이 다른 트랜잭션에 보이지 않습니다."
    finally:
        # 연결 종료
        conn1.close()
        conn2.close()


def test_transaction_durability(db_connection, clean_tables, create_test_user):
    """
    트랜잭션의 지속성(Durability) 검증: 
    커밋된 트랜잭션은 영구적으로 반영되어야 함
    """
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    # 트랜잭션 내에서 세그먼트와 액션 생성
    with db_connection.cursor() as cur:
        cur.execute("BEGIN")
        
        # 세그먼트 생성
        cur.execute("""
            INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
            VALUES (%s, %s, %s, %s)
        """, (user_id, "Whale", "High", "test_segment"))
        
        # 액션 생성
        cur.execute("""
            INSERT INTO user_actions (user_id, action_type, timestamp, value)
            VALUES (%s, %s, %s, %s)
        """, (user_id, "LOGIN", datetime.now(), 1.0))
        
        # 커밋
        db_connection.commit()
    
    # 새 연결 생성하여 데이터가 지속되었는지 확인
    new_conn = psycopg2.connect(**{
        'dbname': 'cc_webapp',
        'user': 'cc_user',
        'password': 'cc_password',
        'host': 'localhost',
        'port': 5432
    })
    
    try:
        with new_conn.cursor() as cur:
            # 세그먼트 확인
            cur.execute("SELECT COUNT(*) FROM user_segments WHERE user_id = %s", (user_id,))
            segment_count = cur.fetchone()[0]
            assert segment_count == 1, "커밋된 세그먼트 데이터가 지속되지 않았습니다."
            
            # 액션 확인
            cur.execute("SELECT COUNT(*) FROM user_actions WHERE user_id = %s", (user_id,))
            action_count = cur.fetchone()[0]
            assert action_count == 1, "커밋된 액션 데이터가 지속되지 않았습니다."
    finally:
        new_conn.close()


def test_concurrent_user_updates(db_connection, clean_tables, create_test_user):
    """
    동시성 제어: 여러 스레드가 동일한 사용자 정보를 동시에 업데이트할 때 
    경쟁 상태(race condition)가 발생하지 않아야 함
    """
    # 사용자 생성
    user = create_test_user()
    user_id = user['id']
    
    # 초기 값 설정 - phone_number를 테스트에 사용
    initial_phone = "010-0000-0000"
    with db_connection.cursor() as cur:
        cur.execute("UPDATE users SET phone_number = %s WHERE id = %s", (initial_phone, user_id))
        db_connection.commit()
    
    # 업데이트 함수 정의
    def update_phone_number(user_id, new_phone, sleep_time=0.1):
        conn = psycopg2.connect(**{
            'dbname': 'cc_webapp',
            'user': 'cc_user',
            'password': 'cc_password',
            'host': 'localhost',
            'port': 5432
        })
        try:
            # 트랜잭션 시작
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                
                # 현재 값 읽기
                cur.execute("SELECT phone_number FROM users WHERE id = %s FOR UPDATE", (user_id,))
                current_phone = cur.fetchone()[0]
                
                # 잠시 대기하여 경쟁 조건 시뮬레이션
                time.sleep(sleep_time)
                
                # 새 값으로 업데이트
                cur.execute("UPDATE users SET phone_number = %s WHERE id = %s", (new_phone, user_id))
                
                # 커밋
                conn.commit()
                return current_phone
        except Exception as e:
            conn.rollback()
            return str(e)
        finally:
            conn.close()
    
    # 여러 스레드에서 동시에 업데이트
    thread1 = threading.Thread(target=update_phone_number, args=(user_id, "010-1111-1111", 0.2))
    thread2 = threading.Thread(target=update_phone_number, args=(user_id, "010-2222-2222", 0.1))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    # 최종 값 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT phone_number FROM users WHERE id = %s", (user_id,))
        final_phone = cur.fetchone()[0]
        
        # 어떤 스레드가 마지막으로 실행되었는지에 따라 결과가 달라질 수 있음
        # 하지만 일관성은 유지되어야 함
        assert final_phone in ["010-1111-1111", "010-2222-2222"], f"예상치 못한 전화번호: {final_phone}"


def test_deadlock_prevention(db_connection, clean_tables, create_test_user):
    """
    데드락 방지 및 처리: 두 트랜잭션이 서로 다른 순서로 리소스를 요청할 때
    데드락을 감지하고 적절히 처리해야 함
    """
    # 두 사용자 생성
    user1 = create_test_user(nickname="deadlock_user1")
    user2 = create_test_user(nickname="deadlock_user2")
    
    user1_id = user1['id']
    user2_id = user2['id']
    
    # 데드락 시뮬레이션 함수
    def transaction_scenario(first_user_id, second_user_id, sleep_time=0.5):
        conn = psycopg2.connect(**{
            'dbname': 'cc_webapp',
            'user': 'cc_user',
            'password': 'cc_password',
            'host': 'localhost',
            'port': 5432
        })
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        
        try:
            with conn.cursor() as cur:
                # 첫 번째 리소스 잠금
                cur.execute("BEGIN")
                cur.execute("SELECT * FROM users WHERE id = %s FOR UPDATE", (first_user_id,))
                
                # 잠시 대기하여 다른 트랜잭션이 두 번째 리소스를 잠글 시간 제공
                time.sleep(sleep_time)
                
                # 두 번째 리소스 잠금 시도
                cur.execute("SELECT * FROM users WHERE id = %s FOR UPDATE", (second_user_id,))
                
                # 업데이트 작업
                cur.execute("UPDATE users SET phone_number = %s WHERE id = %s", 
                           (f"010-updated-{first_user_id}", first_user_id))
                cur.execute("UPDATE users SET phone_number = %s WHERE id = %s", 
                           (f"010-updated-{second_user_id}", second_user_id))
                
                # 커밋
                conn.commit()
                return "Success"
        except Exception as e:
            conn.rollback()
            return str(e)
        finally:
            conn.close()
    
    # 두 스레드에서 서로 다른 순서로 리소스 요청
    thread1 = threading.Thread(target=transaction_scenario, args=(user1_id, user2_id, 0.5))
    thread2 = threading.Thread(target=transaction_scenario, args=(user2_id, user1_id, 0.2))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    # 데드락이 발생하면 PostgreSQL이 자동으로 한 트랜잭션을 취소함
    # 그래서 두 사용자 중 하나는 업데이트되고 다른 하나는 원래 값을 유지해야 함
    # 여기서는 구체적인 결과를 검증하기보다 시스템이 크래시 없이 계속 작동하는지 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT phone_number FROM users WHERE id IN (%s, %s)", (user1_id, user2_id))
        phone_numbers = [row[0] for row in cur.fetchall()]
        
        # 적어도 하나의 전화번호는 업데이트되었거나, 둘 다 원래 값을 유지해야 함
        assert any(pn.startswith("010-updated-") for pn in phone_numbers) or \
               all(pn == "010-0000-0000" for pn in phone_numbers), \
               f"예상치 못한 전화번호: {phone_numbers}"
