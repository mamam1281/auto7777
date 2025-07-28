#!/usr/bin/env python3
"""
관리자 사용자 생성 스크립트
실제 상황과 동등한 환경을 위해 관리자 계정을 생성합니다.
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db, engine, Base
from app.models import User, InviteCode

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """관리자 사용자와 초대 코드를 생성합니다."""
    
    # 데이터베이스 테이블 생성
    print("데이터베이스 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    
    # 데이터베이스 세션 생성
    db = next(get_db())
    
    try:
        # 기존 관리자 사용자 확인
        existing_admin = db.query(User).filter(User.site_id == "admin").first()
        if existing_admin:
            print(f"관리자 사용자가 이미 존재합니다: {existing_admin.nickname}")
            return existing_admin
        
        # 초대 코드 생성
        invite_code = "ADMIN1"
        existing_invite = db.query(InviteCode).filter(InviteCode.code == invite_code).first()
        if not existing_invite:
            new_invite = InviteCode(code=invite_code, is_used=False)
            db.add(new_invite)
            print(f"초대 코드 생성: {invite_code}")
        
        # 관리자 사용자 생성
        admin_password = "admin123"  # 실제 배포시에는 더 강력한 비밀번호 사용
        password_hash = pwd_context.hash(admin_password)
        
        admin_user = User(
            site_id="admin",
            nickname="관리자",
            phone_number="010-0000-0000",
            password_hash=password_hash,
            invite_code=invite_code,
            cyber_token_balance=999999,
            rank="ADMIN"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 관리자 사용자 생성 완료!")
        print(f"   사이트ID: admin")
        print(f"   비밀번호: admin123")
        print(f"   닉네임: 관리자")
        print(f"   등급: ADMIN")
        print(f"   토큰: 999,999")
        print("")
        print("🚀 로그인 방법:")
        print("   1. http://localhost:3000/auth/login 접속")
        print("   2. 사이트ID: admin")
        print("   3. 비밀번호: admin123")
        print("   4. 로그인 후 관리자 메뉴 접근 가능")
        
        # 일반 테스트 사용자도 몇 명 생성
        create_test_users(db)
        
        return admin_user
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_test_users(db: Session):
    """테스트용 일반 사용자들을 생성합니다."""
    
    test_users = [
        {
            "site_id": "user001",
            "nickname": "테스트유저1",
            "phone_number": "010-1111-1111",
            "password": "test123",
            "rank": "STANDARD",
            "tokens": 1500
        },
        {
            "site_id": "user002", 
            "nickname": "VIP유저",
            "phone_number": "010-2222-2222",
            "password": "test123",
            "rank": "VIP",
            "tokens": 5000
        },
        {
            "site_id": "user003",
            "nickname": "프리미엄유저",
            "phone_number": "010-3333-3333", 
            "password": "test123",
            "rank": "PREMIUM",
            "tokens": 3000
        }
    ]
    
    for user_data in test_users:
        # 기존 사용자 확인
        existing_user = db.query(User).filter(User.site_id == user_data["site_id"]).first()
        if existing_user:
            continue
            
        # 초대 코드 생성
        invite_code = f"TEST{user_data['site_id'][-1]}"
        existing_invite = db.query(InviteCode).filter(InviteCode.code == invite_code).first()
        if not existing_invite:
            new_invite = InviteCode(code=invite_code, is_used=False)
            db.add(new_invite)
        
        # 사용자 생성
        password_hash = pwd_context.hash(user_data["password"])
        
        test_user = User(
            site_id=user_data["site_id"],
            nickname=user_data["nickname"],
            phone_number=user_data["phone_number"],
            password_hash=password_hash,
            invite_code=invite_code,
            cyber_token_balance=user_data["tokens"],
            rank=user_data["rank"]
        )
        
        db.add(test_user)
        print(f"   테스트 사용자 생성: {user_data['nickname']} ({user_data['rank']})")
    
    db.commit()
    print("✅ 테스트 사용자들 생성 완료!")

if __name__ == "__main__":
    print("🔧 Casino-Club 관리자 계정 설정 시작...")
    create_admin_user()
    print("🎉 설정 완료! 이제 관리자로 로그인할 수 있습니다.")
