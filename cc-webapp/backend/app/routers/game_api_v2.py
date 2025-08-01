"""
종합 게임 API 라우터 V2
- 인증 연동 버전
- 슬롯, 룰렛, 가챠, 가위바위보 등 모든 게임 기능 포함
- JWT 토큰 기반 인증으로 보안 강화
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..services.game_service import GameService
from ..database import get_db
from ..auth.simple_auth import require_user
from fastapi.security import OAuth2PasswordBearer
from ..repositories.game_repository import GameRepository

# OAuth2 인증 스키마 설정 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(prefix="/api/games", tags=["Games API"])

# 사용자 세션 관리 모델
class GameUserSession(BaseModel):
    user_id: int
    session_id: str
    game_type: str
    started_at: datetime
    last_active_at: datetime
    tokens_spent: int
    tokens_won: int

# Pydantic 모델들
class PrizeRouletteSpinRequest(BaseModel):
    """경품추첨 룰렛 요청"""
    pass  # 단순히 돌리기만 하므로 추가 파라미터 없음

class GachaPullRequest(BaseModel):
    count: int  # 뽑기 횟수

class RPSPlayRequest(BaseModel):
    choice: str  # "rock", "paper", "scissors"
    bet_amount: int

class SlotSpinResponse(BaseModel):
    result: str
    tokens_change: int
    balance: int
    streak: int
    animation: Optional[str]

class PrizeRouletteSpinResponse(BaseModel):
    """경품 룰렛 스핀 응답"""
    success: bool
    prize: Optional[dict]
    message: str
    spins_left: int
    cooldown_expires: Optional[str]

class PrizeRouletteInfoResponse(BaseModel):
    """경품 룰렛 정보 응답"""
    spins_left: int
    prizes: List[Dict[str, Any]]
    max_daily_spins: int

class GachaPullResponse(BaseModel):
    results: List[str]  # 실제 GachaPullResult에 맞춤
    tokens_change: int
    balance: int

class RPSPlayResponse(BaseModel):
    user_choice: str
    computer_choice: str
    result: str
    tokens_change: int
    balance: int

class GameStatsResponse(BaseModel):
    """사용자 게임 통계 응답"""
    total_games_played: int
    total_wins: int
    total_losses: int
    win_rate: float
    total_tokens_spent: int
    total_tokens_won: int
    profit_loss: int
    longest_win_streak: int
    current_win_streak: int
    favorite_game: str
    last_played_at: Optional[datetime]

# 의존성 주입
def get_game_service() -> GameService:
    """게임 서비스 의존성"""
    return GameService()

# 게임 세션 기록 함수
async def record_game_session(
    user_id: int,
    game_type: str,
    tokens_spent: int = 0,
    tokens_won: int = 0,
    db: Optional[Session] = None
):
    """게임 세션 기록"""
    try:
        if db is None:
            return None
            
        from ..repositories.game_session_repository import GameSessionRepository
        import logging
        logger = logging.getLogger(__name__)
        
        if tokens_won > 0:
            # 토큰 획득 - 게임 세션 업데이트
            # 이미 시작된 세션에 결과와 획득 토큰 기록
            result = "win" if tokens_won > 0 else "lose"
            # 실제 구현에서는 세션 ID를 추적해야 하지만, 여기서는 간단하게 처리
            # 마지막 세션을 가져와 업데이트
            sessions = GameSessionRepository.get_user_sessions(db, user_id, limit=1)
            if sessions:
                last_session = sessions[0]
                GameSessionRepository.update_game_session(
                    db, last_session.session_id, result, tokens_won
                )
            logger.info(f"User {user_id} won {tokens_won} tokens in {game_type}")
        else:
            # 게임 시작 - 새 세션 생성
            session = GameSessionRepository.create_game_session(
                db, user_id, game_type, tokens_spent
            )
            logger.info(f"User {user_id} started {game_type} session, spent {tokens_spent} tokens")
            
            # 일일 제한 사용
            if game_type == "prize_roulette":
                # 룰렛의 경우 쿨다운 적용 (5분)
                GameSessionRepository.use_daily_play(db, user_id, game_type, cooldown_minutes=5)
            else:
                # 다른 게임은 쿨다운 없이 사용량만 증가
                GameSessionRepository.use_daily_play(db, user_id, game_type)
                
        return True
    except Exception as e:
        # 로깅만 하고 실패 시에도 게임은 계속 진행
        import logging
        logging.getLogger(__name__).error(f"Error recording game session: {str(e)}")
        return False

# 게임 엔드포인트들
@router.post(
    "/slot/spin", 
    response_model=SlotSpinResponse, 
    summary="🎰 슬롯 머신 스핀", 
    description="""
    **슬롯 머신 게임을 플레이합니다.**
    
    ### 🎮 게임 특징:
    - Variable-Ratio Reward 시스템으로 중독성 있는 게임플레이
    - 연패 시 보상 확률 증가 (심리적 보상 메커니즘)
    - 잭팟 시 특별 애니메이션 효과
    
    ### 💰 토큰 시스템:
    - 기본 베팅: 10토큰 
    - 승리 시: 20-200토큰 획득 (확률별 차등)
    - 잭팟: 최대 500토큰 획득
    
    ### 📊 응답 정보:
    - `result`: 게임 결과 ("win", "lose", "jackpot")
    - `tokens_change`: 토큰 변화량 (음수=차감, 양수=획득)
    - `balance`: 현재 토큰 잔고
    - `streak`: 연속 플레이 횟수
    - `animation`: UI 애니메이션 키 (선택사항)
    """
)
async def spin_slot(
    current_user_id: int = Depends(require_user),  # 인증 의존성 활성화
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """
    슬롯 머신 스핀 API
    
    ### 인증
    - JWT 토큰 인증 필요
    
    ### 설명
    - 1회 스핀마다 10 토큰 차감
    - 결과에 따라 토큰 획득 (일반, 잭팟, 스트릭 등)
    - 연속 당첨 시 스트릭 보너스 적용
    
    ### 응답
    - result: 결과 (win, jackpot, lose 등)
    - tokens_change: 토큰 변화량 (양수: 획득, 음수: 손실)
    - balance: 현재 잔액
    - streak: 현재 연속 당첨 횟수
    - animation: 애니메이션 타입 (선택적)
    """
    try:
        # 게임 세션 기록 (비동기)
        await record_game_session(
            user_id=current_user_id,
            game_type="slot",
            tokens_spent=10,  # 기본 비용
            db=db
        )
        
        # 슬롯 머신 결과 계산
        result = game_service.slot_spin(current_user_id, db)
        
        # 게임 세션 업데이트 (획득한 토큰)
        await record_game_session(
            user_id=current_user_id,
            game_type="slot",
            tokens_won=result.tokens_change if result.tokens_change > 0 else 0,
            db=db
        )
        
        return SlotSpinResponse(
            result=result.result,
            tokens_change=result.tokens_change,
            balance=result.balance,
            streak=result.streak,
            animation=result.animation
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/roulette/spin", 
    response_model=PrizeRouletteSpinResponse, 
    summary="🎡 경품 룰렛 스핀", 
    description="""
    **경품 룰렛을 돌려 다양한 경품을 획득합니다.**
    
    ### 🎁 경품 시스템:
    - 일일 3회 무료 스핀 제공
    - 10분 쿨다운 시간 적용
    - 등급별 차등 경품 (일반/레어/에픽/레전더리)
    
    ### 🏆 획득 가능 경품:
    - **토큰**: 50-500개 (확률 50%)
    - **포인트**: 100-1000점 (확률 30%) 
    - **쿠폰**: 할인쿠폰, 무료게임권 (확률 15%)
    - **레어 아이템**: 특별 아바타, 테마 (확률 5%)
    
    ### 📊 응답 정보:
    - `success`: 스핀 성공 여부
    - `prize`: 획득한 경품 정보 (아이템명, 수량, 등급)
    - `spins_left`: 남은 스핀 횟수
    - `cooldown_expires`: 다음 스핀 가능 시간
    """
)
async def spin_prize_roulette(
    current_user_id: int = Depends(require_user),  # 인증 의존성 활성화
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """
    경품추첨 룰렛 스핀 API
    
    ### 인증
    - JWT 토큰 인증 필요
    
    ### 제한 사항
    - 일일 스핀 제한 적용 (기본 3회)
    - 스핀 사용 후 쿨다운 시간 적용 (10분)
    
    ### 경품
    - 다양한 경품 아이템 획득 가능
    - 토큰, 포인트, 쿠폰 등 여러 보상 타입
    
    ### 응답
    - success: 성공 여부
    - prize: 획득한 경품 정보 (있는 경우)
    - message: 결과 메시지
    - spins_left: 남은 스핀 횟수
    - cooldown_expires: 쿨다운 만료 시간 (ISO 형식)
    """
    try:
        from ..repositories.game_session_repository import GameSessionRepository
        
        # 일일 제한 확인
        limit_check = GameSessionRepository.check_daily_limit(db, current_user_id, "prize_roulette")
        
        # 플레이 가능 여부 확인
        if not limit_check["can_play"]:
            message = "일일 플레이 횟수를 모두 사용했습니다."
            if limit_check["cooldown_active"]:
                message = "쿨다운 시간이 지나면 다시 시도하세요."
                
            return PrizeRouletteSpinResponse(
                success=False,
                prize=None,
                message=message,
                spins_left=limit_check["plays_left"],
                cooldown_expires=limit_check["cooldown_expires_at"].isoformat() if limit_check["cooldown_expires_at"] else None
            )
        
        # 게임 세션 기록
        await record_game_session(
            user_id=current_user_id,
            game_type="prize_roulette",
            db=db
        )
        
        # 일일 사용량 증가 및 쿨다운 설정 (쿨다운 10분)
        GameSessionRepository.use_daily_play(db, current_user_id, "prize_roulette", cooldown_minutes=10)
        
        # 룰렛 결과 계산
        result = game_service.spin_prize_roulette(current_user_id)
        
        # Prize 객체를 딕셔너리로 변환
        prize_dict = None
        if result.prize:
            prize_dict = {
                "id": result.prize.id,
                "name": result.prize.name,
                "value": result.prize.value,
                "color": result.prize.color
            }
            
            # 경품 획득 시 세션 업데이트
            await record_game_session(
                user_id=current_user_id,
                game_type="prize_roulette",
                tokens_won=result.prize.value,
                db=db
            )
        
        # 최신 제한 정보로 다시 조회
        updated_limit = GameSessionRepository.check_daily_limit(db, current_user_id, "prize_roulette")
        
        return PrizeRouletteSpinResponse(
            success=result.success,
            prize=prize_dict,
            message=result.message,
            spins_left=updated_limit["plays_left"],
            cooldown_expires=updated_limit["cooldown_expires_at"].isoformat() if updated_limit["cooldown_expires_at"] else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in prize roulette: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/roulette/info", response_model=PrizeRouletteInfoResponse, summary="룰렛 정보 조회", description="경품 룰렛의 현재 상태와 경품 목록을 조회합니다.")
async def get_roulette_info(
    current_user_id: int = Depends(require_user),  # 인증 의존성 활성화
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """
    룰렛 정보 조회 API
    
    ### 인증
    - JWT 토큰 인증 필요
    
    ### 제공 정보
    - 사용자의 남은 일일 스핀 횟수
    - 가능한 경품 목록 및 상세 정보
    - 획득 확률 및 가치
    - 일일 최대 스핀 횟수
    
    ### 응답
    - spins_left: 남은 스핀 횟수
    - prizes: 경품 목록 (id, name, value, color, probability 등)
    - max_daily_spins: 일일 최대 스핀 횟수
    """
    try:
        spins_left = game_service.get_roulette_spins_left(current_user_id)
        prizes = game_service.get_roulette_prizes()
        
        return PrizeRouletteInfoResponse(
            spins_left=spins_left,
            prizes=prizes,
            max_daily_spins=3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/gacha/pull", 
    response_model=GachaPullResponse, 
    summary="🎁 가챠 뽑기", 
    description="""
    **토큰을 사용하여 가챠 아이템을 뽑습니다.**
    
    ### 🎲 가챠 시스템:
    - 단일 뽑기: 50토큰
    - 10연속 뽑기: 450토큰 (10% 할인)
    - 근접 실패 메커니즘: 고급 아이템이 나올 뻔한 연출 포함
    
    ### 🌟 아이템 등급:
    - **일반 (60%)**: 기본 아이템, 소량 토큰
    - **레어 (25%)**: 중급 아이템, 아바타 파츠
    - **에픽 (12%)**: 고급 아이템, 특별 효과
    - **레전더리 (3%)**: 최고급 아이템, 한정판
    
    ### 💰 비용 & 보상:
    - 뽑기당 기본 50토큰 소모
    - 10연속 시 1개 레어 이상 보장
    - 100회 뽑기 시 레전더리 확정 (천장 시스템)
    """
)
async def pull_gacha(
    request: GachaPullRequest,
    current_user_id: int = Depends(require_user),  # 인증 의존성 활성화
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """
    가챠 뽑기 API
    
    ### 인증
    - JWT 토큰 인증 필요
    
    ### 요청 파라미터
    - count: 뽑기 횟수 (1 이상의 정수)
    
    ### 비용
    - 1회당 50 토큰
    - 다중 뽑기는 비례 비용 발생 (예: 10회 = 500 토큰)
    
    ### 등급 시스템
    - 일반 (common): 높은 확률
    - 레어 (rare): 중간 확률
    - 에픽 (epic): 낮은 확률
    - 레전더리 (legendary): 매우 낮은 확률
    
    ### 응답
    - results: 각 뽑기 결과 목록
    - tokens_change: 토큰 변화량 (일반적으로 음수, 특수 아이템 획득 시 양수 가능)
    - balance: 현재 잔액
    """
    try:
        # 게임 세션 기록 (토큰 소비)
        tokens_cost = request.count * 50  # 가챠 1회당 50토큰
        await record_game_session(
            user_id=current_user_id,
            game_type="gacha",
            tokens_spent=tokens_cost,
            db=db
        )
        
        # 가챠 결과 계산
        result = game_service.gacha_pull(current_user_id, request.count, db)
        
        # 게임 세션 업데이트 (획득한 토큰/아이템)
        if result.tokens_change > 0:
            await record_game_session(
                user_id=current_user_id,
                game_type="gacha",
                tokens_won=result.tokens_change,
                db=db
            )
        
        return GachaPullResponse(
            results=result.results,
            tokens_change=result.tokens_change,
            balance=result.balance
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/rps/play", 
    response_model=RPSPlayResponse, 
    summary="✂️ 가위바위보 게임", 
    description="""
    **가위바위보 게임을 플레이하고 베팅합니다.**
    
    ### 🎮 게임 규칙:
    - 가위(scissors), 바위(rock), 보(paper) 중 선택
    - 이기면 베팅금액의 2배 획득
    - 비기면 베팅금액 반환
    - 지면 베팅금액 잃음
    
    ### 💰 베팅 시스템:
    - 최소 베팅: 10토큰
    - 최대 베팅: 100토큰
    - 승리 시: 베팅금액 × 2 획득
    - 무승부: 베팅금액 반환
    
    ### 📊 응답 정보:
    - `user_choice`: 사용자 선택 (rock/paper/scissors)
    - `computer_choice`: 컴퓨터 선택
    - `result`: 게임 결과 (win/lose/draw)
    - `tokens_change`: 토큰 변화량
    - `balance`: 현재 토큰 잔고
    """
)
async def play_rps(
    request: RPSPlayRequest,
    current_user_id: int = Depends(require_user),  # 인증 의존성 활성화
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """
    가위바위보 게임 API
    
    ### 인증
    - JWT 토큰 인증 필요
    
    ### 요청 파라미터
    - choice: 사용자 선택 ("rock", "paper", "scissors")
    - bet_amount: 베팅 금액 (양의 정수)
    
    ### 결과 계산
    - 승리: 베팅 금액의 2배 획득
    - 무승부: 베팅 금액 반환
    - 패배: 베팅 금액 손실
    
    ### 응답
    - user_choice: 사용자 선택
    - computer_choice: 컴퓨터 선택
    - result: 결과 ("win", "draw", "lose")
    - tokens_change: 토큰 변화량
    - balance: 현재 잔액
    """
    try:
        # 게임 세션 기록 (베팅 금액)
        await record_game_session(
            user_id=current_user_id,
            game_type="rock_paper_scissors",
            tokens_spent=request.bet_amount,
            db=db
        )
        
        # 게임 결과 계산
        result = game_service.rps_play(
            current_user_id, 
            request.choice, 
            request.bet_amount, 
            db
        )
        
        # 승리 시 세션 업데이트
        if result.tokens_change > 0:
            await record_game_session(
                user_id=current_user_id,
                game_type="rock_paper_scissors",
                tokens_won=result.tokens_change,
                db=db
            )
        
        return RPSPlayResponse(
            user_choice=result.user_choice,
            computer_choice=result.computer_choice,
            result=result.result,
            tokens_change=result.tokens_change,
            balance=result.balance
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", response_model=GameStatsResponse, summary="게임 통계 조회", description="사용자의 게임 통계 정보를 조회합니다.")
async def get_game_stats(
    current_user_id: int = Depends(require_user),  # 인증 의존성 활성화
    db: Session = Depends(get_db)
):
    """
    사용자 게임 통계 API
    
    ### 인증
    - JWT 토큰 인증 필요
    
    ### 제공 정보
    - 전체 게임 통계 (총 게임 수, 승/패, 승률)
    - 경제 정보 (소비한 토큰, 획득한 토큰, 수익/손실)
    - 연승 정보 (최장 연승, 현재 연승)
    - 사용자 행동 패턴 (선호 게임, 마지막 플레이 시간)
    
    ### 응답
    - total_games_played: 총 플레이한 게임 수
    - total_wins: 총 승리 횟수
    - total_losses: 총 패배 횟수
    - win_rate: 승률 (0.0 ~ 100.0)
    - total_tokens_spent: 총 소비한 토큰
    - total_tokens_won: 총 획득한 토큰
    - profit_loss: 순이익/손실 (획득 - 소비)
    - longest_win_streak: 최장 연승 기록
    - current_win_streak: 현재 연승 횟수
    - favorite_game: 가장 자주 플레이한 게임
    - last_played_at: 마지막 플레이 시간
    """
    try:
        from ..repositories.game_session_repository import GameSessionRepository
        
        # 사용자 통계 조회
        stats = GameSessionRepository.get_user_stats(db, current_user_id)
        
        # 세션이 없을 경우 기본값 반환
        if not stats:
            return GameStatsResponse(
                total_games_played=0,
                total_wins=0,
                total_losses=0,
                win_rate=0.0,
                total_tokens_spent=0,
                total_tokens_won=0,
                profit_loss=0,
                longest_win_streak=0,
                current_win_streak=0,
                favorite_game="none",
                last_played_at=None
            )
            
        # DB에서 가져온 통계 데이터로 응답 생성
        # 직접 값 추출하여 안전하게 변환
        response_data = {
            "total_games_played": 0,
            "total_wins": 0,
            "total_losses": 0,
            "win_rate": 0.0,
            "total_tokens_spent": 0,
            "total_tokens_won": 0,
            "profit_loss": 0,
            "longest_win_streak": 0,
            "current_win_streak": 0,
            "favorite_game": "none",
            "last_played_at": None
        }
        
        # 실제 DB 값이 있으면 업데이트
        if stats:
            # __dict__로 간단히 가져오기 힘든 ORM 객체의 경우
            stats_dict = {
                "total_games_played": getattr(stats, "total_games_played", 0) or 0,
                "total_wins": getattr(stats, "total_wins", 0) or 0,
                "total_losses": getattr(stats, "total_losses", 0) or 0,
                "win_rate": getattr(stats, "win_rate", 0.0) or 0.0,
                "total_tokens_spent": getattr(stats, "total_tokens_spent", 0) or 0,
                "total_tokens_won": getattr(stats, "total_tokens_won", 0) or 0,
                "profit_loss": getattr(stats, "profit_loss", 0) or 0,
                "longest_win_streak": getattr(stats, "longest_win_streak", 0) or 0,
                "current_win_streak": getattr(stats, "current_win_streak", 0) or 0,
                "favorite_game": getattr(stats, "favorite_game", "none") or "none",
                "last_played_at": getattr(stats, "last_played_at", None)
            }
            
            # 딕셔너리 업데이트
            response_data.update(stats_dict)
            
        # 모든 값을 적절한 타입으로 변환
        for key, value in response_data.items():
            if key == "win_rate" and value is not None:
                response_data[key] = float(value)
            elif key == "last_played_at":
                # 날짜는 그대로 둠
                pass
            elif key == "favorite_game" and value is not None:
                response_data[key] = str(value)
            elif value is not None:
                response_data[key] = int(value)
        
        # Pydantic 모델로 변환하여 반환
        return GameStatsResponse(**response_data)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error getting game stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
