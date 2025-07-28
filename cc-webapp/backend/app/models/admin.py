from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="activities")

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reward_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="rewards")
    admin = relationship("User", foreign_keys=[admin_id], back_populates="administered_rewards")
