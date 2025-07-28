#!/usr/bin/env python3
"""
테스트 데이터 생성 스크립트
관리자 시스템 테스트를 위한 샘플 사용자와 활동 데이터를 생성합니다.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'cc-webapp', 'backend'))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, UserActivity, Reward
from app.models.admin import UserActivity as AdminUserActivity, Reward as AdminReward
from datetime import datetime, timedelta
import bcrypt

def create_test_data():
    db = SessionLocal()
    
    try:
        # 기존 테스트 데이터 정리 (옵션)
        print("기존 테스트 데이터 확인 중...")
        existing_users = db.query(User).filter(User.nickname.in_(['admin', 'testuser1', 'testuser2'])).all()
        if existing_users:
            print(f"기존 테스트 사용자 {len(existing_users)}명 발견됨")
        
        # 관리자 계정 생성
        admin_user = db.query(User).filter(User.nickname == 'admin').first()
        if not admin_user:
            print("관리자 계정 생성 중...")
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            admin_user = User(
                site_id='ADMIN001',
                nickname='admin',
                phone_number='010-0000-0000',
                password_hash=hashed_password.decode('utf-8'),
                cyber_token_balance=1000000,
                rank='ADMIN',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"관리자 계정 생성됨: ID {admin_user.id}")
        else:
            print(f"기존 관리자 계정 사용: ID {admin_user.id}")
        
        # 테스트 사용자들 생성
        test_users = []
        for i in range(1, 6):
            existing_user = db.query(User).filter(User.nickname == f'testuser{i}').first()
            if not existing_user:
                print(f"테스트 사용자 {i} 생성 중...")
                hashed_password = bcrypt.hashpw(f'password{i}'.encode('utf-8'), bcrypt.gensalt())
                test_user = User(
                    site_id=f'USER{i:03d}',
                    nickname=f'testuser{i}',
                    phone_number=f'010-1234-{i:04d}',
                    password_hash=hashed_password.decode('utf-8'),
                    cyber_token_balance=1000 + (i * 500),
                    rank='VIP' if i <= 2 else 'STANDARD',
                    created_at=datetime.now() - timedelta(days=i*5),
                    updated_at=datetime.now() - timedelta(days=1)
                )
                db.add(test_user)
                test_users.append(test_user)
            else:
                test_users.append(existing_user)
                print(f"기존 테스트 사용자 {i} 사용: ID {existing_user.id}")
        
        db.commit()
        
        # 활동 데이터 생성
        print("사용자 활동 데이터 생성 중...")
        activity_types = ['LOGIN', 'GAME_PLAY', 'REWARD_RECEIVED', 'PURCHASE', 'LOGOUT']
        
        for user in test_users:
            if user:
                for j in range(3):  # 각 사용자당 3개의 활동
                    activity = AdminUserActivity(
                        user_id=user.id,
                        activity_type=activity_types[j % len(activity_types)],
                        details=f'{user.nickname}의 {activity_types[j % len(activity_types)]} 활동',
                        timestamp=datetime.now() - timedelta(hours=j*2)
                    )
                    db.add(activity)
        
        # 보상 데이터 생성
        print("보상 데이터 생성 중...")
        for user in test_users[:3]:  # 처음 3명에게만 보상 지급
            if user:
                reward = AdminReward(
                    user_id=user.id,
                    reward_type='CYBER_TOKEN',
                    amount=100,
                    reason=f'{user.nickname}에게 지급된 테스트 보상',
                    admin_id=admin_user.id,
                    created_at=datetime.now() - timedelta(hours=12)
                )
                db.add(reward)
        
        db.commit()
        
        # 결과 확인
        total_users = db.query(User).count()
        total_activities = db.query(AdminUserActivity).count()
        total_rewards = db.query(AdminReward).count()
        
        print("\n=== 테스트 데이터 생성 완료 ===")
        print(f"총 사용자: {total_users}명")
        print(f"총 활동: {total_activities}개")
        print(f"총 보상: {total_rewards}개")
        print("\n=== 테스트 계정 정보 ===")
        print("관리자 계정: admin / admin123")
        print("일반 사용자: testuser1~5 / password1~5")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("관리자 시스템 테스트 데이터 생성을 시작합니다...")
    create_test_data()
    print("테스트 데이터 생성이 완료되었습니다!")
