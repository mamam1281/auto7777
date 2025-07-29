"""
테스트 데이터 생성 도구
"""

import os
import sys
import random
import datetime
import argparse
from pathlib import Path

# 프로젝트 루트 디렉토리 추가 (상대 경로 임포트용)
sys.path.append(str(Path(__file__).parent.resolve()))

# 데이터베이스 세션 및 모델 임포트
from app.db.session import get_db, engine
from app.models.user import User
from app.models.game import UserAction, UserReward, UserStreak
from app.models.base import Base
from app.core.security import get_password_hash


def create_test_data(num_users=50, reset_db=False):
    """테스트 데이터를 생성하는 함수"""
    # DB 세션 가져오기
    db = next(get_db())
    
    # DB 리셋 옵션
    if reset_db:
        print("데이터베이스 초기화 중...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    # 사용자 데이터 생성
    print(f"{num_users}명의 테스트 사용자 생성 중...")
    users = []
    ranks = ["STANDARD", "PREMIUM", "VIP"]
    
    for i in range(1, num_users + 1):
        # 랜덤 데이터 생성
        rank = random.choice(ranks)
        regular_coins = random.randint(1000, 50000)
        premium_coins = random.randint(100, 5000)
        
        # 사용자 생성
        user = User(
            nickname=f"test_user_{i}",
            email=f"user{i}@example.com",
            hashed_password=get_password_hash("password123"),
            rank=rank,
            regular_coins=regular_coins,
            premium_coins=premium_coins,
            is_active=True
        )
        users.append(user)
    
    # 사용자 저장
    db.add_all(users)
    db.commit()
    
    # 사용자 ID 가져오기
    for user in users:
        db.refresh(user)
    
    # 게임 액션 데이터 생성
    print("게임 액션 데이터 생성 중...")
    actions = []
    
    for user in users:
        # 각 사용자당 3~10개의 액션 생성
        num_actions = random.randint(3, 10)
        
        for _ in range(num_actions):
            # 날짜 생성 (최근 7일 이내)
            days_ago = random.randint(0, 7)
            action_date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            # 랜덤 게임 타입
            game_type = random.choice(["SLOT", "CARD", "DICE"])
            
            # 랜덤 액션 타입
            if game_type == "SLOT":
                action_type = "SPIN"
                bet_amount = random.randint(10, 500)
            elif game_type == "CARD":
                action_type = random.choice(["DEAL", "HIT", "STAND"])
                bet_amount = random.randint(50, 1000)
            else:
                action_type = "ROLL"
                bet_amount = random.randint(10, 300)
            
            # 액션 생성
            action = UserAction(
                user_id=user.id,
                game_type=game_type,
                action_type=action_type,
                bet_amount=bet_amount,
                action_result=random.choice(["WIN", "LOSE", "DRAW"]),
                timestamp=action_date
            )
            actions.append(action)
    
    # 액션 저장
    db.add_all(actions)
    db.commit()
    
    # 리워드 데이터 생성
    print("리워드 데이터 생성 중...")
    rewards = []
    
    for user in users:
        # 각 사용자당 1~5개의 리워드 생성
        num_rewards = random.randint(1, 5)
        
        for _ in range(num_rewards):
            # 날짜 생성 (최근 14일 이내)
            days_ago = random.randint(0, 14)
            reward_date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            # 랜덤 리워드 타입
            reward_type = random.choice(["REGULAR_COINS", "PREMIUM_COINS", "BONUS"])
            
            # 리워드 금액
            if reward_type == "REGULAR_COINS":
                amount = random.randint(100, 2000)
            elif reward_type == "PREMIUM_COINS":
                amount = random.randint(10, 200)
            else:
                amount = random.randint(50, 500)
            
            # 리워드 생성
            reward = UserReward(
                user_id=user.id,
                reward_type=reward_type,
                amount=amount,
                reason=random.choice(["DAILY_LOGIN", "GAME_WIN", "PROMOTION"]),
                timestamp=reward_date
            )
            rewards.append(reward)
    
    # 리워드 저장
    db.add_all(rewards)
    db.commit()
    
    # 스트릭 데이터 생성
    print("스트릭 데이터 생성 중...")
    streaks = []
    
    for user in users:
        # 50% 확률로 스트릭 데이터 생성
        if random.random() > 0.5:
            streak_count = random.randint(1, 10)
            
            # 스트릭 생성
            streak = UserStreak(
                user_id=user.id,
                streak_type="LOGIN",
                current_count=streak_count,
                max_count=max(streak_count, random.randint(streak_count, 15)),
                last_updated=datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))
            )
            streaks.append(streak)
    
    # 스트릭 저장
    db.add_all(streaks)
    db.commit()
    
    print("테스트 데이터 생성 완료!")
    print(f"- 사용자: {len(users)}명")
    print(f"- 게임 액션: {len(actions)}개")
    print(f"- 리워드: {len(rewards)}개")
    print(f"- 스트릭: {len(streaks)}개")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="테스트 데이터 생성 도구")
    parser.add_argument(
        "--users", type=int, default=50,
        help="생성할 테스트 사용자 수 (기본값: 50)"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="데이터베이스 초기화 후 데이터 생성 (기존 데이터 삭제)"
    )
    
    args = parser.parse_args()
    create_test_data(num_users=args.users, reset_db=args.reset)


if __name__ == "__main__":
    main()
