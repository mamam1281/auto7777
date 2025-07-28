#!/usr/bin/env python3
"""
테스트 데이터 생성 스크립트
관리자 계정과 초대 코드, 테스트 사용자들을 생성합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import SessionLocal, engine, Base
from app import models
import random
import string

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_random_string(length: int = 8) -> str:
    """랜덤 문자열 생성"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_test_data():
    """테스트 데이터 생성"""
    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        print("🔧 테스트 데이터 생성 시작...")
        
        # 1. 초대 코드 생성
        invite_codes = ["WELCOME", "TEST123", "ADMIN01"]
        for code in invite_codes:
            existing = db.query(models.InviteCode).filter(models.InviteCode.code == code).first()
            if not existing:
                invite = models.InviteCode(code=code, is_used=False)
                db.add(invite)
                print(f"✅ 초대 코드 생성: {code}")
        
        # 2. 관리자 계정 생성
        admin_site_id = "admin"
        admin_user = db.query(models.User).filter(models.User.site_id == admin_site_id).first()
        if not admin_user:
            admin_user = models.User(
                site_id=admin_site_id,
                nickname="관리자",
                phone_number="010-0000-0000",
                password_hash=pwd_context.hash("admin123"),
                rank="ADMIN",
                cyber_token_balance=10000,
                invite_code="ADMIN01"
            )
            db.add(admin_user)
            print(f"✅ 관리자 계정 생성: {admin_site_id}")
        else:
            print(f"ℹ️  관리자 계정 이미 존재: {admin_site_id}")
        
        # 3. 테스트 사용자들 생성
        test_users = [
            {
                "site_id": "user001",
                "nickname": "테스트유저1",
                "phone_number": "010-1111-1111",
                "password": "test123",
                "rank": "STANDARD",
                "cyber_token_balance": 500
            },
            {
                "site_id": "user002", 
                "nickname": "VIP유저",
                "phone_number": "010-2222-2222",
                "password": "test123",
                "rank": "VIP",
                "cyber_token_balance": 2000
            },
            {
                "site_id": "user003",
                "nickname": "신규유저",
                "phone_number": "010-3333-3333", 
                "password": "test123",
                "rank": "STANDARD",
                "cyber_token_balance": 200
            }
        ]
        
        for user_data in test_users:
            existing = db.query(models.User).filter(models.User.site_id == user_data["site_id"]).first()
            if not existing:
                user = models.User(
                    site_id=user_data["site_id"],
                    nickname=user_data["nickname"],
                    phone_number=user_data["phone_number"],
                    password_hash=pwd_context.hash(user_data["password"]),
                    rank=user_data["rank"],
                    cyber_token_balance=user_data["cyber_token_balance"],
                    invite_code="WELCOME"
                )
                db.add(user)
                print(f"✅ 테스트 사용자 생성: {user_data['site_id']} ({user_data['nickname']})")
        
        # 4. 테스트 활동 로그 생성
        db.commit()
        
        # 사용자 ID들 가져오기
        users = db.query(models.User).all()
        user_ids = [user.id for user in users]
        
        # UserActivity 테이블 활동 로그 생성
        activities = [
            {"user_id": user_ids[0] if len(user_ids) > 0 else 1, "activity_type": "LOGIN", "details": "로그인"},
            {"user_id": user_ids[1] if len(user_ids) > 1 else 1, "activity_type": "GAME_PLAY", "details": "슬롯머신 게임 플레이"},
            {"user_id": user_ids[2] if len(user_ids) > 2 else 1, "activity_type": "SIGNUP", "details": "신규 회원가입"},
            {"user_id": user_ids[0] if len(user_ids) > 0 else 1, "activity_type": "REWARD_RECEIVED", "details": "일일 보상 수령"},
        ]
        
        for activity_data in activities:
            activity = models.UserActivity(
                user_id=activity_data["user_id"],
                activity_type=activity_data["activity_type"],
                details=activity_data["details"]
            )
            db.add(activity)
        
        print("✅ 테스트 활동 로그 생성")
        
        # 5. 보상 데이터 생성
        rewards = [
            {"user_id": user_ids[0] if len(user_ids) > 0 else 1, "reward_type": "CYBER_TOKEN", "amount": 100, "reason": "일일 출석 보상"},
            {"user_id": user_ids[1] if len(user_ids) > 1 else 1, "reward_type": "CYBER_TOKEN", "amount": 500, "reason": "VIP 보너스"},
        ]
        
        for reward_data in rewards:
            reward = models.Reward(
                user_id=reward_data["user_id"],
                reward_type=reward_data["reward_type"],
                amount=reward_data["amount"],
                reason=reward_data["reason"],
                admin_id=1  # 관리자 ID
            )
            db.add(reward)
        
        print("✅ 테스트 보상 데이터 생성")
        
        db.commit()
        
        print("\n🎉 테스트 데이터 생성 완료!")
        print("\n📋 생성된 계정 정보:")
        print("관리자 계정: site_id=admin, password=admin123")
        print("테스트 계정1: site_id=user001, password=test123")
        print("테스트 계정2: site_id=user002, password=test123")
        print("테스트 계정3: site_id=user003, password=test123")
        print("\n📋 초대 코드: WELCOME, TEST123, ADMIN01")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
