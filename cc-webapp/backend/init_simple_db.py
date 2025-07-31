"""
간단한 SQLite 데이터베이스 초기화 스크립트
"""
import sqlite3
import os

DB_PATH = "auth.db"

def init_database():
    """데이터베이스 테이블 생성 및 초기 데이터 입력"""
    
    # 기존 데이터베이스 삭제
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"기존 데이터베이스 {DB_PATH} 삭제됨")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 사용자 테이블 생성
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT UNIQUE NOT NULL,
        nickname TEXT UNIQUE NOT NULL,
        phone_number TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        invite_code TEXT NOT NULL,
        cyber_token_balance INTEGER DEFAULT 200,
        rank TEXT DEFAULT 'STANDARD',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login_at TIMESTAMP
    )
    """)
    
    # 초대 코드 테이블 생성
    cursor.execute("""
    CREATE TABLE invite_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        used_at TIMESTAMP
    )
    """)
    
    # 초기 초대 코드들 생성
    invite_codes = [
        "WELCOME2024",
        "TEST123",
        "CASINO777",
        "LUCKY888",
        "BONUS999"
    ]
    
    for code in invite_codes:
        cursor.execute("INSERT INTO invite_codes (code) VALUES (?)", (code,))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 데이터베이스 {DB_PATH} 초기화 완료")
    print(f"✅ 초대 코드 {len(invite_codes)}개 생성됨: {', '.join(invite_codes)}")

if __name__ == "__main__":
    init_database()
