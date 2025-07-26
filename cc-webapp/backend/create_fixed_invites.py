"""
고정 초대코드 생성 스크립트
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy.orm import sessionmaker
from app.models import InviteCode
from app.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_fixed_invite_codes():
    """고정 초대코드 3개 생성"""
    print("🎫 고정 초대코드 생성 시작")
    
    fixed_codes = ["5882", "6969", "6974"]
    
    db = SessionLocal()
    try:
        for code in fixed_codes:
            # 이미 존재하는지 확인
            existing = db.query(InviteCode).filter(InviteCode.code == code).first()
            if existing:
                print(f"   ℹ️ {code} - 이미 존재함")
            else:
                # 새로 생성
                invite = InviteCode(code=code, is_used=False)
                db.add(invite)
                print(f"   ✅ {code} - 새로 생성")
        
        db.commit()
        print("🎉 고정 초대코드 설정 완료!")
        
        # 현재 모든 초대코드 확인
        all_codes = db.query(InviteCode).all()
        print(f"\n📋 현재 초대코드 목록 ({len(all_codes)}개):")
        for invite in all_codes:
            status = "사용됨" if invite.is_used else "미사용"
            print(f"   - {invite.code} ({status})")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_fixed_invite_codes()
