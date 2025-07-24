"""게임 관련 API 엔드포인트"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ..database import get_db
from ..auth.simple_auth import require_user
from ..services.game_service import GameService
from ..repositories.game_repository import GameRepository

router = APIRouter(prefix="/api/games", tags=["games"])

# Pydantic 모델들
class RouletteSpinRequest(BaseModel):
    bet_type: str  # "number", "color", "odd_even"
    bet_amount: int
    value: Optional[str] = None  # 베팅 값 (숫자, 색깔 등)

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

class RouletteSpinResponse(BaseModel):
    winning_number: int
    result: str
    tokens_change: int
    balance: int
    animation: Optional[str]

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

# 의존성 주입
def get_game_service() -> GameService:
    """게임 서비스 의존성"""
    return GameService()

@router.post("/slot/spin", response_model=SlotSpinResponse)
async def spin_slot(
    current_user_id: int = Depends(require_user),
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """슬롯 머신 스핀"""
    try:
        result = game_service.slot_spin(current_user_id, db)
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

@router.post("/roulette/spin", response_model=RouletteSpinResponse)
async def spin_roulette(
    request: RouletteSpinRequest,
    current_user_id: int = Depends(require_user),
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """룰렛 스핀"""
    try:
        result = game_service.roulette_spin(
            current_user_id, 
            request.bet_amount, 
            request.bet_type, 
            request.value, 
            db
        )
        return RouletteSpinResponse(
            winning_number=result.winning_number,
            result=result.result,
            tokens_change=result.tokens_change,
            balance=result.balance,
            animation=result.animation
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gacha/pull", response_model=GachaPullResponse)
async def pull_gacha(
    request: GachaPullRequest,
    current_user_id: int = Depends(require_user),
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """가챠 뽑기"""
    try:
        result = game_service.gacha_pull(current_user_id, request.count, db)
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
    current_user_id: int = Depends(require_user),
    db: Session = Depends(get_db),
    game_service: GameService = Depends(get_game_service)
):
    """가위바위보 게임"""
    try:
        result = game_service.rps_play(
            current_user_id, 
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