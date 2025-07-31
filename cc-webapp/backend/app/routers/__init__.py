# Import individual router modules to make them accessible
from . import auth_simple_test as auth  # 임시로 간단한 테스트 버전 사용
# from . import admin  # 임시 비활성화
# from . import games  # 임시 비활성화
# from . import segments  # 임시 비활성화
# from . import chat  # 임시 비활성화
# from . import feedback  # 임시 비활성화
# from . import ai  # 임시 비활성화
# from . import analyze  # 임시 비활성화
# from . import recommend  # 임시 비활성화
# from . import auth_simple  # 이미 제거됨

# Optional: define __all__ list for controlled imports
__all__ = ["auth", "games", "segments", "chat", "feedback", "ai", "analyze", "recommend", "auth_simple"]
