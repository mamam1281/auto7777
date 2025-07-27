from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

class _DummyScheduler:
    running = False

    def shutdown(self, wait: bool = False) -> None:  # noqa: D401
        """No-op shutdown when scheduler is unavailable."""

try:
    from .apscheduler_jobs import start_scheduler, scheduler
except Exception:  # noqa: BLE001

    def start_scheduler():
        print("Scheduler disabled or APScheduler not installed")

    scheduler = _DummyScheduler()
try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ImportError:  # Optional dependency in tests
    Instrumentator = None
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
except Exception:  # noqa: BLE001
    sentry_sdk = None
    FastApiIntegration = None
import os  # For Sentry DSN from env var
from pydantic import BaseModel  # For request/response models
from typing import Optional

from app.routers import (
    auth,
    auth_simple,  # 추가
    admin,  # 새로 추가된 관리자 라우터
    games,
    segments,
    chat,
    feedback,
    ai,
    analyze,
    recommend,
    rewards,   # 추가
    unlock,    # 추가
    user_segments, # 추가
    gacha,  # 추가
    prize_roulette,  # 추가
    notification,  # 추가
    tracking,  # 추가
    personalization,  # 추가
    adult_content,  # 추가
    actions,  # 추가
    corporate,  # 추가
    users,  # 추가
    recommendation,  # 추가된 임포트
    doc_titles  # 추가
)

# --- Sentry Initialization (Placeholder - should be configured properly with DSN) ---
# It's good practice to initialize Sentry as early as possible.
# The DSN should be configured via an environment variable for security and flexibility.
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN and sentry_sdk and FastApiIntegration:
    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development"),
            integrations=[FastApiIntegration()],
        )
        print("Sentry SDK initialized successfully.")
    except Exception as e:  # noqa: BLE001
        print(f"Error: Failed to initialize Sentry SDK. {e}")
else:
    print(
        "Warning: SENTRY_DSN not found or sentry_sdk missing. Sentry not initialized."
    )
# --- End Sentry Initialization Placeholder ---



from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    if os.getenv("DISABLE_SCHEDULER") != "1":
        print("FastAPI startup event: Initializing job scheduler...")
        start_scheduler()
    yield
    # Shutdown logic
    print("FastAPI shutdown event: Shutting down scheduler...")
    if scheduler.running:
        scheduler.shutdown(wait=False)

app = FastAPI(
    lifespan=lifespan,
    title="Casino Club API",
    description="API for interactive mini-games and token-based reward system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Prometheus Instrumentation
if Instrumentator:
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        inprogress_labels=True,
    )
    instrumentator.instrument(app)
    instrumentator.expose(
        app, include_in_schema=False, endpoint="/metrics", tags=["monitoring"]
    )


# Configure CORS
origins = [
    "http://localhost:3000",  # Assuming Next.js runs on port 3000
    "http://139.180.155.143:3000",  # 프로덕션 프론트엔드
    "https://139.180.155.143:3000",  # HTTPS 지원
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router, prefix="/api")
app.include_router(auth_simple.router, prefix="/api")  # 새로운 단순 인증 시스템
app.include_router(admin.router, prefix="/api")  # 관리자 API 추가
app.include_router(games.router)  # prefix 제거 (이미 /api/games로 설정됨)
app.include_router(segments.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(ai.router, prefix="/api")  # 🆕 Added AI router
app.include_router(analyze.router, prefix="/api")  # 🆕 Added analyze router  
app.include_router(recommend.router, prefix="/api")  # 🆕 Added recommend router
app.include_router(rewards.router, prefix="/api")  # 추가
app.include_router(unlock.router, prefix="/api")   # 추가
app.include_router(user_segments.router, prefix="/api") # 추가
app.include_router(gacha.router, prefix="/api")  # 추가
app.include_router(prize_roulette.router, prefix="/api/games/roulette", tags=["prize_roulette"])  # 경품 룰렛 API
app.include_router(notification.router, prefix="/api")  # 추가
app.include_router(tracking.router, prefix="/api")  # 추가
app.include_router(personalization.router, prefix="/api")  # 추가
app.include_router(adult_content.router, prefix="/api")  # 추가
app.include_router(actions.router, prefix="/api")  # 추가
app.include_router(corporate.router, prefix="/api")  # 추가
app.include_router(users.router, prefix="/api")  # 추가
app.include_router(recommendation.router, prefix="/api")  # 추가된 라우터 등록
app.include_router(doc_titles.router)  # prefix 없이 등록하여 /docs/titles 직접 접근 가능


# Request/Response Models
class UserLogin(BaseModel):
    """사용자 로그인 스키마"""

    user_id: str
    password: str


class LoginResponse(BaseModel):
    """로그인 응답 스키마"""

    token: str
    user_id: str
    message: Optional[str] = None


@app.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login(user: UserLogin):
    """
    사용자 로그인 엔드포인트

    - **user_id**: 사용자 ID
    - **password**: 비밀번호
    - 성공 시 JWT 토큰 반환
    """
    # 실제 로직은 추후 구현
    if user.user_id == "test" and user.password == "password":
        return {
            "token": "sample_jwt_token",
            "user_id": user.user_id,
            "message": "로그인 성공",
        }
    raise HTTPException(status_code=401, detail="인증 실패")


@app.get("/health", tags=["System"])
async def health_check():
    """
    시스템 상태 확인 엔드포인트

    - 서버 정상 동작 여부 확인
    - 헬스체크 용도
    """
    return {"status": "healthy"}
