from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

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
except Exception:  # noqa: BLE001
    sentry_sdk = None
import os  # For Sentry DSN from env var

# Kafka integration
from app.kafka_client import send_kafka_message

# Define the app first
# ... (app initialization code) ...

# Then define models and routes
class UserActionEvent(BaseModel):
    user_id: str
    action_type: str
    payload: Optional[dict] = None
from pydantic import BaseModel  # For request/response models
from typing import Optional

# 라우터 import 추가 (가이드에 따라 재구성)
from app.routers import (
    auth,
    users,
    actions,
    gacha,
    rewards,
    shop,
    prize_roulette,
    admin,
    rps,
    dashboard,
    missions,
    quiz,
    notifications,
    # battlepass_router # battlepass 라우터는 아직 없는 것으로 보임
)

# JWT 인증 API 임포트 추가 - 사용자 요구사항에 맞는 auth.py만 사용
# try:
#     from app.routers import simple_auth  # PostgreSQL 기반 간단한 인증 라우터
#     SIMPLE_AUTH_AVAILABLE = True
#     print("✅ Simple Auth API 모듈 로드 성공")
# except ImportError as e:
#     SIMPLE_AUTH_AVAILABLE = False
#     print(f"⚠️ Warning: Simple Auth API not available: {e}")
# except Exception as e:
#     SIMPLE_AUTH_AVAILABLE = False
#     print(f"❌ Error loading Simple Auth API: {e}")
SIMPLE_AUTH_AVAILABLE = False  # 중복 제거를 위해 비활성화

# Kafka API 임포트 추가
try:
    from app.api.v1.kafka import router as kafka_router
    KAFKA_AVAILABLE = True
    print("✅ Kafka API 모듈 로드 성공")
except ImportError as e:
    KAFKA_AVAILABLE = False
    print(f"⚠️ Warning: Kafka integration not available: {e}")
except Exception as e:
    KAFKA_AVAILABLE = False
    print(f"❌ Error loading Kafka integration: {e}")

# --- Sentry Initialization (Placeholder - should be configured properly with DSN) ---
# It's good practice to initialize Sentry as early as possible.
# The DSN should be configured via an environment variable for security and flexibility.
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN and sentry_sdk:
    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development"),
        )
        print("Sentry SDK initialized successfully.")
    except Exception as e:  # noqa: BLE001
        print(f"Error: Failed to initialize Sentry SDK. {e}")
else:
    print(
        "Warning: SENTRY_DSN not found or sentry_sdk missing. Sentry not initialized."
    )
# --- End Sentry Initialization Placeholder ---

# 로깅 시스템 및 에러 핸들러 임포트
from app.core.logging import setup_logging, LoggingContextMiddleware
from app.core.error_handlers import add_exception_handlers, error_handling_middleware

