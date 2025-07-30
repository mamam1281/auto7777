"""
미션 시스템과 프로필 이미지를 위한 초기 테스트 데이터 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
from app.models.mission import Mission
from app.models.avatar import Avatar

def create_sample_data():
    """샘플 미션과 아바타 데이터 생성"""
    
    # 데이터베이스 연결
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 기본 미션들 생성
        sample_missions = [
            Mission(
                title="첫 로그인",
                description="Casino Club에 첫 로그인하기",
                mission_type="LOGIN",
                target_value=1,
                reward_type="cyber_token",
                reward_amount=50,
                reward_description="사이버 토큰 50개",
                is_daily=False,
                is_active=True,
                priority=1
            ),
            Mission(
                title="일일 로그인",
                description="매일 로그인하여 보상 받기",
                mission_type="DAILY_LOGIN",
                target_value=1,
                reward_type="cyber_token", 
                reward_amount=10,
                reward_description="사이버 토큰 10개",
                is_daily=True,
                is_active=True,
                priority=2
            ),
            Mission(
                title="슬롯 도전자",
                description="슬롯을 5번 플레이하기",
                mission_type="SLOT_SPIN",
                target_value=5,
                reward_type="cyber_token",
                reward_amount=30,
                reward_description="사이버 토큰 30개",
                is_daily=False,
                is_active=True,
                priority=3
            )
        ]
        
        # 기본 아바타들 생성
        sample_avatars = [
            Avatar(
                name="기본 아바타",
                description="모든 사용자가 사용할 수 있는 기본 아바타",
                image_url="/static/avatars/default.png",
                category="basic",
                required_rank="STANDARD",
                is_premium=False,
                is_active=True,
                sort_order=1
            ),
            Avatar(
                name="네온 사이버",
                description="사이버펑크 테마의 네온 아바타",
                image_url="/static/avatars/neon_cyber.png", 
                category="premium",
                required_rank="PREMIUM",
                is_premium=True,
                is_active=True,
                sort_order=2
            ),
            Avatar(
                name="VIP 골드",
                description="VIP 회원 전용 골드 아바타",
                image_url="/static/avatars/vip_gold.png",
                category="vip",
                required_rank="VIP",
                is_premium=True,
                is_active=True,
                sort_order=3
            )
        ]
        
        # 데이터베이스에 저장
        for mission in sample_missions:
            # 중복 체크
            existing = db.query(Mission).filter(Mission.title == mission.title).first()
            if not existing:
                db.add(mission)
                print(f"✅ 미션 추가: {mission.title}")
            else:
                print(f"⚠️ 미션 이미 존재: {mission.title}")
        
        for avatar in sample_avatars:
            # 중복 체크  
            existing = db.query(Avatar).filter(Avatar.name == avatar.name).first()
            if not existing:
                db.add(avatar)
                print(f"✅ 아바타 추가: {avatar.name}")
            else:
                print(f"⚠️ 아바타 이미 존재: {avatar.name}")
        
        db.commit()
        print("\n🎉 샘플 데이터 생성 완료!")
        
        # 생성된 데이터 확인
        missions_count = db.query(Mission).count()
        avatars_count = db.query(Avatar).count()
        print(f"📊 총 미션: {missions_count}개")
        print(f"🎨 총 아바타: {avatars_count}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
