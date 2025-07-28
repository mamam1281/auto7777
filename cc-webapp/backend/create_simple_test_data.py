#!/usr/bin/env python3
"""
간단한 테스트 데이터 생성 스크립트
관리자 계정과 테스트 사용자만 생성합니다.
"""

import sys
import os
from pathlib import Path

# 백엔드 디렉토리를 Python 경로에 추가
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

print(f"🔧 백엔드 디렉토리: {backend_dir}")

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    # models.py 파일에서 직접 import
    import sys
    sys.path.append('app')
    from models import Base, User, InviteCode, UserAction, UserReward
    from passlib.context import CryptContext
    from datetime import datetime, timedelta
    import secrets
    print("✅ 모든 모듈 가져오기 성공")
except ImportError as e:
    print(f"❌ 모듈 가져오기 실패: {e}")
    sys.exit(1)

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_simple_test_data():
    """간단한 테스트 데이터를 생성합니다."""
    print("🔧 테스트 데이터 생성 시작...")
    
    # 데이터베이스 연결
    DATABASE_URL = "sqlite:///./dev.db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. 초대 코드 생성
        invite_codes = ["ADMIN1", "TEST01", "TEST02", "DEMO99"]
        for code in invite_codes:
            existing = db.query(InviteCode).filter(InviteCode.code == code).first()
            if not existing:
                invite_code = InviteCode(code=code, is_used=False)
                db.add(invite_code)
        
        db.commit()
        print("✅ 초대 코드 생성 완료")
        
        # 2. 관리자 계정 생성
        admin_password = "admin123"
        admin_hash = pwd_context.hash(admin_password)
        
        existing_admin = db.query(User).filter(User.site_id == "admin").first()
        if not existing_admin:
            admin_user = User(
                site_id="admin",
                nickname="관리자",
                phone_number="010-0000-0000",
                password_hash=admin_hash,
                invite_code="ADMIN1",
                cyber_token_balance=999999,
                rank="VIP"
            )
            db.add(admin_user)
            db.commit()
            print("✅ 관리자 계정 생성 완료 (site_id: admin, password: admin123)")
        else:
            print("ℹ️ 관리자 계정이 이미 존재합니다.")
        
        # 3. 테스트 사용자 생성
        test_users = [
            {
                "site_id": "testuser1", 
                "nickname": "테스트유저1", 
                "phone_number": "010-1111-1111",
                "password": "test123",
                "invite_code": "TEST01",
                "balance": 1000,
                "rank": "PREMIUM"
            },
            {
                "site_id": "demouser", 
                "nickname": "데모유저", 
                "phone_number": "010-9999-9999",
                "password": "demo123",
                "invite_code": "DEMO99",
                "balance": 200,
                "rank": "STANDARD"
            }
        ]
        
        for user_data in test_users:
            existing_user = db.query(User).filter(User.site_id == user_data["site_id"]).first()
            if not existing_user:
                user_hash = pwd_context.hash(user_data["password"])
                test_user = User(
                    site_id=user_data["site_id"],
                    nickname=user_data["nickname"],
                    phone_number=user_data["phone_number"],
                    password_hash=user_hash,
                    invite_code=user_data["invite_code"],
                    cyber_token_balance=user_data["balance"],
                    rank=user_data["rank"]
                )
                db.add(test_user)
        
        db.commit()
        print("✅ 테스트 사용자 생성 완료")
        
        # 4. 생성된 데이터 확인
        user_count = db.query(User).count()
        invite_count = db.query(InviteCode).count()
        
        print(f"\n📊 생성된 데이터 요약:")
        print(f"   • 사용자: {user_count}명")
        print(f"   • 초대코드: {invite_count}개")
        
        print(f"\n🎉 테스트 데이터 생성 완료!")
        print(f"📝 관리자 로그인 정보:")
        print(f"   • site_id: admin")
        print(f"   • password: admin123")
        print(f"📝 테스트 사용자:")
        print(f"   • site_id: testuser1, password: test123")
        print(f"   • site_id: demouser, password: demo123")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_test_data()
