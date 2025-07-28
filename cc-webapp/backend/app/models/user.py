from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(50), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(100), nullable=False)
    invite_code = Column(String(6), nullable=False, index=True)
    cyber_token_balance = Column(Integer, default=200)
    created_at = Column(DateTime, default=datetime.utcnow)
    rank = Column(String(20), default="STANDARD", nullable=False)
    
    # Relationships with the admin module
    activities = relationship("UserActivity", back_populates="user")
    rewards = relationship("Reward", back_populates="user", foreign_keys="[Reward.user_id]")
    # User rewards and notifications relationships
    user_rewards = relationship("UserReward", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    created_invite_codes = relationship("InviteCode", foreign_keys="[InviteCode.created_by_user_id]", back_populates="created_by_user")
    used_invite_code = relationship("InviteCode", foreign_keys="[InviteCode.used_by_user_id]", back_populates="used_by_user")
    # Additional relationships
    segment = relationship("UserSegment", uselist=False, back_populates="user")  # One-to-one
    actions = relationship("UserAction", back_populates="user")
    administered_rewards = relationship("Reward", back_populates="admin", foreign_keys="[Reward.admin_id]")
    site_visits = relationship("SiteVisit", back_populates="user")
