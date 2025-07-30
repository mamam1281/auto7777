"""
Avatar/Profile image models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.database import Base


class AvatarRarity(enum.Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Avatar(Base):
    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(500), nullable=False)
    rarity = Column(Enum(AvatarRarity), default=AvatarRarity.COMMON)
    unlock_condition = Column(String(255))  # 예: "rank:PREMIUM", "tokens:1000"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
