"""
🎰 Casino-Club F2P - 통합 모델 모듈
=================================
모든 데이터베이스 모델의 중앙 집중 관리

✅ 정리 완료 (2025-08-02)
- 중복 제거 및 통합
- 체계적인 분류
- 일관된 import 경로
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

