"""
사용자 세션 및 로그인 관리 모델
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserSession(Base):
    """사용자 세션 관리"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    access_token_jti = Column(String(100), nullable=True, index=True)  # JWT ID for access token
    device_info = Column(Text, nullable=True)  # 기기 정보 (User-Agent, IP 등)
    ip_address = Column(String(45), nullable=True)  # IPv6 지원
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="sessions")


class LoginAttempt(Base):
    """로그인 시도 기록"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(100), nullable=True)  # invalid_credentials, account_locked 등
    user_agent = Column(Text, nullable=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 인덱스: site_id + attempted_at, ip_address + attempted_at


class BlacklistedToken(Base):
    """블랙리스트된 토큰 (로그아웃/강제 무효화)"""
    __tablename__ = "blacklisted_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(100), unique=True, nullable=False, index=True)  # JWT ID
    token_type = Column(String(20), nullable=False)  # access, refresh
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(100), nullable=True)  # logout, force_logout, security_breach
    
    # 관계 설정
    user = relationship("User")
