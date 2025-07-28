from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class UserSegment(Base):
    __tablename__ = "user_segments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rfm_group = Column(String(50), nullable=False)
    risk_profile = Column(String(50), nullable=False)
    name = Column(String(50), nullable=True)

    # Relationship
    user = relationship("User", back_populates="segment", uselist=False)  # One-to-one