# 로깅 시스템 초기화
log_level = "DEBUG" if os.getenv("ENVIRONMENT", "development") != "production" else "INFO"
setup_logging(level=log_level)

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
    title="🎰 Casino-Club F2P API",
    description="""
# ♣️ Casino-Club F2P 종합 백엔드 API

이 문서는 **완전히 재구축되고 안정화된** Casino-Club F2P 프로젝트의 API 명세입니다.

## 🚀 핵심 철학
- **안정성 우선:** 모든 API는 명확한 서비스 계층과 단위 테스트를 통해 안정성을 확보했습니다.
- **사용자 여정 중심:** API는 '회원가입 → 게임 플레이 → 보상'의 자연스러운 사용자 흐름에 맞춰 설계되었습니다.
- **확장성:** 신규 게임, 미션, 이벤트 등을 쉽게 추가할 수 있는 모듈식 구조를 지향합니다.

## ✨ 주요 기능 API
- **인증 (`/api/auth`):** `5858` 초대코드 기반 회원가입 및 JWT 토큰 발급
- **사용자 (`/api/users`):** 프로필 및 보상 내역 조회
- **게임 (`/api/games`):** 슬롯, 룰렛, 가위바위보 등 핵심 게임 플레이
- **상점 (`/api/shop`):** 아이템 구매
- **관리자 (`/api/admin`):** 사용자 관리 및 데이터 조회
- **대시보드 (`/api/dashboard`):** 핵심 지표 및 통계 제공

    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Jules - AI Software Engineer",
        "url": "https://github.com/google/generative-ai-docs",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    tags_metadata=[
        {
            "name": "Simple Auth",
            "description": "사용자 인증 및 계정 관리 API",
            "externalDocs": {
                "description": "인증 시스템 가이드",
                "url": "/docs/auth-guide",
            },
        },
        {
            "name": "Users",
            "description": "사용자 프로필 및 정보 관리 API",
        },
        {
            "name": "Kafka",
            "description": "실시간 이벤트 발행 및 메시징 시스템",
        },
        {
            "name": "Event",
            "description": "사용자 행동 이벤트 추적",
        },
        {
            "name": "Authentication",
            "description": "로그인 및 토큰 기반 인증",
        },
        {
            "name": "System",
            "description": "시스템 상태 확인 및 모니터링",
        },
    ]
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
    "http://localhost:3001",  # Next.js dev server on port 3001
    "http://localhost:3002",  # Next.js dev server on port 3002 (현재 사용 중)
    "http://139.180.155.143:3000",  # 프로덕션 프론트엔드
    "https://139.180.155.143:3000",  # HTTPS 지원
    # Add other origins if needed
]

# 에러 핸들러 등록
add_exception_handlers(app)

# 에러 핸들링 미들웨어 등록
app.add_middleware(error_handling_middleware)

# 로깅 컨텍스트 미들웨어 등록
app.add_middleware(LoggingContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router, prefix="/api/auth", tags=["🔐 인증"])
app.include_router(users.router, prefix="/api/users", tags=["👤 사용자"])
app.include_router(actions.router, prefix="/api/actions", tags=["🎮 게임 액션"])
app.include_router(gacha.router, prefix="/api/gacha", tags=["🎁 가챠"])
app.include_router(rewards.router, prefix="/api/rewards", tags=["🏆 보상"])
app.include_router(shop.router, prefix="/api/shop", tags=["🛒 상점"])
app.include_router(prize_roulette.router, prefix="/api/games/roulette", tags=["🎡 프라이즈 룰렛"])
app.include_router(admin.router, prefix="/api/admin", tags=["🛠️ 관리자"])
app.include_router(rps.router, prefix="/api/games/rps", tags=["✂️ 가위바위보"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["📊 대시보드"])
app.include_router(missions.router, prefix="/api/missions", tags=["🎯 미션"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["📝 퀴즈"])
app.include_router(notifications.router, prefix="/ws", tags=["📡 실시간 알림"])
# app.include_router(battlepass_router.router, prefix="/api/battlepass", tags=["배틀패스"])

print("✅ Core API endpoints registered")

# Simple Auth API 라우터 등록
if SIMPLE_AUTH_AVAILABLE:
    # app.include_router(simple_auth.router)  # 이미 위에서 /api prefix로 등록됨
    print("✅ Simple Auth API endpoints registered (already included above)")
else:
    print("⚠️ Simple Auth API endpoints not available")

# Simple Auth API 라우터 등록
if SIMPLE_AUTH_AVAILABLE:
    # app.include_router(simple_auth.router)  # 이미 위에서 /api prefix로 등록됨
    print("✅ Simple Auth API endpoints registered (already included above)")
else:
    print("⚠️ Simple Auth API endpoints not available")

# Kafka API 라우터 등록 (가능한 경우에만)
if KAFKA_AVAILABLE:
    app.include_router(kafka_router)
    print("✅ Kafka API endpoints registered")
else:
    print("⚠️ Kafka API endpoints not available")

# Kafka integration route
@app.post("/api/kafka/publish", tags=["Kafka", "Event"])
async def publish_user_action_event(event: UserActionEvent = Body(...)):
    """
    사용자 행동 이벤트를 Kafka로 발행 (샘플)
    - topic: user_actions
    - value: {user_id, action_type, payload}
    """
    send_kafka_message("user_actions", event.model_dump())
    return {"status": "ok", "message": "Event published to Kafka", "event": event.model_dump()}

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
@app.head("/health", tags=["System"])
async def health_check():
    """
    시스템 상태 확인 엔드포인트

    - 서버 정상 동작 여부 확인
    - 헬스체크 용도
    - GET 및 HEAD 메서드 모두 지원
    """
    return {"status": "healthy"}
