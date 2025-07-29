from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class VIPAccessLog(Base):
    __tablename__ = "vip_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_type = Column(String(50), nullable=False)  # e.g., 'ENTER', 'EXIT', 'UPGRADE', etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(255), nullable=True)

    user = relationship("User")
