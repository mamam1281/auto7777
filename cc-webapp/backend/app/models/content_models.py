"""
컨텐츠 관리 모델들
- 성인 컨텐츠, VIP 액세스, 구매 등
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from .auth_clean import Base


class AdultContent(Base):
    """성인 컨텐츠 관리"""
    __tablename__ = "adult_content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False, index=True)  # IMAGE, VIDEO, STREAM, etc.
    tier_required = Column(String(20), nullable=False, index=True)  # STANDARD, VIP, PREMIUM
    age_restriction = Column(Integer, default=18, nullable=False)
    file_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    access_logs = relationship("VIPAccessLog", back_populates="content")
    
    # Indexes
    __table_args__ = (
        Index("ix_adult_content_tier_active", "tier_required", "is_active"),
        Index("ix_adult_content_type_active", "content_type", "is_active"),
    )


class VIPAccessLog(Base):
    """VIP 컨텐츠 액세스 로그"""
    __tablename__ = "vip_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("adult_content.id", ondelete="CASCADE"), nullable=False, index=True)
    access_type = Column(String(20), nullable=False, index=True)  # VIEW, DOWNLOAD, STREAM
    tokens_used = Column(Integer, default=0, nullable=False)
    accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6 지원
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="vip_access_logs")
    content = relationship("AdultContent", back_populates="access_logs")
    
    # Indexes
    __table_args__ = (
        Index("ix_vip_access_logs_user_id_accessed_at", "user_id", "accessed_at"),
        Index("ix_vip_access_logs_content_id_accessed_at", "content_id", "accessed_at"),
    )


class Purchase(Base):
    """구매 기록"""
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(50), nullable=False, index=True)  # CYBER_TOKENS, VIP_UPGRADE, CONTENT_ACCESS
    item_id = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True, index=True)
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, COMPLETED, FAILED, REFUNDED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="purchases")
    
    # Indexes
    __table_args__ = (
        Index("ix_purchases_user_id_created_at", "user_id", "created_at"),
        Index("ix_purchases_status_created_at", "status", "created_at"),
    )


class Shop(Base):
    """상점 아이템"""
    __tablename__ = "shop"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    discount_percent = Column(Float, default=0.0, nullable=False)
    is_limited = Column(Boolean, default=False, nullable=False)
    stock_quantity = Column(Integer, nullable=True)  # NULL = unlimited
    tier_required = Column(String(20), default="STANDARD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("ix_shop_type_active", "item_type", "is_active"),
        Index("ix_shop_tier_active", "tier_required", "is_active"),
    )


class Notification(Base):
    """알림 관리"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # NULL = 전체 공지
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, index=True)  # REWARD, PROMOTION, SYSTEM, etc.
    priority = Column(String(20), default="NORMAL", nullable=False, index=True)  # LOW, NORMAL, HIGH, URGENT
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index("ix_notifications_user_id_read", "user_id", "is_read"),
        Index("ix_notifications_user_id_created_at", "user_id", "created_at"),
        Index("ix_notifications_type_created_at", "notification_type", "created_at"),
    )
