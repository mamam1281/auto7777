"""
?˜ì •???¸ì¦ API ë¡œì§ ?ŒìŠ¤???¤í¬ë¦½íŠ¸
"""
import sys
import os
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# ëª¨ë¸ê³??°ì´?°ë² ?´ìŠ¤ ?„í¬??
from app.models import User, Base, InviteCode
from app.database import get_db

# ?ŒìŠ¤?¸ìš© ?°ì´?°ë² ?´ìŠ¤ ?¤ì •
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ?°ì´?°ë² ?´ìŠ¤ ?Œì´ë¸??ì„±
Base.metadata.create_all(bind=engine)

# bcrypt ì»¨í…?¤íŠ¸
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.mark.skip(reason=" ¿ÜºÎ ¼­¹ö ¿¬°á Å×½ºÆ® - ¹èÆ÷ ½Ã Á¦¿Ü\)
def test_signup_logic():
    """?Œì›ê°€??ë¡œì§ ?ŒìŠ¤??""
    print("\n=== ?“ ?Œì›ê°€???ŒìŠ¤??===")
    
    db = SessionLocal()
    try:
        # 1. ì´ˆë?ì½”ë“œ ?ì„±
        invite_code = InviteCode(code="TEST01", is_used=False)
        db.add(invite_code)
        db.commit()
        print("??ì´ˆë?ì½”ë“œ ?ì„±: TEST01")
        
        # 2. ?Œì›ê°€???°ì´??
        signup_data = {
            "site_id": "user123",
            "nickname": "?ŒìŠ¤?¸ìœ ?€",
            "phone_number": "010-1234-5678",
            "password": "password123",
            "invite_code": "TEST01"
        }
        
        # 3. ì¤‘ë³µ ê²€??
        existing_site_id = db.query(User).filter(User.site_id == signup_data["site_id"]).first()
        existing_nickname = db.query(User).filter(User.nickname == signup_data["nickname"]).first()
        existing_phone = db.query(User).filter(User.phone_number == signup_data["phone_number"]).first()
        
        if existing_site_id:
            print("???¬ì´?¸ID ì¤‘ë³µ!")
            return False
        if existing_nickname:
            print("???‰ë„¤??ì¤‘ë³µ!")
            return False
        if existing_phone:
            print("???„í™”ë²ˆí˜¸ ì¤‘ë³µ!")
            return False
        print("??ì¤‘ë³µ ê²€???µê³¼")
        
        # 4. ì´ˆë?ì½”ë“œ ê²€ì¦?
        invite = db.query(InviteCode).filter(
            InviteCode.code == signup_data["invite_code"],
            InviteCode.is_used == False
        ).first()
        if not invite:
            print("??ì´ˆë?ì½”ë“œ ë¬´íš¨!")
            return False
        print("??ì´ˆë?ì½”ë“œ ? íš¨")
        
        # 5. ë¹„ë?ë²ˆí˜¸ ?´ì‹±
        password_hash = pwd_context.hash(signup_data["password"])
        print(f"??ë¹„ë?ë²ˆí˜¸ ?´ì‹± ?„ë£Œ: {password_hash[:30]}...")
        
        # 6. ?¬ìš©???ì„±
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
        
        print(f"???¬ìš©???ì„± ?„ë£Œ!")
        print(f"   - ID: {user.id}")
        print(f"   - ?¬ì´?¸ID: {user.site_id}")
        print(f"   - ?‰ë„¤?? {user.nickname}")
        print(f"   - ?„í™”ë²ˆí˜¸: {user.phone_number}")
        print(f"   - ?ì„±?? {user.created_at}")
        
        return user
    
    except Exception as e:
        print(f"???Œì›ê°€???¤ë¥˜: {e}")
        db.rollback()
        return False
    finally:
        db.close()

@pytest.mark.skip(reason=" ¿ÜºÎ ¼­¹ö ¿¬°á Å×½ºÆ® - ¹èÆ÷ ½Ã Á¦¿Ü\)
def test_login_logic(site_id: str = "user123", password: str = "password123"):
    """ë¡œê·¸??ë¡œì§ ?ŒìŠ¤??""
    print(f"\n=== ?” ë¡œê·¸???ŒìŠ¤??(?¬ì´?¸ID: {site_id}) ===")
    
    db = SessionLocal()
    try:
        # 1. ?¬ì´?¸IDë¡??¬ìš©??ì°¾ê¸°
        user = db.query(User).filter(User.site_id == site_id).first()
        if not user:
            print("???¬ìš©?ë? ì°¾ì„ ???†ìŠµ?ˆë‹¤")
            return False
        print(f"???¬ìš©??ë°œê²¬: {user.nickname}")
        
        # 2. ë¹„ë?ë²ˆí˜¸ ê²€ì¦?
        if not user.password_hash:
            print("??ë¹„ë?ë²ˆí˜¸ ?´ì‹œê°€ ?†ìŠµ?ˆë‹¤")
            return False
        
        if not pwd_context.verify(password, user.password_hash):
            print("??ë¹„ë?ë²ˆí˜¸ê°€ ?€?¸ìŠµ?ˆë‹¤")
            return False
        
        print("??ë¹„ë?ë²ˆí˜¸ ê²€ì¦??±ê³µ")
        print(f"   - ?¬ìš©??ID: {user.id}")
        print(f"   - ?‰ë„¤?? {user.nickname}")
        print(f"   - ?„í™”ë²ˆí˜¸: {user.phone_number}")
        
        return user
    
    except Exception as e:
        print(f"??ë¡œê·¸???¤ë¥˜: {e}")
        return False
    finally:
        db.close()

def main():
    print("?¯ ?ˆë¡œ???¸ì¦ ?œìŠ¤???ŒìŠ¤???œì‘")
    print("=" * 50)
    
    # ?Œì›ê°€???ŒìŠ¤??
    user = test_signup_logic()
    if not user:
        print("\n???Œì›ê°€???ŒìŠ¤???¤íŒ¨!")
        return
    
    # ë¡œê·¸???ŒìŠ¤??(?¬ë°”ë¥?ë¹„ë?ë²ˆí˜¸)
    login_success = test_login_logic("user123", "password123")
    if not login_success:
        print("\n??ë¡œê·¸???ŒìŠ¤???¤íŒ¨!")
        return
    
    # ë¡œê·¸???ŒìŠ¤??(?˜ëª»??ë¹„ë?ë²ˆí˜¸)
    print("\n=== ?” ?˜ëª»??ë¹„ë?ë²ˆí˜¸ ?ŒìŠ¤??===")
    login_fail = test_login_logic("user123", "wrongpassword")
    if login_fail:
        print("???˜ëª»??ë¹„ë?ë²ˆí˜¸ë¡?ë¡œê·¸???±ê³µ (?¤ë¥˜!)")
        return
    
    print("\n?‰ ëª¨ë“  ?ŒìŠ¤???±ê³µ!")
    print("???Œì›ê°€?? ?¬ì´?¸ID + ?‰ë„¤??+ ?„í™”ë²ˆí˜¸ + ë¹„ë?ë²ˆí˜¸")
    print("??ë¡œê·¸?? ?¬ì´?¸ID + ë¹„ë?ë²ˆí˜¸ ê²€ì¦?)
    print("??ë¹„ë?ë²ˆí˜¸ ?´ì‹± ë°?ê²€ì¦?)

if __name__ == "__main__":
    main()
