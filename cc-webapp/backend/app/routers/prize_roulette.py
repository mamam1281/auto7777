"""
Prize Roulette API Router
Í≤KOREAN_TEXT_REMOVED Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED FastAPI KOREAN_TEXT_REMOVED
"""

from fastapi import APIRouter, Depends, HTTPException, status

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel

from ..database import get_db
from ..models import User
import random

logger = logging.getLogger(__name__)
router = APIRouter()

# === Pydantic Models ===

class Prize(BaseModel):
    """KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED"""
    id: str
    name: str
    value: int
    color: str
    probability: float
    icon: Optional[str] = None

class PrizeRouletteInfoResponse(BaseModel):
    """Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED"""
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    next_reset_time: datetime

class PrizeRouletteSpinRequest(BaseModel):
    """Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED"""
    user_id: Optional[str] = "temp_user"  # KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVEDID

class PrizeRouletteSpinResponse(BaseModel):
    """Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED"""
    success: bool
    prize: Optional[Prize] = None
    message: str
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    is_near_miss: Optional[bool] = False
    animation_type: Optional[str] = "normal"

# === Constants ===

PRIZES = [
    Prize(id="coins_100", name="ÏΩKOREAN_TEXT_REMOVED 100Í∞KOREAN_TEXT_REMOVED, value=100, color="#FFD700", probability=0.35, icon="KOREAN_TEXT_REMOVED"),
    Prize(id="coins_500", name="ÏΩKOREAN_TEXT_REMOVED 500Í∞KOREAN_TEXT_REMOVED, value=500, color="#FFA500", probability=0.20, icon="KOREAN_TEXT_REMOVED"),
    Prize(id="coins_1000", name="ÏΩKOREAN_TEXT_REMOVED 1000Í∞KOREAN_TEXT_REMOVED, value=1000, color="#FF6B35", probability=0.15, icon="KOREAN_TEXT_REMOVED"),
    Prize(id="gems_10", name="KOREAN_TEXT_REMOVED10Í∞KOREAN_TEXT_REMOVED, value=10, color="#9D4EDD", probability=0.18, icon="KOREAN_TEXT_REMOVED"),
    Prize(id="gems_50", name="KOREAN_TEXT_REMOVED50Í∞KOREAN_TEXT_REMOVED, value=50, color="#7209B7", probability=0.10, icon="KOREAN_TEXT_REMOVED"),
    Prize(id="jackpot", name="KOREAN_TEXT_REMOVED! KOREAN_TEXT_REMOVED200Í∞KOREAN_TEXT_REMOVED, value=200, color="#FF0080", probability=0.015, icon="KOREAN_TEXT_REMOVED"),
    Prize(id="bonus", name="Î≥KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED", value=1, color="#00FF88", probability=0.005, icon="KOREAN_TEXT_REMOVED")
]

DAILY_SPIN_LIMIT = 3
SPIN_COOLDOWN_MINUTES = 0  # KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED Í∞KOREAN_TEXT_REMOVEDÏø®ÎKOREAN_TEXT_REMOVED (KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVEDÎßKOREAN_TEXT_REMOVED

# === Service Functions ===

def get_user_spin_data(user_id: str, db: Session) -> Dict[str, Any]:
    """KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVEDÏ°KOREAN_TEXT_REMOVED (KOREAN_TEXT_REMOVED: Î©KOREAN_TEXT_REMOVED™®Î¶KOREAN_TEXT_REMOVEDÍ∏KOREAN_TEXT_REMOVED)"""
    # KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVED Íµ¨ÌKOREAN_TEXT_REMOVED Ï°KOREAN_TEXT_REMOVED
    # KOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVEDÎ©KOREAN_TEXT_REMOVED™®Î¶KOREAN_TEXT_REMOVEDÍ∏KOREAN_TEXT_REMOVED Íµ¨ÌKOREAN_TEXT_REMOVED
    today = datetime.now().date()
    
    # KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVEDÍµ¨Ï°∞ (KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVED DB KOREAN_TEXT_REMOVEDÎ∏KOREAN_TEXT_REMOVED
    return {
        "user_id": user_id,
        "date": today,
        "spins_used": 0,  # KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVED DBKOREAN_TEXT_REMOVED Ï°KOREAN_TEXT_REMOVED
        "last_spin_time": None
    }

def update_user_spin_data(user_id: str, db: Session) -> None:
    """KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED (KOREAN_TEXT_REMOVED: Î©KOREAN_TEXT_REMOVED™®Î¶KOREAN_TEXT_REMOVEDÍ∏KOREAN_TEXT_REMOVED)"""
    # KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVED Íµ¨ÌKOREAN_TEXT_REMOVEDÄKOREAN_TEXT_REMOVED
    pass

def select_prize_with_probability() -> Prize:
    """KOREAN_TEXT_REMOVED Í∏KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED"""
    random_value = random.random()
    cumulative_prob = 0.0
    
    for prize in PRIZES:
        cumulative_prob += prize.probability
        if random_value <= cumulative_prob:
            return prize
    
    # KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¨¥Í≤KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED Í≤KOREAN_TEXT_REMOVED Ï≤KOREAN_TEXT_REMOVEDÎ≤KOREAN_TEXT_REMOVEDß∏ KOREAN_TEXT_REMOVED Î∞KOREAN_TEXT_REMOVED
    return PRIZES[0]

def is_near_miss(selected_prize: Prize, user_preferences: Optional[Dict] = None) -> bool:
    """Í∑KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¨ÎKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED"""
    # Í≥KOREAN_TEXT_REMOVEDÏπKOREAN_TEXT_REMOVED Í∑KOREAN_TEXT_REMOVED Î≤KOREAN_TEXT_REMOVEDÍ≤KOREAN_TEXT_REMOVEDÎ•KOREAN_TEXT_REMOVEDÍ∑KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVED
    high_value_prizes = ["jackpot", "gems_50", "coins_1000"]
    
    if selected_prize.id not in high_value_prizes:
        # 40% KOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVEDÍ∑KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
        return random.random() < 0.4
    
    return False

# === API Endpoints ===

@router.get("/info", response_model=PrizeRouletteInfoResponse)
async def get_prize_roulette_info(
    user_id: str = "temp_user",
    db = Depends(get_db)
):
    """
    Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED Ï°KOREAN_TEXT_REMOVED
    - KOREAN_TEXT_REMOVED®ÏKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
    - Ïø®ÎKOREAN_TEXT_REMOVED
    - KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVED Î¶¨ÏKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
    """
    try:
        spin_data = get_user_spin_data(user_id, db)
        
        # KOREAN_TEXT_REMOVED§ÎKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED Í≥KOREAN_TEXT_REMOVED
        spins_used = spin_data.get("spins_used", 0)
        spins_left = max(0, DAILY_SPIN_LIMIT - spins_used)
        
        # KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVED Î¶¨ÏKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED (KOREAN_TEXT_REMOVED)
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return PrizeRouletteInfoResponse(
            spins_left=spins_left,
            next_reset_time=tomorrow
        )
        
    except Exception as e:
        logger.error(f"Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED Ï°KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVEDÎ•KOREAN_TEXT_REMOVEDÏ°KOREAN_TEXT_REMOVED."
        )

@router.post("/spin", response_model=PrizeRouletteSpinResponse)
async def spin_roulette(
    request: PrizeRouletteSpinRequest,
    db = Depends(get_db)
):
    """
    Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED
    - KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVEDÄKOREAN_TEXT_REMOVED Ï∞®ÎKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
    - KOREAN_TEXT_REMOVEDÄÎ≥KOREAN_TEXT_REMOVED Ï°KOREAN_TEXT_REMOVED
    - Í∑KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED Î°KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
    """
    try:
        from ..services.roulette_service import RouletteService
        from ..repositories.game_repository import GameRepository
        
        # KOREAN_TEXT_REMOVEDÏ¥KOREAN_TEXT_REMOVED
        game_repo = GameRepository()
        roulette_service = RouletteService(game_repo)
        
        # KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVEDID Ï≤KOREAN_TEXT_REMOVED¶¨ (KOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVED´ÏKOREAN_TEXT_REMOVED Î≥ÄKOREAN_TEXT_REMOVED
        user_id = hash(request.user_id) % 1000000  # Î¨KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED´ÏKOREAN_TEXT_REMOVEDÎ°KOREAN_TEXT_REMOVEDÎ≥ÄKOREAN_TEXT_REMOVED
        
        # Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED (DB KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED)
        result = roulette_service.spin_prize_roulette(user_id, db)
        
        # KOREAN_TEXT_REMOVED Î≥ÄKOREAN_TEXT_REMOVED
        prize_data = None
        if result.prize:
            prize_data = Prize(
                id=result.prize.id,
                name=result.prize.name,
                value=result.prize.value,
                color=result.prize.color,
                probability=result.prize.probability,
                icon=getattr(result.prize, 'icon', None)
            )
        
        return PrizeRouletteSpinResponse(
            success=result.success,
            prize=prize_data,
            message=result.message,
            spins_left=result.spins_left,
            cooldown_expires=result.cooldown_expires,
            is_near_miss=result.is_near_miss,
            animation_type=result.animation_type
        )
        
    except Exception as e:
        logger.error(f"Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED Ï§KOREAN_TEXT_REMOVED§ÎKOREAN_TEXT_REMOVEDÍ∞Ä Î∞KOREAN_TEXT_REMOVED: {str(e)}"
        )
    """
    Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED
    - KOREAN_TEXT_REMOVED Í∏KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
    - KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
    - KOREAN_TEXT_REMOVED ÏßÄÍ∏KOREAN_TEXT_REMOVEDÏ≤KOREAN_TEXT_REMOVED¶¨
    """
    try:
        user_id = request.user_id or "temp_user"
        
        # KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVEDÏ°KOREAN_TEXT_REMOVED
        spin_data = get_user_spin_data(user_id, db)
        spins_used = spin_data.get("spins_used", 0)
        
        # KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
        if spins_used >= DAILY_SPIN_LIMIT:
            return PrizeRouletteSpinResponse(
                success=False,
                message="KOREAN_TEXT_REMOVED§ÎKOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVEDÎ•KOREAN_TEXT_REMOVEDÎ™®ÎKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED. KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED",
                spins_left=0
            )
        
        # KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
        selected_prize = select_prize_with_probability()
        
        # Í∑KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¨ÎKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
        near_miss = is_near_miss(selected_prize)
        
        # KOREAN_TEXT_REMOVEDÎ©KOREAN_TEXT_REMOVEDÄKOREAN_TEXT_REMOVEDÍ≤KOREAN_TEXT_REMOVED
        animation_type = "normal"
        if selected_prize.id == "jackpot":
            animation_type = "jackpot"
        elif near_miss:
            animation_type = "near_miss"
        
        # KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
        update_user_spin_data(user_id, db)
        
        # KOREAN_TEXT_REMOVED ÏßÄÍ∏KOREAN_TEXT_REMOVEDÏ≤KOREAN_TEXT_REMOVED¶¨ (KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVED Íµ¨ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
        # award_prize_to_user(user_id, selected_prize, db)
        
        # KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED
        return PrizeRouletteSpinResponse(
            success=True,
            prize=selected_prize,
            message=f"Ï∂KOREAN_TEXT_REMOVED©ÎKOREAN_TEXT_REMOVED {selected_prize.name}KOREAN_TEXT_REMOVEDÎ•KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED!",
            spins_left=max(0, DAILY_SPIN_LIMIT - spins_used - 1),
            is_near_miss=near_miss,
            animation_type=animation_type
        )
        
    except Exception as e:
        logger.error(f"Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Î£KOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED Ï§KOREAN_TEXT_REMOVED§ÎKOREAN_TEXT_REMOVEDÍ∞Ä Î∞KOREAN_TEXT_REMOVED."
        )

@router.get("/prizes", response_model=List[Prize])
async def get_available_prizes():
    """
    KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED Í∞ÄKOREAN_TEXT_REMOVED•ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED Î™©ÎKOREAN_TEXT_REMOVED Ï°KOREAN_TEXT_REMOVED
    """
    return PRIZES

@router.get("/history")
async def get_spin_history(
    user_id: str = "temp_user",
    limit: int = 10,
    db = Depends(get_db)
):
    """
    KOREAN_TEXT_REMOVED¨ÏKOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¶¨ Ï°KOREAN_TEXT_REMOVED (KOREAN_TEXT_REMOVED•ÌKOREAN_TEXT_REMOVED Íµ¨ÌKOREAN_TEXT_REMOVED)
    """
    # KOREAN_TEXT_REMOVED§ÏKOREAN_TEXT_REMOVED Íµ¨ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¶¨ Ï°KOREAN_TEXT_REMOVED
    return {
        "message": "KOREAN_TEXT_REMOVED§ÌKOREAN_TEXT_REMOVED KOREAN_TEXT_REMOVED¶¨ Í∏KOREAN_TEXT_REMOVEDÄ Ï§ÄÎπKOREAN_TEXT_REMOVEDÏ§KOREAN_TEXT_REMOVED.",
        "history": []
    }
