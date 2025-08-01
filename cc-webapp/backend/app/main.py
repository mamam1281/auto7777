from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

from app.routers import (
    auth,  # 간소화된 인증 라우터
    games,  # 게임 API 활성화
    game_api_v2,  # 인증 연동된 새로운 게임 API 라우터
    # 모든 다른 라우터들을 임시로 비활성화 - 모델 의존성 해결 후 재활성화
    # ai,
    # analyze,
    # recommend,
    rewards,   # 추가
    # unlock,    # 추가
    # user_segments, # 추가
    # gacha,  # 추가
    # prize_roulette,  # 추가
    # notification,  # 추가
    # tracking,  # 추가
    personalization,  # 추가
    adult_content,  # 추가
    actions,  # 추가
    corporate,  # 추가
    users,  # 추가
    recommendation,  # 추가된 임포트
    doc_titles,  # 추가
    invite_router  # 초대코드 관련 API 추가
)

# JWT 인증 API 임포트 추가
try:
    from app.routers import simple_auth  # PostgreSQL 기반 간단한 인증 라우터
    SIMPLE_AUTH_AVAILABLE = True
    print("✅ Simple Auth API 모듈 로드 성공")
except ImportError as e:
    SIMPLE_AUTH_AVAILABLE = False
    print(f"⚠️ Warning: Simple Auth API not available: {e}")
except Exception as e:
    SIMPLE_AUTH_AVAILABLE = False
    print(f"❌ Error loading Simple Auth API: {e}")

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
## 🎮 Casino-Club F2P 웹 애플리케이션 API

### ✨ 주요 기능
- **🔐 JWT 인증**: 초대코드 기반 회원가입 및 안전한 토큰 기반 사용자 인증
- **🎰 게임 시스템**: 슬롯 머신, 가챠, 룰렛, 가위바위보 등 다양한 카지노 게임
- **💎 토큰 경제**: 사이버 토큰 기반 게임 경제 시스템 (기본 200토큰 지급)
- **🎁 보상 시스템**: 게임 플레이에 따른 실시간 보상 지급
- **📊 실시간 이벤트**: Kafka를 통한 사용자 행동 추적 및 분석
- **👤 사용자 프로필**: 개인화된 사용자 데이터 및 게임 통계 관리

### 🛠 기술 스택
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 14 + SQLite (개발 백업)
- **Messaging**: Apache Kafka 3.6 + Zookeeper
- **Caching**: Redis 7
- **Authentication**: JWT with Refresh Token
- **Monitoring**: Prometheus + Grafana (선택사항)

### 📖 API 사용 가이드
1. **회원가입**: `/api/auth/signup`에서 초대코드(5858, 1234, 0000, 6969) + 닉네임으로 가입
2. **로그인**: `/api/auth/login`으로 로그인하여 JWT 토큰 획득
3. **인증**: Authorization 헤더에 `Bearer {access_token}` 형태로 토큰 전송
4. **게임 플레이**: 인증된 상태에서 `/api/games/*` 엔드포인트로 게임 진행
5. **토큰 갱신**: `/api/auth/refresh`로 만료된 토큰 갱신

### 🎮 게임 시스템
- **슬롯 머신**: Variable-Ratio Reward 시스템, 연패 보상, 심리적 효과
- **가챠 시스템**: 확률 기반 뽑기, 근접 실패 메커니즘, 연속 뽑기 할인
- **경품 룰렛**: 일일 한정 룰렛, 쿨다운 시스템, 등급별 경품
- **가위바위보**: 실시간 대전, 베팅 시스템

### 🔗 관련 문서
- **검증 보고서**: [CASINO_CLUB_F2P_검증보고서.md](./CASINO_CLUB_F2P_검증보고서.md)
- **프로젝트 가이드**: [20250729-가이드006.md](./20250729-가이드006.md)
- **데이터베이스 스키마**: [DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md)
- **Docker 설정**: [DOCKER_GUIDE.md](./DOCKER_GUIDE.md)

