"""User Reward model definition."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from app.database import Base

class UserReward(Base):
    """User Reward model for tracking rewards given to users."""
    
    __tablename__ = "user_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reward_type = Column(String, index=True)
    reward_value = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    source_description = Column(String, nullable=True)
    awarded_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_rewards")
    
    def __repr__(self):
        return f"<UserReward(user_id={self.user_id}, type={self.reward_type}, amount={self.amount})>"