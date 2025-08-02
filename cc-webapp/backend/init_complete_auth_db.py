"""
새로운 사용자 모델로 데이터베이스 초기화
회원가입 필수 입력사항: 초대코드, 사이트아이디, 닉네임, 폰번호, 비밀번호
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models.auth_models import User
from app.models.invite_code import InviteCode
from app.services.auth_service import AuthService
from sqlalchemy.orm import Session

def init_database():
    """데이터베이스 초기화"""
    print("🔄 데이터베이스 초기화 시작...")
    
    # 모든 테이블 삭제 후 재생성
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블 생성 완료")
    
    # 세션 생성
    db = SessionLocal()
    
    try:
        # 관리자 계정 생성
        admin_user = User(
            site_id="admin",
            nickname="관리자",
            phone_number="01000000000",
            hashed_password=AuthService.get_password_hash("admin123"),
            full_name="시스템 관리자",
            invite_code="5858",
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # 초대코드 생성 (무제한 사용)
        invite_code = InviteCode(
            code="5858",
            created_by=admin_user.id,
            max_uses=999999,
            current_uses=0,
            is_active=True
        )
        db.add(invite_code)
        
        # 테스트 사용자 생성
        test_user = User(
            site_id="testuser",
            nickname="테스터",
            phone_number="01012345678",
            hashed_password=AuthService.get_password_hash("test123"),
            full_name="테스트 사용자",
            invite_code="5858",
            is_admin=False,
            is_active=True
        )
        db.add(test_user)
        
        db.commit()
        print("✅ 관리자 계정 생성 완료: admin / admin123")
        print("✅ 초대코드 생성 완료: 5858 (무제한)")
        print("✅ 테스트 계정 생성 완료: testuser / test123")
        print("   - 닉네임: 테스터")
        print("   - 폰번호: 01012345678")
        print("🎉 데이터베이스 초기화 완료!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
