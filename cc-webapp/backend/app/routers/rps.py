from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal

from ..services.rps_service import RPSService, RPSResult
from ..database import get_db

router = APIRouter()

class RPSPlayRequest(BaseModel):
    user_choice: Literal["rock", "paper", "scissors"]
    bet_amount: int = Field(..., ge=5000, le=10000)

class RPSPlayResponse(BaseModel):
    user_choice: str
    computer_choice: str
    result: str
    tokens_change: int
    balance: int
    daily_play_count: int

@router.post("/play", response_model=RPSPlayResponse, summary="가위바위보 게임 플레이", description="사용자가 선택한 패(가위, 바위, 보)와 베팅액으로 게임을 진행합니다.")
async def play_rps(
    request: RPSPlayRequest,
    db: Session = Depends(get_db),
    # This assumes a way to get the current user's ID, e.g., from a dependency
    # For now, we'll pass it in the request or use a placeholder
    user_id: int = 1 # Placeholder: Replace with Depends(get_current_user_id)
):
    """
    ### 요청 본문:
    - **user_choice**: "rock", "paper", "scissors" 중 하나
    - **bet_amount**: 5,000에서 10,000 사이의 베팅액

    ### 응답:
    - 사용자의 선택, 컴퓨터의 선택, 게임 결과, 토큰 변화량, 최종 잔액 등 상세 정보를 반환합니다.
    """
    rps_service = RPSService(db=db)
    try:
        result = rps_service.play(
            user_id=user_id,
            user_choice=request.user_choice,
            bet_amount=request.bet_amount,
            db=db
        )
        return RPSPlayResponse(**result.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
