"""
게임 시스템 모델들
- 사용자 액션, 보상, 게임 플레이 등
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from .auth_clean import Base


class UserAction(Base):
    """사용자 액션 로그"""
    __tablename__ = "user_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # SLOT_SPIN, GACHA_PULL, etc.
    value = Column(Float, default=0.0, nullable=False)
    details = Column(Text, nullable=True)  # JSON 형태의 추가 정보
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="actions")
    
    # Indexes
    __table_args__ = (
        Index("ix_user_actions_user_id_type", "user_id", "action_type"),
        Index("ix_user_actions_user_id_created_at", "user_id", "created_at"),
        Index("ix_user_actions_type_created_at", "action_type", "created_at"),
    )


class UserReward(Base):
    """사용자 보상 로그"""
    __tablename__ = "user_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reward_type = Column(String(50), nullable=False, index=True)  # CYBER_TOKENS, ITEM, etc.
    reward_value = Column(String(100), nullable=False)  # 보상 값 (아이템ID나 토큰 수량 등)
    amount = Column(Integer, default=1, nullable=False)
    source = Column(String(50), nullable=False, index=True)  # SLOT_WIN, GACHA, DAILY_LOGIN, etc.
    source_description = Column(String(200), nullable=True)
    awarded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    claimed = Column(Boolean, default=True, nullable=False)
    claimed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="rewards")
    
    # Indexes
    __table_args__ = (
        Index("ix_user_rewards_user_id_awarded_at", "user_id", "awarded_at"),
        Index("ix_user_rewards_source_awarded_at", "source", "awarded_at"),
        Index("ix_user_rewards_user_id_claimed", "user_id", "claimed"),
    )


class GameSession(Base):
    """게임 세션 로그"""
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game_type = Column(String(50), nullable=False, index=True)  # SLOT, GACHA, RPS, etc.
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)
    total_spins = Column(Integer, default=0, nullable=False)
    total_bet = Column(Integer, default=0, nullable=False)
    total_win = Column(Integer, default=0, nullable=False)
    result = Column(String(20), nullable=True)  # WIN, LOSE, DRAW
    
    # Relationships
    user = relationship("User", back_populates="game_sessions")


class UserActivity(Base):
    """사용자 활동 로그"""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # LOGIN, GAME_PLAY, PURCHASE, etc.
    description = Column(String(200), nullable=True)
    meta_data = Column(Text, nullable=True)  # JSON 형태의 추가 정보
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    # Indexes
    __table_args__ = (
        Index("ix_user_activities_user_id_occurred_at", "user_id", "occurred_at"),
        Index("ix_user_activities_type_occurred_at", "activity_type", "occurred_at"),
    )


class Reward(Base):
    """보상 마스터 테이블"""
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    reward_type = Column(String(50), nullable=False, index=True)
    reward_value = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("ix_rewards_type_active", "reward_type", "is_active"),
    )


# User 모델에 relationship 추가하기 위한 import는 auth_clean.py에서 처리
