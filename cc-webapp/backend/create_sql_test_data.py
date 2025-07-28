#!/usr/bin/env python3
"""
최종 테스트 데이터 생성 스크립트
SQLite 데이터베이스에 직접 SQL로 테스트 데이터를 삽입합니다.
"""

import sqlite3
import hashlib
from datetime import datetime
from passlib.context import CryptContext

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_data_with_sql():
    """SQL을 사용하여 테스트 데이터를 직접 생성합니다."""
    print("🔧 SQL을 사용한 테스트 데이터 생성 시작...")
    
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()
    
    try:
        # 1. 초대 코드 테이블에 데이터 삽입
        invite_codes = [
            ("ADMIN1", False, datetime.utcnow().isoformat()),
            ("TEST01", False, datetime.utcnow().isoformat()),
            ("TEST02", False, datetime.utcnow().isoformat()),
            ("DEMO99", False, datetime.utcnow().isoformat())
        ]
        
        for code, is_used, created_at in invite_codes:
            cursor.execute("""
                INSERT OR IGNORE INTO invite_codes (code, is_used, created_at)
                VALUES (?, ?, ?)
            """, (code, is_used, created_at))
        
        print("✅ 초대 코드 생성 완료")
        
        # 2. 사용자 테이블에 관리자 및 테스트 사용자 삽입
        admin_password_hash = pwd_context.hash("admin123")
        test_password_hash = pwd_context.hash("test123")
        demo_password_hash = pwd_context.hash("demo123")
        
        users = [
            ("admin", "관리자", "010-0000-0000", admin_password_hash, "ADMIN1", 999999, "VIP", datetime.utcnow().isoformat()),
            ("testuser1", "테스트유저1", "010-1111-1111", test_password_hash, "TEST01", 1000, "PREMIUM", datetime.utcnow().isoformat()),
            ("testuser2", "테스트유저2", "010-2222-2222", test_password_hash, "TEST02", 500, "STANDARD", datetime.utcnow().isoformat()),
            ("demouser", "데모유저", "010-9999-9999", demo_password_hash, "DEMO99", 200, "STANDARD", datetime.utcnow().isoformat())
        ]
        
        for site_id, nickname, phone, password_hash, invite_code, balance, rank, created_at in users:
            cursor.execute("""
                INSERT OR IGNORE INTO users 
                (site_id, nickname, phone_number, password_hash, invite_code, cyber_token_balance, rank, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (site_id, nickname, phone, password_hash, invite_code, balance, rank, created_at))
        
        print("✅ 사용자 계정 생성 완료")
        
        # 변경사항 커밋
        conn.commit()
        
        # 생성된 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invite_codes")
        invite_count = cursor.fetchone()[0]
        
        print(f"\n📊 생성된 데이터 요약:")
        print(f"   • 사용자: {user_count}명")
        print(f"   • 초대코드: {invite_count}개")
        
        print(f"\n🎉 테스트 데이터 생성 완료!")
        print(f"📝 관리자 로그인 정보:")
        print(f"   • site_id: admin")
        print(f"   • password: admin123")
        print(f"📝 테스트 사용자:")
        print(f"   • site_id: testuser1, password: test123")
        print(f"   • site_id: testuser2, password: test123")
        print(f"   • site_id: demouser, password: demo123")
        
        # 생성된 사용자 목록 확인
        cursor.execute("SELECT site_id, nickname, rank, cyber_token_balance FROM users")
        users = cursor.fetchall()
        print(f"\n👥 생성된 사용자 목록:")
        for user in users:
            print(f"   • {user[0]} ({user[1]}) - {user[2]} 등급, {user[3]} 토큰")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_data_with_sql()
