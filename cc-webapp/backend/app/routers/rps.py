from fastapi import APIRouter, Depends, HTTPException

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

@router.post("/play", response_model=RPSPlayResponse, summary="가?�바?�보 게임 ?�레??, description="?�용?��? ?�택????가?? 바위, �??� 베팅?�으�?게임??진행?�니??")
async def play_rps(
    request: RPSPlayRequest,
    db = Depends(get_db),
    # This assumes a way to get the current user's ID, e.g., from a dependency
    # For now, we'll pass it in the request or use a placeholder
    user_id: int = 1 # Placeholder: Replace with Depends(get_current_user_id)
):
    """
    ### ?�청 본문:
    - **user_choice**: "rock", "paper", "scissors" �??�나
    - **bet_amount**: 5,000?�서 10,000 ?�이??베팅??

    ### ?�답:
    - ?�용?�의 ?�택, 컴퓨?�의 ?�택, 게임 결과, ?�큰 변?�량, 최종 ?�액 ???�세 ?�보�?반환?�니??
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
