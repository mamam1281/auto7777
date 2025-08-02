"""
Services package - 간소화
"""

# 기존 서비스들 (활성화)
from .user_service import UserService
from .auth_service import AuthService
from .quiz_service import QuizService
from .friendship_service import FriendshipService
from .notification_service import NotificationService
from .invite_service import InviteService

# 새로운 AI 서비스들
from .ai_recommendation_service import AIRecommendationService
from .emotion_engine import EmotionEngine

# 새로운 채팅 서비스
from .chat_service import ChatService

__all__ = [
    "UserService",
    "AuthService", 
    "QuizService",
    "FriendshipService",
    "NotificationService",
    "InviteService",
    "AIRecommendationService",
    "EmotionEngine",
    "ChatService"
]


# Optionally, make other services available for easier import if structured this way
# from .token_service import TokenService
# from .age_verification_service import AgeVerificationService
# from .adult_content_service import AdultContentService
# from .flash_offer_service import FlashOfferService
# from .vip_content_service import VIPContentService
# from .game_service import GameService
# from .user_activity_service import UserActivityService
# from .user_feedback_service import UserFeedbackService
# from .personalization_service import PersonalizationService
# from .rfm_service import RFMService
# from .segmentation_service import SegmentationService
    # "FlashOfferService",
    # "VIPContentService",
    # "GameService",
    # "UserActivityService",
    # "NotificationService",
    # "UserFeedbackService",
    # "PersonalizationService",
    # "RFMService",
    # "SegmentationService",
    # "ChatService",
]
