"""
수정된 인증 API 로직 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# 모델과 데이터베이스 임포트
from app.models import User, Base, InviteCode
from app.database import get_db

# 테스트용 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# bcrypt 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_signup_logic():
    """회원가입 로직 테스트"""
    print("\n=== 📝 회원가입 테스트 ===")
    
    db = SessionLocal()
    try:
        # 1. 초대코드 생성
        invite_code = InviteCode(code="TEST01", is_used=False)
        db.add(invite_code)
        db.commit()
        print("✅ 초대코드 생성: TEST01")
        
        # 2. 회원가입 데이터
        signup_data = {
            "site_id": "user123",
            "nickname": "테스트유저",
            "phone_number": "010-1234-5678",
            "password": "password123",
            "invite_code": "TEST01"
        }
        
        # 3. 중복 검사
        existing_site_id = db.query(User).filter(User.site_id == signup_data["site_id"]).first()
        existing_nickname = db.query(User).filter(User.nickname == signup_data["nickname"]).first()
        existing_phone = db.query(User).filter(User.phone_number == signup_data["phone_number"]).first()
        
        if existing_site_id:
            print("❌ 사이트ID 중복!")
            return False
        if existing_nickname:
            print("❌ 닉네임 중복!")
            return False
        if existing_phone:
            print("❌ 전화번호 중복!")
            return False
        print("✅ 중복 검사 통과")
        
        # 4. 초대코드 검증
        invite = db.query(InviteCode).filter(
            InviteCode.code == signup_data["invite_code"],
            InviteCode.is_used == False
        ).first()
        if not invite:
            print("❌ 초대코드 무효!")
            return False
        print("✅ 초대코드 유효")
        
        # 5. 비밀번호 해싱
        password_hash = pwd_context.hash(signup_data["password"])
        print(f"✅ 비밀번호 해싱 완료: {password_hash[:30]}...")
        
        # 6. 사용자 생성
        user = User(
            site_id=signup_data["site_id"],
            nickname=signup_data["nickname"],
            phone_number=signup_data["phone_number"],
            password_hash=password_hash,
            invite_code=signup_data["invite_code"]
        )
        db.add(user)
        invite.is_used = True
        db.commit()
        db.refresh(user)
        
        print(f"✅ 사용자 생성 완료!")
        print(f"   - ID: {user.id}")
        print(f"   - 사이트ID: {user.site_id}")
        print(f"   - 닉네임: {user.nickname}")
        print(f"   - 전화번호: {user.phone_number}")
        print(f"   - 생성일: {user.created_at}")
        
        return user
    
    except Exception as e:
        print(f"❌ 회원가입 오류: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_login_logic(site_id: str = "user123", password: str = "password123"):
    """로그인 로직 테스트"""
    print(f"\n=== 🔐 로그인 테스트 (사이트ID: {site_id}) ===")
    
    db = SessionLocal()
    try:
        # 1. 사이트ID로 사용자 찾기
        user = db.query(User).filter(User.site_id == site_id).first()
        if not user:
            print("❌ 사용자를 찾을 수 없습니다")
            return False
        print(f"✅ 사용자 발견: {user.nickname}")
        
        # 2. 비밀번호 검증
        if not user.password_hash:
            print("❌ 비밀번호 해시가 없습니다")
            return False
        
        if not pwd_context.verify(password, user.password_hash):
            print("❌ 비밀번호가 틀렸습니다")
            return False
        
        print("✅ 비밀번호 검증 성공")
        print(f"   - 사용자 ID: {user.id}")
        print(f"   - 닉네임: {user.nickname}")
        print(f"   - 전화번호: {user.phone_number}")
        
        return user
    
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return False
    finally:
        db.close()

def main():
    print("🎯 새로운 인증 시스템 테스트 시작")
    print("=" * 50)
    
    # 회원가입 테스트
    user = test_signup_logic()
    if not user:
        print("\n❌ 회원가입 테스트 실패!")
        return
    
    # 로그인 테스트 (올바른 비밀번호)
    login_success = test_login_logic("user123", "password123")
    if not login_success:
        print("\n❌ 로그인 테스트 실패!")
        return
    
    # 로그인 테스트 (잘못된 비밀번호)
    print("\n=== 🔐 잘못된 비밀번호 테스트 ===")
    login_fail = test_login_logic("user123", "wrongpassword")
    if login_fail:
        print("❌ 잘못된 비밀번호로 로그인 성공 (오류!)")
        return
    
    print("\n🎉 모든 테스트 성공!")
    print("✅ 회원가입: 사이트ID + 닉네임 + 전화번호 + 비밀번호")
    print("✅ 로그인: 사이트ID + 비밀번호 검증")
    print("✅ 비밀번호 해싱 및 검증")

if __name__ == "__main__":
    main()