### 🚀 현재 구현 상태 (2025.08.02)
- ✅ **인증 시스템**: 초대코드 회원가입, JWT 로그인, 토큰 갱신/검증
- ✅ **게임 API**: 슬롯 머신, 가챠, 룰렛, 가위바위보 완전 구현
- ✅ **보상 시스템**: 게임 결과에 따른 토큰 지급/차감
- ✅ **사용자 프로필**: 프로필 조회, 게임 통계, 토큰 잔고 관리
- ✅ **실시간 이벤트**: Kafka 기반 사용자 행동 로깅
- ✅ **헬스체크**: 시스템 상태 모니터링
- ⚠️ **Alembic 마이그레이션**: 초기 마이그레이션 파일 생성 필요
- 🔄 **추후 계획**: 배틀패스, 상점 시스템, 실시간 알림
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Casino Club F2P Team",
        "email": "dev@casino-club.com",
    },
    license_info={
        "name": "Private License",
        "identifier": "Proprietary"
    },
    tags_metadata=[
        {
            "name": "Simple Auth",
            "description": "🔐 사용자 인증 및 계정 관리 API",
            "externalDocs": {
                "description": "인증 시스템 가이드",
                "url": "/docs/auth-guide",
            },
        },
        {
            "name": "games", 
            "description": "🎰 카지노 게임 API (기본 버전)",
        },
        {
            "name": "Games API",
            "description": "🎮 카지노 게임 API (인증 통합 버전) - 슬롯, 가챠, 룰렛, 가위바위보",
        },
        {
            "name": "Users",
            "description": "👤 사용자 프로필 및 정보 관리 API",
        },
        {
            "name": "Rewards",
            "description": "🎁 보상 시스템 API - 게임 보상 조회 및 관리",
        },
        {
            "name": "Kafka",
            "description": "📊 실시간 이벤트 발행 및 메시징 시스템",
        },
        {
            "name": "Event",
            "description": "📈 사용자 행동 이벤트 추적",
        },
        {
            "name": "Authentication", 
            "description": "🔑 기본 로그인 및 토큰 기반 인증 (레거시)",
        },
        {
            "name": "System",
            "description": "⚙️ 시스템 상태 확인 및 모니터링",
        },
        {
            "name": "monitoring",
            "description": "📊 Prometheus 메트릭 및 모니터링",
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
if SIMPLE_AUTH_AVAILABLE:
    app.include_router(simple_auth.router, prefix="/api")  # PostgreSQL 기반 간단한 인증 라우터
    print("✅ Simple Auth API endpoints registered")
# 다른 모든 라우터들을 임시로 비활성화 - 모델 의존성 문제 해결 후 재활성화
# app.include_router(admin.router, prefix="/api")  # 임시 비활성화
app.include_router(games.router)  # 게임 API 라우터 활성화
app.include_router(game_api_v2.router)  # 인증 연동된 새로운 게임 API 라우터 추가
# app.include_router(segments.router, prefix="/api")
# app.include_router(chat.router, prefix="/api")
# app.include_router(feedback.router, prefix="/api")
# app.include_router(ai.router, prefix="/api")  # 🆕 Added AI router
# app.include_router(analyze.router, prefix="/api")  # 🆕 Added analyze router  
# app.include_router(recommend.router, prefix="/api")  # 🆕 Added recommend router
app.include_router(rewards.router, prefix="/api")  # 추가
# app.include_router(unlock.router, prefix="/api")   # 추가
# app.include_router(user_segments.router, prefix="/api") # 추가
# app.include_router(gacha.router, prefix="/api")  # 추가
# app.include_router(prize_roulette.router, prefix="/api/games/roulette", tags=["prize_roulette"])  # 경품 룰렛 API
# app.include_router(notification.router, prefix="/api")  # 추가
# app.include_router(tracking.router, prefix="/api")  # 추가
# app.include_router(personalization.router, prefix="/api")  # 추가
# app.include_router(adult_content.router, prefix="/api")  # 추가
# app.include_router(actions.router, prefix="/api")  # 추가
# app.include_router(corporate.router, prefix="/api")  # 추가
app.include_router(users.router, prefix="/api")  # 🎯 프로필 조회 API 활성화
# app.include_router(recommendation.router, prefix="/api")  # 추가된 라우터 등록
# app.include_router(doc_titles.router)  # prefix 없이 등록하여 /docs/titles 직접 접근 가능
# app.include_router(invite_router.router)  # 초대코드 유효성 검증 API 추가 (이미 /api/invite prefix 포함)

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
@app.post(
    "/api/kafka/publish", 
    tags=["Kafka", "Event"],
    summary="📊 실시간 이벤트 발행",
    description="""
**사용자 행동 이벤트를 Kafka 메시지 큐로 실시간 발행합니다.**

### 🚀 이벤트 시스템:
- Apache Kafka 기반 실시간 이벤트 스트리밍
- 사용자 행동 분석 및 개인화를 위한 데이터 수집
- 비동기 처리로 게임 성능에 영향 없음

### 📝 이벤트 유형:
- **game_play**: 게임 플레이 이벤트 (슬롯, 가챠, 룰렛 등)
- **token_transaction**: 토큰 획득/소모 이벤트
- **user_action**: 일반 사용자 행동 (로그인, 페이지 이동 등)
- **achievement**: 도전과제 달성 이벤트

### 🔧 페이로드 구조:
- **user_id**: 사용자 고유 ID
- **action_type**: 이벤트 타입 (위 유형 중 하나)
- **payload**: 추가 데이터 (게임 결과, 토큰 변화량 등)

### 💡 사용 예시:
```json
{
  "user_id": "12345",
  "action_type": "game_play",
  "payload": {
    "game": "slot",
    "result": "win",
    "tokens_won": 100
  }
}
```
    """
)
async def publish_user_action_event(event: UserActionEvent = Body(...)):
    """
    사용자 행동 이벤트를 Kafka로 발행
    
    실시간 분석 및 개인화를 위해 사용자의 모든 행동을 이벤트로 수집합니다.
    이 데이터는 추후 사용자 세분화, 추천 시스템, 보상 최적화 등에 활용됩니다.
    """
    send_kafka_message("user_actions", event.model_dump())
    return {
        "status": "ok", 
        "message": "Event published to Kafka successfully", 
        "event": event.model_dump(),
        "topic": "user_actions",
        "timestamp": datetime.utcnow().isoformat()
    }

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


@app.get(
    "/health", 
    tags=["System"],
    summary="⚙️ 시스템 헬스체크",
    description="""
**서버와 주요 서비스의 상태를 확인합니다.**

### 🔍 확인 항목:
- FastAPI 서버 정상 동작 여부
- 데이터베이스 연결 상태
- Redis 캐시 서버 상태  
- Kafka 메시지 큐 상태

### 📊 응답 정보:
- **status**: 전체 시스템 상태 ("healthy" | "unhealthy")
- **timestamp**: 응답 시간 (ISO 8601 형식)
- **services**: 각 서비스별 상태 정보
- **version**: API 버전

### 💡 모니터링 용도:
- 로드밸런서 헬스체크
- Kubernetes liveness/readiness probe
- 외부 모니터링 시스템 (Prometheus, Grafana)
    """
)
@app.head("/health", tags=["System"])
async def health_check():
    """
    시스템 상태 확인 엔드포인트
    
    GET/HEAD 메서드를 모두 지원하여 다양한 모니터링 도구와 호환됩니다.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": "healthy", 
            "redis": "healthy",
            "kafka": "healthy"
        }
    }
