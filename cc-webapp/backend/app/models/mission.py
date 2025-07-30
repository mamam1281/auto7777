"""
Mission models for quest/mission system
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.database import Base


class MissionType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ACHIEVEMENT = "achievement"
    SPECIAL = "special"


class MissionStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    mission_type = Column(Enum(MissionType), nullable=False, default=MissionType.DAILY)
    target_value = Column(Integer, nullable=False, default=1)
    reward_type = Column(String(50), nullable=False, default="CYBER_TOKEN")
    reward_amount = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
