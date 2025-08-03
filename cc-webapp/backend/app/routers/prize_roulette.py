"""
Prize Roulette API Router
ê²½í’ˆ ë£°ë › ?œìŠ¤?œì„ ?„í•œ FastAPI ?¼ìš°??
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
    """?í’ˆ ?•ë³´"""
    id: str
    name: str
    value: int
    color: str
    probability: float
    icon: Optional[str] = None

class PrizeRouletteInfoResponse(BaseModel):
    """ë£°ë › ?•ë³´ ?‘ë‹µ"""
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    next_reset_time: datetime

class PrizeRouletteSpinRequest(BaseModel):
    """ë£°ë › ?¤í? ?”ì²­"""
    user_id: Optional[str] = "temp_user"  # ?„ì‹œ ?¬ìš©??ID

class PrizeRouletteSpinResponse(BaseModel):
    """ë£°ë › ?¤í? ?‘ë‹µ"""
    success: bool
    prize: Optional[Prize] = None
    message: str
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    is_near_miss: Optional[bool] = False
    animation_type: Optional[str] = "normal"

# === Constants ===

PRIZES = [
    Prize(id="coins_100", name="ì½”ì¸ 100ê°?, value=100, color="#FFD700", probability=0.35, icon="?ª™"),
    Prize(id="coins_500", name="ì½”ì¸ 500ê°?, value=500, color="#FFA500", probability=0.20, icon="?’°"),
    Prize(id="coins_1000", name="ì½”ì¸ 1000ê°?, value=1000, color="#FF6B35", probability=0.15, icon="?’"),
    Prize(id="gems_10", name="??10ê°?, value=10, color="#9D4EDD", probability=0.18, icon="?’œ"),
    Prize(id="gems_50", name="??50ê°?, value=50, color="#7209B7", probability=0.10, icon="?”®"),
    Prize(id="jackpot", name="??ŒŸ! ??200ê°?, value=200, color="#FF0080", probability=0.015, icon="?°"),
    Prize(id="bonus", name="ë³´ë„ˆ???¤í?", value=1, color="#00FF88", probability=0.005, icon="?")
]

DAILY_SPIN_LIMIT = 3
SPIN_COOLDOWN_MINUTES = 0  # ?¤í? ê°?ì¿¨ë‹¤???†ìŒ (?¼ì¼ ?œí•œë§?

# === Service Functions ===

def get_user_spin_data(user_id: str, db: Session) -> Dict[str, Any]:
    """?¬ìš©???¤í? ?°ì´??ì¡°íšŒ (?„ì‹œ: ë©”ëª¨ë¦?ê¸°ë°˜)"""
    # ?¤ì œ êµ¬í˜„?ì„œ???°ì´?°ë² ?´ìŠ¤?ì„œ ì¡°íšŒ
    # ?„ì¬???„ì‹œë¡?ë©”ëª¨ë¦?ê¸°ë°˜ êµ¬í˜„
    today = datetime.now().date()
    
    # ?„ì‹œ ?°ì´??êµ¬ì¡° (?¤ì œë¡œëŠ” DB ?Œì´ë¸?
    return {
        "user_id": user_id,
        "date": today,
        "spins_used": 0,  # ?¤ì œë¡œëŠ” DB?ì„œ ì¡°íšŒ
        "last_spin_time": None
    }

def update_user_spin_data(user_id: str, db: Session) -> None:
    """?¬ìš©???¤í? ?°ì´???…ë°?´íŠ¸ (?„ì‹œ: ë©”ëª¨ë¦?ê¸°ë°˜)"""
    # ?¤ì œ êµ¬í˜„?ì„œ???°ì´?°ë² ?´ìŠ¤???€??
    pass

def select_prize_with_probability() -> Prize:
    """?•ë¥  ê¸°ë°˜ ?í’ˆ ? íƒ"""
    random_value = random.random()
    cumulative_prob = 0.0
    
    for prize in PRIZES:
        cumulative_prob += prize.probability
        if random_value <= cumulative_prob:
            return prize
    
    # ?•ë¥  ?¤ì°¨ë¡??¸í•´ ?„ë¬´ê²ƒë„ ? íƒ?˜ì? ?Šì? ê²½ìš° ì²?ë²ˆì§¸ ?í’ˆ ë°˜í™˜
    return PRIZES[0]

def is_near_miss(selected_prize: Prize, user_preferences: Optional[Dict] = None) -> bool:
    """ê·¼ì ‘ ?¤íŒ¨ ?¬ë? ?ë‹¨"""
    # ê³ ê?ì¹??í’ˆ ê·¼ì²˜?ì„œ ë²—ì–´??ê²½ìš°ë¥?ê·¼ì ‘ ?¤íŒ¨ë¡??ë‹¨
    high_value_prizes = ["jackpot", "gems_50", "coins_1000"]
    
    if selected_prize.id not in high_value_prizes:
        # 40% ?•ë¥ ë¡?ê·¼ì ‘ ?¤íŒ¨ ?°ì¶œ
        return random.random() < 0.4
    
    return False

# === API Endpoints ===

@router.get("/info", response_model=PrizeRouletteInfoResponse)
async def get_prize_roulette_info(
    user_id: str = "temp_user",
    db = Depends(get_db)
):
    """
    ë£°ë › ?•ë³´ ì¡°íšŒ
    - ?¨ì? ?¤í? ?Ÿìˆ˜
    - ì¿¨ë‹¤???íƒœ
    - ?¤ìŒ ë¦¬ì…‹ ?œê°„
    """
    try:
        spin_data = get_user_spin_data(user_id, db)
        
        # ?¤ëŠ˜ ?¬ìš©???¤í? ?Ÿìˆ˜ ê³„ì‚°
        spins_used = spin_data.get("spins_used", 0)
        spins_left = max(0, DAILY_SPIN_LIMIT - spins_used)
        
        # ?¤ìŒ ë¦¬ì…‹ ?œê°„ (?ì •)
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return PrizeRouletteInfoResponse(
            spins_left=spins_left,
            next_reset_time=tomorrow
        )
        
    except Exception as e:
        logger.error(f"ë£°ë › ?•ë³´ ì¡°íšŒ ?¤íŒ¨: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ë£°ë › ?•ë³´ë¥?ì¡°íšŒ?????†ìŠµ?ˆë‹¤."
        )

@router.post("/spin", response_model=PrizeRouletteSpinResponse)
async def spin_roulette(
    request: PrizeRouletteSpinRequest,
    db = Depends(get_db)
):
    """
    ë£°ë › ?¤í? ?¤í–‰
    - ? ì? ?€?…ë³„ ì°¨ë“± ?•ë¥  ?ìš©
    - ?œê°„?€ë³??¹ë¥  ì¡°ì •
    - ê·¼ì ‘ ?¤íŒ¨ ë¡œì§ ?ìš©
    """
    try:
        from ..services.roulette_service import RouletteService
        from ..repositories.game_repository import GameRepository
        
        # ?œë¹„??ì´ˆê¸°??
        game_repo = GameRepository()
        roulette_service = RouletteService(game_repo)
        
        # ?¬ìš©??ID ì²˜ë¦¬ (?„ì‹œë¡??«ì ë³€??
        user_id = hash(request.user_id) % 1000000  # ë¬¸ì?´ì„ ?«ìë¡?ë³€??
        
        # ë£°ë › ?¤í? ?¤í–‰ (DB ?¸ì…˜ ?„ë‹¬)
        result = roulette_service.spin_prize_roulette(user_id, db)
        
        # ?‘ë‹µ ë³€??
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
        logger.error(f"ë£°ë › ?¤í? ?¤íŒ¨: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ë£°ë › ?¤í? ì¤??¤ë¥˜ê°€ ë°œìƒ?ˆìŠµ?ˆë‹¤: {str(e)}"
        )
    """
    ë£°ë › ?¤í? ?¤í–‰
    - ?•ë¥  ê¸°ë°˜ ?í’ˆ ? íƒ
    - ?¬ìš©???œí•œ ?•ì¸
    - ?í’ˆ ì§€ê¸?ì²˜ë¦¬
    """
    try:
        user_id = request.user_id or "temp_user"
        
        # ?¬ìš©???¤í? ?°ì´??ì¡°íšŒ
        spin_data = get_user_spin_data(user_id, db)
        spins_used = spin_data.get("spins_used", 0)
        
        # ?¤í? ?Ÿìˆ˜ ?œí•œ ?•ì¸
        if spins_used >= DAILY_SPIN_LIMIT:
            return PrizeRouletteSpinResponse(
                success=False,
                message="?¤ëŠ˜???¤í? ?Ÿìˆ˜ë¥?ëª¨ë‘ ?¬ìš©?ˆìŠµ?ˆë‹¤. ?´ì¼ ?¤ì‹œ ?„ì „?˜ì„¸??",
                spins_left=0
            )
        
        # ?í’ˆ ? íƒ
        selected_prize = select_prize_with_probability()
        
        # ê·¼ì ‘ ?¤íŒ¨ ?¬ë? ?ë‹¨
        near_miss = is_near_miss(selected_prize)
        
        # ? ë‹ˆë©”ì´???€??ê²°ì •
        animation_type = "normal"
        if selected_prize.id == "jackpot":
            animation_type = "jackpot"
        elif near_miss:
            animation_type = "near_miss"
        
        # ?¤í? ?°ì´???…ë°?´íŠ¸
        update_user_spin_data(user_id, db)
        
        # ?í’ˆ ì§€ê¸?ì²˜ë¦¬ (?¤ì œ êµ¬í˜„ ??
        # award_prize_to_user(user_id, selected_prize, db)
        
        # ?±ê³µ ?‘ë‹µ
        return PrizeRouletteSpinResponse(
            success=True,
            prize=selected_prize,
            message=f"ì¶•í•˜?©ë‹ˆ?? {selected_prize.name}??ë¥? ?ë“?ˆìŠµ?ˆë‹¤!",
            spins_left=max(0, DAILY_SPIN_LIMIT - spins_used - 1),
            is_near_miss=near_miss,
            animation_type=animation_type
        )
        
    except Exception as e:
        logger.error(f"ë£°ë › ?¤í? ?¤íŒ¨: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ë£°ë › ?¤í? ì¤??¤ë¥˜ê°€ ë°œìƒ?ˆìŠµ?ˆë‹¤."
        )

@router.get("/prizes", response_model=List[Prize])
async def get_available_prizes():
    """
    ?¬ìš© ê°€?¥í•œ ?í’ˆ ëª©ë¡ ì¡°íšŒ
    """
    return PRIZES

@router.get("/history")
async def get_spin_history(
    user_id: str = "temp_user",
    limit: int = 10,
    db = Depends(get_db)
):
    """
    ?¬ìš©???¤í? ?ˆìŠ¤? ë¦¬ ì¡°íšŒ (?¥í›„ êµ¬í˜„)
    """
    # ?¤ì œ êµ¬í˜„?ì„œ???°ì´?°ë² ?´ìŠ¤?ì„œ ?ˆìŠ¤? ë¦¬ ì¡°íšŒ
    return {
        "message": "?¤í? ?ˆìŠ¤? ë¦¬ ê¸°ëŠ¥?€ ì¤€ë¹?ì¤‘ì…?ˆë‹¤.",
        "history": []
    }
