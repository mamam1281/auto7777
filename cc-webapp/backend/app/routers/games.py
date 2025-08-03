"""게임 관련 API 엔드포인트"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any

from ..database import get_db
from ..dependencies import get_current_user
from ..services.game_service import GameService
# from ..repositories.game_repository import GameRepository  # 임시 비활성화

router = APIRouter(prefix="/api/games", tags=["games"])

# Pydantic 모델들
from pydantic import BaseModel

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
    daily_spin_count: int
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
    prizes: List[dict]
    max_daily_spins: int

class GachaPullResponse(BaseModel):
    """가챠 뽑기 응답"""
    results: List[dict]
    tokens_change: int
    balance: int

class RPSPlayResponse(BaseModel):
    """가위바위보 응답"""
    user_choice: str
    computer_choice: str
    result: str
    tokens_change: int
    balance: int

# 의존성 주입
def get_game_service() -> GameService:
    """게임 서비스 의존성"""
    return GameService()

@router.post("/slot/spin", response_model=SlotSpinResponse)
async def spin_slot(
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """슬롯 머신 스핀"""
    try:
        result = game_service.slot_spin(current_user.id, db)
        return SlotSpinResponse(
            result=result.result,
            tokens_change=result.tokens_change,
            balance=result.balance,
            daily_spin_count=result.daily_spin_count,
            animation=result.animation
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/roulette/spin", response_model=PrizeRouletteSpinResponse)
async def spin_prize_roulette(
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """경품추첨 룰렛 스핀"""
    try:
        result = game_service.spin_prize_roulette(current_user.id)
        
        # Prize 객체를 딕셔너리로 변환 (속성이 없으면 기본값 사용)
        prize_dict = None
        if result.prize:
            prize_dict = {
                "id": getattr(result.prize, 'id', 1),
                "name": getattr(result.prize, 'name', 'Prize'),
                "value": getattr(result.prize, 'value', 100),
                "color": getattr(result.prize, 'color', '#FFD700')
            }
        
        return PrizeRouletteSpinResponse(
            success=result.success,
            prize=prize_dict,
            message=result.message,
            spins_left=getattr(result, 'spins_left', 0),
            cooldown_expires=getattr(result, 'cooldown_expires', None)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/roulette/info", response_model=PrizeRouletteInfoResponse)
async def get_roulette_info(
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """룰렛 정보 조회"""
    try:
        spins_left = game_service.get_roulette_spins_left(current_user.id)
        prizes = game_service.get_roulette_prizes()
        
        return PrizeRouletteInfoResponse(
            spins_left=spins_left,
            prizes=prizes,
            max_daily_spins=3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gacha/pull", response_model=GachaPullResponse)
async def pull_gacha(
    request: GachaPullRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """가챠 뽑기"""
    try:
        result = game_service.gacha_pull(current_user.id, request.count, db)
        return GachaPullResponse(
            results=result.results,
            tokens_change=result.tokens_change,
            balance=result.balance
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/rps/play", response_model=RPSPlayResponse)
async def play_rps(
    request: RPSPlayRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """가위바위보 게임"""
    try:
        result = game_service.rps_play(
            current_user.id, 
            request.choice, 
            request.bet_amount, 
            db
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