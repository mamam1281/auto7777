#!/usr/bin/env python3
"""
테스트 데이터 생성 스크립트 (수정된 버전)
관리자 계정과 테스트 사용자 데이터를 생성합니다.
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
    from app import models
    from app.database import Base
    from passlib.context import CryptContext
    from datetime import datetime, timedelta
    import secrets
    print("✅ 모든 모듈 가져오기 성공")
except ImportError as e:
    print(f"❌ 모듈 가져오기 실패: {e}")
    sys.exit(1)

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_data():
    """테스트 데이터를 생성합니다."""
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
        invite_codes = ["ADMIN1", "TEST01", "TEST02", "TEST03", "DEMO99"]
        for code in invite_codes:
            existing = db.query(models.InviteCode).filter(models.InviteCode.code == code).first()
            if not existing:
                invite_code = models.InviteCode(code=code, is_used=False)
                db.add(invite_code)
        
        db.commit()
        print("✅ 초대 코드 생성 완료")
        
        # 2. 관리자 계정 생성
        admin_password = "admin123"
        admin_hash = pwd_context.hash(admin_password)
        
        existing_admin = db.query(models.User).filter(models.User.site_id == "admin").first()
        if not existing_admin:
            admin_user = models.User(
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
                "site_id": "testuser2", 
                "nickname": "테스트유저2", 
                "phone_number": "010-2222-2222",
                "password": "test123",
                "invite_code": "TEST02", 
                "balance": 500,
                "rank": "STANDARD"
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
            existing_user = db.query(models.User).filter(models.User.site_id == user_data["site_id"]).first()
            if not existing_user:
                user_hash = pwd_context.hash(user_data["password"])
                test_user = models.User(
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
        
        # 4. 사용자 활동 데이터 생성
        users = db.query(models.User).all()
        for user in users:
            # 사용자 행동 데이터
            actions = [
                {"action_type": "login", "value": 0.0},
                {"action_type": "game_play", "value": 100.0},
                {"action_type": "purchase", "value": 50.0}
            ]
            
            for action_data in actions:
                action = models.UserAction(
                    user_id=user.id,
                    action_type=action_data["action_type"],
                    value=action_data["value"],
                    timestamp=datetime.utcnow() - timedelta(hours=secrets.randbelow(72))
                )
                db.add(action)
            
            # 사용자 리워드 데이터
            rewards = [
                {"reward_type": "cyber_token", "reward_value": "100", "source_description": "가입 보너스"},
                {"reward_type": "premium_access", "reward_value": "1일", "source_description": "이벤트 참여"}
            ]
            
            for reward_data in rewards:
                reward = models.UserReward(
                    user_id=user.id,
                    reward_type=reward_data["reward_type"],
                    reward_value=reward_data["reward_value"],
                    source_description=reward_data["source_description"],
                    awarded_at=datetime.utcnow() - timedelta(hours=secrets.randbelow(48))
                )
                db.add(reward)
        
        db.commit()
        print("✅ 사용자 활동 및 리워드 데이터 생성 완료")
        
        # 5. 생성된 데이터 확인
        user_count = db.query(models.User).count()
        invite_count = db.query(models.InviteCode).count()
        action_count = db.query(models.UserAction).count()
        reward_count = db.query(models.UserReward).count()
        
        print(f"\n📊 생성된 데이터 요약:")
        print(f"   • 사용자: {user_count}명")
        print(f"   • 초대코드: {invite_count}개")
        print(f"   • 사용자 활동: {action_count}건")
        print(f"   • 리워드: {reward_count}건")
        
        print(f"\n🎉 테스트 데이터 생성 완료!")
        print(f"📝 관리자 로그인 정보:")
        print(f"   • site_id: admin")
        print(f"   • password: admin123")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
