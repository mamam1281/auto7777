# Import individual router modules to make them accessible
# 핵심 라우터들만 먼저 활성화 (단계적 확장)
from . import auth  # 완전한 5개 입력 인증 시스템 사용
from . import users  # 사용자 API
from . import admin  # 관리자 API (간소화 버전)
from . import actions  # 게임 액션 API
from . import gacha  # 가챠 API
from . import rewards  # 보상 API
from . import shop  # 상점 API
from . import missions  # 미션 API
from . import quiz_router as quiz  # 퀴즈 API - 새로 추가
from . import dashboard  # 대시보드 API
from . import rps  # 가위바위보 API
from . import prize_roulette  # 프라이즈 룰렛 API
from . import notifications  # 알림 API

# 추후 단계별로 활성화할 라우터들
from . import ai_router  # AI 추천 시스템 - 새로 추가
# from . import adult_content  # 성인 콘텐츠 API (모델 누락)
# from . import ai  # AI 기능 API
from . import analyze  # 분석 API - 6단계 활성화
from . import chat_router as chat  # 채팅 API - 새로 추가
# from . import corporate  # 기업 API
from . import doc_titles  # 문서 제목 API - 1단계 활성화
from . import feedback  # 피드백 API - 2단계 활성화
from . import games  # 게임 API - 3단계 활성화
from . import game_api  # 게임 API 추가 - 4단계 활성화
from . import invite_router  # 초대 코드 API - 5단계 활성화
# from . import notification  # 단일 알림 API
# from . import personalization  # 개인화 API
# from . import recommend  # 추천 API
# from . import recommendation  # 추천 시스템 API
from . import roulette  # 룰렛 API - 7단계 활성화
from . import segments  # 세그먼트 API - 8단계 활성화
from . import tracking  # 트래킹 API - 9단계 활성화
from . import unlock  # 잠금해제 API - 10단계 활성화
# from . import user_segments  # 사용자 세그먼트 API

# Optional: define __all__ list for controlled imports
__all__ = [
    "auth", "users", "admin", "actions", "gacha", "rewards", "shop", 
    "missions", "dashboard", "rps", "prize_roulette", "notifications",
    "doc_titles",    # 1단계 추가
    "feedback",      # 2단계 추가
    "games",         # 3단계 추가
    "game_api",      # 4단계 추가
    "invite_router", # 5단계 추가
    "analyze",       # 6단계 추가
    "roulette",      # 7단계 추가
    "segments",      # 8단계 추가
    "tracking",      # 9단계 추가
    "unlock"         # 10단계 추가
]
