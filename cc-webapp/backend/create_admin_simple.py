import sqlite3
import bcrypt

def create_admin_account():
    """간단한 관리자 계정 생성"""
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect('dev.db')
        cursor = conn.cursor()
        
        # 비밀번호 해시
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 관리자 계정 확인
        cursor.execute("SELECT * FROM users WHERE site_id = 'admin'")
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print("✅ 관리자 계정이 이미 존재합니다.")
            print(f"   ID: admin")
            print(f"   비밀번호: admin123")
        else:
            # 관리자 계정 생성
            cursor.execute("""
                INSERT INTO users (site_id, nickname, phone_number, password_hash, rank, cyber_token_balance, created_at)
                VALUES ('admin', '관리자', '010-0000-0000', ?, 'ADMIN', 10000, datetime('now'))
            """, (password_hash,))
            
            print("✅ 관리자 계정이 생성되었습니다!")
            print(f"   ID: admin")
            print(f"   비밀번호: admin123")
        
        # 테스트 사용자 계정 생성
        test_password_hash = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("SELECT * FROM users WHERE site_id = 'test'")
        existing_test = cursor.fetchone()
        
        if not existing_test:
            cursor.execute("""
                INSERT INTO users (site_id, nickname, phone_number, password_hash, rank, cyber_token_balance, created_at)
                VALUES ('test', '테스트유저', '010-1111-1111', ?, 'STANDARD', 1000, datetime('now'))
            """, (test_password_hash,))
            
            print("✅ 테스트 계정이 생성되었습니다!")
            print(f"   ID: test")
            print(f"   비밀번호: test123")
        
        conn.commit()
        conn.close()
        
        print("\n📋 관리자 기능 테스트 방법:")
        print("1. 프론트엔드에서 admin/admin123 또는 test/test123로 로그인")
        print("2. /admin 페이지로 이동")
        print("3. 사용자 관리, 보상 관리, 활동 로그 기능 테스트")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    create_admin_account()
