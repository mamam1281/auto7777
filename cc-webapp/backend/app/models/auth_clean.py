"""
간소화된 인증 시스템 모델
- 중복 제거
- 핵심 테이블만 포함
- 로그인/인증/회원가입 기본 틀
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """사용자 테이블 - 전체 시스템용 확장"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(50), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(100), nullable=False)
    invite_code = Column(String(6), nullable=False, index=True)
    
    # 게임 토큰 & 통화
    cyber_token_balance = Column(Integer, default=200)
    premium_gems = Column(Integer, default=0, nullable=False)
    
    # 사용자 등급 & 상태
    rank = Column(String(20), default="STANDARD", nullable=False)  # STANDARD, VIP, PREMIUM
    vip_tier = Column(String(20), default="STANDARD", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_adult_verified = Column(Boolean, default=False, nullable=False)
    
    # 프로필 정보
    profile_image = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)
    
    # 게임 진행도
    experience_points = Column(Integer, default=0, nullable=False)
    battlepass_level = Column(Integer, default=1, nullable=False)
    battlepass_xp = Column(Integer, default=0, nullable=False)
    
    # 통계
    total_spent = Column(Integer, default=0, nullable=False)  # 총 지출 (USD cents)
    login_count = Column(Integer, default=0, nullable=False)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Auth Relationships
    login_attempts = relationship("LoginAttempt", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    security_events = relationship("SecurityEvent", back_populates="user")
    
    # Game Relationships (lazy loading for performance)
    actions = relationship("UserAction", back_populates="user", lazy="dynamic")
    rewards = relationship("UserReward", back_populates="user", lazy="dynamic") 
    game_sessions = relationship("GameSession", back_populates="user", lazy="dynamic")
    activities = relationship("UserActivity", back_populates="user", lazy="dynamic")
    
    # Content Relationships
    vip_access_logs = relationship("VIPAccessLog", back_populates="user", lazy="dynamic")
    purchases = relationship("Purchase", back_populates="user", lazy="dynamic")
    notifications = relationship("Notification", back_populates="user", lazy="dynamic")
    
    # Analytics Relationships
    segment = relationship("UserSegment", back_populates="user", uselist=False)
    battle_pass_progress = relationship("BattlePassProgress", back_populates="user", lazy="dynamic")
    gacha_logs = relationship("GachaLog", back_populates="user", lazy="dynamic")
    
    # Indexes
    __table_args__ = (
        Index("ix_users_nickname_phone", "nickname", "phone_number"),
        Index("ix_users_vip_tier_active", "vip_tier", "is_active"),
        Index("ix_users_rank_created_at", "rank", "created_at"),
    )


class InviteCode(Base):
    """초대코드 테이블"""
    __tablename__ = "invite_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # 만료일시 (NULL이면 무제한)
    max_uses = Column(Integer, nullable=True)     # 최대 사용 횟수 (NULL이면 무제한)
    use_count = Column(Integer, default=0)        # 현재 사용 횟수
    created_by_user_id = Column(Integer, nullable=True)  # 생성자 user ID (NULL이면 시스템 생성)
    used_by_user_id = Column(Integer, nullable=True)     # 사용한 user ID
    last_used_at = Column(DateTime, nullable=True)       # 마지막 사용 시각


class LoginAttempt(Base):
    """로그인 시도 기록 - 시도 제한용"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    success = Column(Boolean, nullable=False, index=True)
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_agent = Column(String(500), nullable=True)
    failure_reason = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="login_attempts")
    
    # Indexes
    __table_args__ = (
        Index("ix_login_attempts_site_id_attempted_at", "site_id", "attempted_at"),
        Index("ix_login_attempts_ip_attempted_at", "ip_address", "attempted_at"),
    )


class RefreshToken(Base):
    """리프레시 토큰 관리"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(128), unique=True, nullable=False, index=True)
    device_fingerprint = Column(String(128), nullable=True, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_used_at = Column(DateTime, nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    revoke_reason = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    # Indexes
    __table_args__ = (
        Index("ix_refresh_tokens_user_id_created_at", "user_id", "created_at"),
        Index("ix_refresh_tokens_expires_at_revoked", "expires_at", "is_revoked"),
    )


class UserSession(Base):
    """사용자 세션 관리"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    device_fingerprint = Column(String(128), nullable=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(500), nullable=True)
    login_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    logout_at = Column(DateTime, nullable=True)
    logout_reason = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index("ix_user_sessions_user_id_active", "user_id", "is_active"),
        Index("ix_user_sessions_last_activity_active", "last_activity_at", "is_active"),
        Index("ix_user_sessions_expires_at_active", "expires_at", "is_active"),
    )


class SecurityEvent(Base):
    """보안 이벤트 로그"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default="INFO", nullable=False, index=True)
    description = Column(String(500), nullable=False)
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(500), nullable=True)
    event_metadata = Column(String(1000), nullable=True)  # metadata -> event_metadata로 변경
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="security_events")
    
    # Indexes
    __table_args__ = (
        Index("ix_security_events_type_created_at", "event_type", "created_at"),
        Index("ix_security_events_severity_created_at", "severity", "created_at"),
        Index("ix_security_events_user_id_created_at", "user_id", "created_at"),
    )
