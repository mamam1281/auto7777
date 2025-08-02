"""인증 관련 데이터베이스 모델"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(50), unique=True, index=True, nullable=False)  # 사이트 아이디
    nickname = Column(String(50), nullable=False)  # 닉네임 (필수)
    phone_number = Column(String(20), nullable=False)  # 폰번호 (필수)
    hashed_password = Column(String(255), nullable=False)  # 비밀번호
    full_name = Column(String(100))  # 전체 이름 (선택)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # 관리자 여부
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    invite_code = Column(String(10), nullable=False)  # 초대코드 (5858 고정)
    
    # 프로필 관련
    avatar_url = Column(String(255))
    bio = Column(Text)
    
    # 게임 관련 관계
    actions = relationship("UserAction", back_populates="user")
    rewards = relationship("UserReward", back_populates="user")
    game_sessions = relationship("GameSession", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")
    gacha_results = relationship("GachaResult", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    
    # 기존 관계 (존재한다면)
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    """사용자 세션 모델"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user_agent = Column(Text)
    ip_address = Column(String(45))
    
    # 관계
    user = relationship("User", back_populates="sessions")


class SecurityEvent(Base):
    """보안 이벤트 모델"""
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_suspicious = Column(Boolean, default=False)
    
    # 관계
    user = relationship("User", back_populates="security_events")
