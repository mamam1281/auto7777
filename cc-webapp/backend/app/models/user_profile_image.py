"""
User profile images / avatar assignments
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class UserProfileImage(Base):
    __tablename__ = "user_profile_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    is_current = Column(Boolean, default=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="profile_images")
    avatar = relationship("Avatar")
