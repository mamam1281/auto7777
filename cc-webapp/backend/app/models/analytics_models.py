"""
사용자 세그멘테이션 및 분석 모델들
- RFM 분석, 사용자 세그먼트, 배틀패스 등
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from .auth_clean import Base


class UserSegment(Base):
    """사용자 세그먼트 (RFM 분석 기반)"""
    __tablename__ = "user_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    rfm_group = Column(String(20), nullable=False, index=True)  # Whale, High_Engaged, Medium, Low_Risk, At_Risk
    recency_score = Column(Integer, nullable=False)  # 1-5 점수
    frequency_score = Column(Integer, nullable=False)  # 1-5 점수
    monetary_score = Column(Integer, nullable=False)  # 1-5 점수
    ltv_score = Column(Float, default=0.0, nullable=False)  # Lifetime Value 예측 점수
    risk_profile = Column(String(20), default="LOW", nullable=False, index=True)  # LOW, MEDIUM, HIGH
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="segment", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index("ix_user_segments_rfm_group", "rfm_group"),
        Index("ix_user_segments_risk_profile", "risk_profile"),
        Index("ix_user_segments_ltv_score", "ltv_score"),
    )


class BattlePass(Base):
    """배틀패스 시즌 관리"""
    __tablename__ = "battle_passes"
    
    id = Column(Integer, primary_key=True, index=True)
    season_name = Column(String(100), nullable=False)
    season_number = Column(Integer, nullable=False, index=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    max_level = Column(Integer, default=100, nullable=False)
    xp_per_level = Column(Integer, default=1000, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user_progresses = relationship("BattlePassProgress", back_populates="battle_pass")
    rewards = relationship("BattlePassReward", back_populates="battle_pass")


class BattlePassProgress(Base):
    """사용자별 배틀패스 진행도"""
    __tablename__ = "battle_pass_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    battle_pass_id = Column(Integer, ForeignKey("battle_passes.id", ondelete="CASCADE"), nullable=False, index=True)
    current_level = Column(Integer, default=1, nullable=False)
    current_xp = Column(Integer, default=0, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    purchased_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="battle_pass_progress")
    battle_pass = relationship("BattlePass", back_populates="user_progresses")
    claimed_rewards = relationship("BattlePassClaimed", back_populates="progress")
    
    # Indexes
    __table_args__ = (
        Index("ix_battle_pass_progress_user_battle_pass", "user_id", "battle_pass_id"),
    )


class BattlePassReward(Base):
    """배틀패스 보상 정의"""
    __tablename__ = "battle_pass_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    battle_pass_id = Column(Integer, ForeignKey("battle_passes.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(Integer, nullable=False)
    track_type = Column(String(20), nullable=False, index=True)  # FREE, PREMIUM
    reward_type = Column(String(50), nullable=False)
    reward_value = Column(String(100), nullable=False)
    reward_amount = Column(Integer, default=1, nullable=False)
    description = Column(String(200), nullable=True)
    
    # Relationships
    battle_pass = relationship("BattlePass", back_populates="rewards")
    
    # Indexes
    __table_args__ = (
        Index("ix_battle_pass_rewards_battle_pass_level", "battle_pass_id", "level"),
        Index("ix_battle_pass_rewards_track_type", "track_type"),
    )


class BattlePassClaimed(Base):
    """배틀패스 보상 수령 기록"""
    __tablename__ = "battle_pass_claimed"
    
    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("battle_pass_progress.id", ondelete="CASCADE"), nullable=False, index=True)
    reward_id = Column(Integer, ForeignKey("battle_pass_rewards.id", ondelete="CASCADE"), nullable=False, index=True)
    claimed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    progress = relationship("BattlePassProgress", back_populates="claimed_rewards")
    reward = relationship("BattlePassReward")
    
    # Indexes
    __table_args__ = (
        Index("ix_battle_pass_claimed_progress_reward", "progress_id", "reward_id"),
    )


class GachaPool(Base):
    """가챠 풀 관리"""
    __tablename__ = "gacha_pools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    pool_type = Column(String(50), nullable=False, index=True)  # STANDARD, LIMITED, PREMIUM
    cost_type = Column(String(20), nullable=False)  # CYBER_TOKENS, PREMIUM_GEMS
    cost_amount = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    items = relationship("GachaItem", back_populates="pool")
    logs = relationship("GachaLog", back_populates="pool")


class GachaItem(Base):
    """가챠 아이템"""
    __tablename__ = "gacha_items"
    
    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(Integer, ForeignKey("gacha_pools.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rarity = Column(String(20), nullable=False, index=True)  # COMMON, RARE, EPIC, LEGENDARY
    drop_rate = Column(Float, nullable=False)  # 0.0 ~ 1.0
    item_type = Column(String(50), nullable=False)
    item_value = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=True)
    
    # Relationships
    pool = relationship("GachaPool", back_populates="items")
    
    # Indexes
    __table_args__ = (
        Index("ix_gacha_items_pool_rarity", "pool_id", "rarity"),
    )


class GachaLog(Base):
    """가챠 뽑기 로그"""
    __tablename__ = "gacha_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pool_id = Column(Integer, ForeignKey("gacha_pools.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("gacha_items.id", ondelete="CASCADE"), nullable=False, index=True)
    cost_paid = Column(Integer, nullable=False)
    pull_type = Column(String(20), nullable=False)  # SINGLE, MULTI_10
    pulled_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="gacha_logs")
    pool = relationship("GachaPool", back_populates="logs")
    item = relationship("GachaItem")
    
    # Indexes
    __table_args__ = (
        Index("ix_gacha_logs_user_id_pulled_at", "user_id", "pulled_at"),
        Index("ix_gacha_logs_pool_id_pulled_at", "pool_id", "pulled_at"),
    )
