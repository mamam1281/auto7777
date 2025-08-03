# cc-webapp/backend/app/routers/gacha.py
from fastapi import APIRouter, Depends, HTTPException

from typing import Dict, Any, Union
import logging

# Assuming these utilities and models are correctly structured
from ..services.gacha_service import GachaService
from ..models import User # To verify user exists
from ..database import get_db # Original get_db from database.py
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service() -> GachaService:
    """가�??�비???�존??""
    return GachaService()


class GachaConfig(BaseModel):
    rarity_table: list[tuple[str, float]]
    reward_pool: Dict[str, int]

# --- Pydantic Models ---
class GachaPullRequest(BaseModel):
    """가�?뽑기 ?�청"""

    user_id: int

class GachaPullResponseItem(BaseModel):
    """가�?결과 ?�답"""

    type: str
    amount: Union[int, None] = None      # For COIN type
    stage: Union[int, None] = None       # For CONTENT_UNLOCK type
    badge_name: Union[str, None] = None  # For BADGE type
    message: Union[str, None] = None     # Optional message from spin_gacha logic
    
    # Pydantic validators for type conversion
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
    
    def __init__(self, **data):
        # Convert string values to appropriate types
        if 'amount' in data and data['amount'] is not None:
            if isinstance(data['amount'], str):
                try:
                    data['amount'] = int(data['amount'])
                except (ValueError, TypeError):
                    data['amount'] = None
        
        if 'stage' in data and data['stage'] is not None:
            if isinstance(data['stage'], str):
                try:
                    data['stage'] = int(data['stage'])
                except (ValueError, TypeError):
                    data['stage'] = None
                    
        super().__init__(**data)

    class Config:
        # Pydantic V2 uses ``from_attributes``. This is not strictly needed
        # here as we are creating from a dict, but is good practice if the
        # source dict could be an ORM model.
        from_attributes = True



# --- API Endpoint ---
@router.post("/gacha/pull", response_model=GachaPullResponseItem, tags=["gacha"])
async def pull_gacha_for_user(
    request_data: GachaPullRequest,
    db = Depends(get_db),
    service: GachaService = Depends(get_service),
):
    """
    Allows a user to pull the gacha.
    This endpoint calls the internal `spin_gacha` utility (from `app.utils.reward_utils`)
    and returns the result.

    Future enhancements not in current scope:
    - Deducting gacha currency from the user's account.
    - Directly recording the won gacha item as a UserReward (currently, frontend logs an action,
      and for CONTENT_UNLOCK, frontend calls /api/unlock).
    """
    logger.info(f"Gacha pull request received for user_id: {request_data.user_id}")

    user = db.query(User).filter(User.id == request_data.user_id).first()
    if not user:
        logger.warning(f"Gacha pull attempt by non-existent user_id: {request_data.user_id}")
        raise HTTPException(status_code=404, detail=f"User with id {request_data.user_id} not found.")    # GachaService가 ?�화 차감 �?보상 ?� 관�??�을 ?�행
    result = service.pull(request_data.user_id, 1, db)
    gacha_result_dict = {"type": result.results[0]}
    
    # 결과 객체?�서 추�? ?�보 추출 (?�전?�게)
    if hasattr(result, 'results') and len(result.results) > 1:
        # results가 ??복잡??구조?????�음
        pass
      # Dict ?�?�으�?변?�을 ?�해 ?�전??기본�??�용
    gacha_result_dict = {
        "type": str(result.results[0]) if result.results else "UNKNOWN"
    }
    
    # ?�???�전?�을 ?�해 명시?�으�??�는 ?�드???�외
    # amount?� stage??가�?결과???�라 ?�적?�로 ?�정?????�음

    if not gacha_result_dict or not gacha_result_dict.get("type"):
        logger.error(
            "GachaService returned an invalid result for user_id %s: %s",
            request_data.user_id,
            gacha_result_dict,
        )
        # This case should ideally not happen if spin_gacha is robust and always returns a dict with a type
        raise HTTPException(status_code=500, detail="Gacha spin failed to produce a valid result. Please try again.")

    logger.info(f"Gacha result for user_id {request_data.user_id}: {gacha_result_dict}")

    # The GachaPullResponseItem Pydantic model will validate the structure of gacha_result_dict.
    # If gacha_result_dict contains extra keys not defined in GachaPullResponseItem,
    # they will be excluded unless the Pydantic model's Config allows extra fields.
    # If it's missing required fields (like 'type'), Pydantic will raise a validation error
    # which FastAPI handles as a 422 Unprocessable Entity, but our check above should catch missing 'type'.
    return GachaPullResponseItem(**gacha_result_dict)


@router.get("/gacha/config", response_model=GachaConfig, tags=["gacha"])
async def get_gacha_config(service: GachaService = Depends(get_service)):
    """?�재 가�??�정 조회"""
    return GachaConfig(**service.get_config())


@router.put("/gacha/config", response_model=GachaConfig, tags=["gacha"])
async def update_gacha_config(
    config: GachaConfig,
    service: GachaService = Depends(get_service),
):
    """가�??�정 갱신"""
    service.update_config(rarity_table=config.rarity_table, reward_pool=config.reward_pool)
    return GachaConfig(**service.get_config())
