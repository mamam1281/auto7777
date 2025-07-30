from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from app.database import Base

class InviteCode(Base):
    __tablename__ = "invite_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30), nullable=True)
    max_uses = Column(Integer, default=1, nullable=True)
    use_count = Column(Integer, default=0, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], back_populates="created_invite_codes")
    used_by_user = relationship("User", foreign_keys=[used_by_user_id], back_populates="used_invite_code")