from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class AdultContent(Base):
    __tablename__ = "adult_content"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(Integer, unique=True, nullable=False, index=True)  # e.g., 1, 2, 3
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    thumbnail_url = Column(String(255), nullable=True)
    media_url = Column(String(255), nullable=True)  # Video or full-res image
    # 랭크 기반 접근 제어 - STANDARD, PREMIUM, VIP 등
    required_rank = Column(String(20), default="STANDARD", nullable=False)
    # RFM 세그먼트 기반 접근 제어 (기존 유지)
    required_segment_level = Column(Integer, default=1, nullable=False)
    # Add any other relevant fields like 'duration', 'tags', etc.
