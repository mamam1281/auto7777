"""
모델 패키지 - 전체 시스템
통합된 모델 시스템으로 모든 기능 지원
"""

# Base 클래스 먼저 import
from .auth_models import Base

# Auth 모델들
from .auth_models import (
    User,
    InviteCode,
    LoginAttempt,
    RefreshToken,
    UserSession,
    SecurityEvent,
)

# Game 모델들
from .game_models import (
    UserAction,
    UserReward,
    GameSession,
    UserActivity,
    Reward,
    GachaResult,
    UserProgress,
)

# User Segment 모델 추가
from .user_models import UserSegment

# 모든 모델 클래스들을 리스트로 정의
__all__ = [
    # Base
    "Base",
    
    # Auth
    "User",
    "InviteCode", 
    "LoginAttempt",
    "RefreshToken",
    "UserSession",
    "SecurityEvent",
    
    # Game
    "UserAction",
    "UserReward",
    "GameSession", 
    "UserActivity",
    "Reward",
    "GachaResult",
    "UserProgress",

    # User
    "UserSegment",
]

