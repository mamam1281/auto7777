#!/usr/bin/env python3
"""
관리자 권한 승격 스크립트
"""

import sys
import os
sys.path.append('/app')

from app.database import SessionLocal
from app.models.user import User

def promote_to_admin():
    db = SessionLocal()
    try:
        # admin_test_001 사용자 찾기
        user = db.query(User).filter(User.site_id == "admin_test_001").first()
        if user:
            print(f"✅ 사용자 발견: {user.nickname} (현재 권한: {user.rank})")
            user.rank = "ADMIN"
            db.commit()
            print(f"✅ 권한 업데이트 완료: {user.rank}")
        else:
            print("❌ admin_test_001 사용자를 찾을 수 없습니다.")
        
        # user_test_001도 확인
        user2 = db.query(User).filter(User.site_id == "user_test_001").first()
        if user2:
            print(f"✅ 일반 사용자 발견: {user2.nickname} (현재 권한: {user2.rank})")
        else:
            print("❌ user_test_001 사용자를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    promote_to_admin()
