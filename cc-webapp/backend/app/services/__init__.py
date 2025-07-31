"""
Services package - 임시로 간소화
"""

# 모든 서비스 임포트를 임시로 비활성화
pass


# Optionally, make other services available for easier import if structured this way
# from .user_service import UserService
# from .auth_service import AuthService
# from .token_service import TokenService
# from .age_verification_service import AgeVerificationService
# from .adult_content_service import AdultContentService
# from .flash_offer_service import FlashOfferService
# from .vip_content_service import VIPContentService
# from .game_service import GameService
# from .user_activity_service import UserActivityService
# from .notification_service import NotificationService
# from .user_feedback_service import UserFeedbackService
# from .personalization_service import PersonalizationService
# from .rfm_service import RFMService
# from .segmentation_service import SegmentationService
# from .chat_service import ChatService

__all__ = [
    "RewardService",
    "NotificationService", # Added
    "TrackingService", # Added
    "GameService",
    "UserSegmentService",
    "SlotService",
    "RouletteService",
    "GachaService",

    # "UserService",
    # "AuthService",
    # "TokenService",
    # "AgeVerificationService",
    # "AdultContentService",
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
