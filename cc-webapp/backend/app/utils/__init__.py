"""
통합 유틸리티 모듈
- 게임 확률 계산
- 리워드 처리
- 감정 피드백
- 세그멘테이션
- Redis 헬퍼
- 웹훅 및 외부 API
"""

__version__ = "1.0.0"

# 모든 유틸리티 함수들을 중앙 집중식으로 import
from .probability_utils import *
from .reward_utils import *
from .emotion_utils import *
from .segment_utils import *
from .redis_utils import *
from .webhook_utils import *
from .sentiment_utils import *

__all__ = [
    # Probability Utils
    'calculate_gacha_probability',
    'calculate_streak_bonus',
    'weighted_random_choice',
    'variable_ratio_reward',
    
    # Reward Utils
    'process_reward',
    'calculate_battlepass_xp',
    'check_unlock_eligibility',
    'award_achievement',
    
    # Emotion Utils
    'get_feedback_message',
    'generate_dopamine_trigger',
    'calculate_addiction_score',
    
    # Segment Utils
    'calculate_rfm_score',
    'update_user_segment',
    'get_personalized_offers',
    
    # Redis Utils
    'cache_user_data',
    'get_cached_data',
    'update_streak_counter',
    'manage_session_data',
    
    # Webhook Utils
    'send_webhook',
    'process_external_api',
    'handle_corporate_api',
    
    # Sentiment Utils
    'analyze_sentiment',
    'extract_emotions',
    'calculate_satisfaction_score'
]
