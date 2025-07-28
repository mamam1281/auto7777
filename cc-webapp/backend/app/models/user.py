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
    rewards = relationship("Reward", back_populates="user")
    # User rewards and notifications relationships
    user_rewards = relationship("UserReward", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
