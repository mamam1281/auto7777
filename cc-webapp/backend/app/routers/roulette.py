"""
PrizeRoulette ê²Œì„ API ?¼ìš°??

?„ë¡ ?¸ì—”?œì˜ PrizeRoulette.tsx ì»´í¬?ŒíŠ¸?ì„œ ?¬ìš©?˜ëŠ” 
??ê°œì˜ ì£¼ìš” ?”ë“œ?¬ì¸?¸ë? ?œê³µ?©ë‹ˆ??
1. GET /api/roulette/info - ?¬ìš©?ë³„ ë£°ë › ?•ë³´ ì¡°íšŒ
2. POST /api/roulette/spin - ë£°ë › ?¤í? ?¤í–‰ ë°?ê²°ê³¼ ë°˜í™˜
"""
from fastapi import APIRouter, Depends, HTTPException, status

from typing import Dict, Any, Optional
import random
import uuid
from datetime import datetime, time, timedelta
import logging
from fastapi.security import OAuth2PasswordBearer

from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
from app.schemas.game_schemas import RouletteInfoResponse, RouletteSpinRequest, RouletteSpinResponse
from app.services.roulette_service import RouletteService

# ë¡œê¹… ?¤ì •
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/roulette",
    tags=["roulette"],
    responses={404: {"description": "Not found"}},
)

# ?„ë¼?´ì¦ˆ ë£°ë › ?œë¹„???¸ìŠ¤?´ìŠ¤ ?ì„±
# ?œë¹„???˜ì¡´??ì£¼ì…???„í•œ ?¨ìˆ˜
def get_roulette_service(db = Depends(get_db)):
    from app.repositories.game_repository import GameRepository
    repo = GameRepository(db)
    return RouletteService(repo)

@router.get("/info", response_model=RouletteInfoResponse)
async def get_roulette_info(
    db = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    ?¬ìš©?ì˜ ?„ë¼?´ì¦ˆ ë£°ë › ?•ë³´ë¥?ì¡°íšŒ?©ë‹ˆ??
    - ?¨ì? ?¤í? ?Ÿìˆ˜
    - ?¤ìŒ ?¤í?ê¹Œì? ?¨ì? ?œê°„ (?ˆëŠ” ê²½ìš°)
    - ê³¼ê±° ?¤í? ?´ì—­ ?”ì•½
    """
    try:
        # ?¤ì œ ?¬ìš©???°ì´??ê¸°ë°˜ ë£°ë › ?•ë³´ ê³„ì‚°
        user_id = current_user.id
        
        # ?¤ëŠ˜???¤í? ?Ÿìˆ˜ ê³„ì‚° (ê¸°ë³¸ê°? 3??
        daily_limit = 3
        spins_used_today = 0  # ?¤ì œë¡œëŠ” DB?ì„œ ì¡°íšŒ
        spins_left = max(0, daily_limit - spins_used_today)
        
        # ?¤ìŒ ?¤í? ê°€???œê°„ (ì¿¨ë‹¤?´ì´ ?ˆë‹¤ë©?
        next_spin_time = None
        if spins_left == 0:
            # ?ì •??ë¦¬ì…‹
            from datetime import datetime, time
            tomorrow = datetime.now().date() + timedelta(days=1)
            next_spin_time = datetime.combine(tomorrow, time.min)
        
        return RouletteInfoResponse(
            spins_left=spins_left,
            next_spin_time=next_spin_time,
            daily_spins_used=spins_used_today,
            total_spins_today=daily_limit
        )
    except Exception as e:
        logger.error(f"ë£°ë › ?•ë³´ ì¡°íšŒ ?¤íŒ¨: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ë£°ë › ?•ë³´ë¥?ë¶ˆëŸ¬?¤ëŠ” ì¤??¤ë¥˜ê°€ ë°œìƒ?ˆìŠµ?ˆë‹¤."
        )


@router.post("/spin", response_model=RouletteSpinResponse)
async def spin_roulette(
    request: Optional[RouletteSpinRequest] = None,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    ?„ë¼?´ì¦ˆ ë£°ë ›???Œë¦¬ê³?ê²°ê³¼ë¥?ë°˜í™˜?©ë‹ˆ??
    - ?¤í? ê²°ê³¼ (?¹ì²¨ ?í’ˆ)
    - ? ë‹ˆë©”ì´???€??(?¼ë°˜, ??ŒŸ, ?ˆì–´ë¯¸ìŠ¤)
    - ê²°ê³¼ ë©”ì‹œì§€
    - ?¨ì? ?¤í? ?Ÿìˆ˜
    """
    try:
        user_id = current_user.id
        
        # ?¤í? ê°€???¬ë? ì²´í¬
        daily_limit = 3
        spins_used_today = 0  # ?¤ì œë¡œëŠ” DB?ì„œ ì¡°íšŒ
        spins_left = max(0, daily_limit - spins_used_today)
        
        if spins_left <= 0:
            return RouletteSpinResponse(
                success=False,
                message="?¤ëŠ˜???¤í? ?Ÿìˆ˜ë¥?ëª¨ë‘ ?¬ìš©?ˆìŠµ?ˆë‹¤. ?´ì¼ ?¤ì‹œ ?œë„?´ì£¼?¸ìš”!",
                spins_left=0,
                cooldown_expires=datetime.now() + timedelta(hours=24)
            )
        
        # ë£°ë › ?¤í? ?œë??ˆì´??
        prizes = [
            {"id": "coin_50", "name": "50 ì½”ì¸", "probability": 30, "type": "normal"},
            {"id": "coin_100", "name": "100 ì½”ì¸", "probability": 25, "type": "normal"},
            {"id": "coin_200", "name": "200 ì½”ì¸", "probability": 20, "type": "normal"},
            {"id": "gem_5", "name": "5 ??, "probability": 15, "type": "rare"},
            {"id": "gem_10", "name": "10 ??, "probability": 8, "type": "rare"},
            {"id": "jackpot", "name": "??ŒŸ! 1000 ì½”ì¸", "probability": 2, "type": "jackpot"}
        ]
        
        # ?•ë¥  ê¸°ë°˜ ?¹ì²¨ ê²°ì •
        rand = random.randint(1, 100)
        cumulative = 0
        selected_prize = prizes[0]  # ê¸°ë³¸ê°?
        
        for prize in prizes:
            cumulative += prize["probability"]
            if rand <= cumulative:
                selected_prize = prize
                break
        
        # ê²°ê³¼ ë©”ì‹œì§€ ?ì„±
        message = f"?‰ {selected_prize['name']}??ë¥? ?ë“?ˆìŠµ?ˆë‹¤!"
        animation_type = selected_prize["type"]
        
        if selected_prize["type"] == "jackpot":
            message = f"?° JACKPOT! {selected_prize['name']}??ë¥? ?ë“?ˆìŠµ?ˆë‹¤!"
        
        # ?¤í? ???¨ì? ?Ÿìˆ˜
        remaining_spins = spins_left - 1
        
        return RouletteSpinResponse(
            success=True,
            result=selected_prize["id"],
            message=message,
            spins_left=remaining_spins,
            animation_type=animation_type,
            prize_name=selected_prize["name"]
        )
    except Exception as e:
        logger.error(f"ë£°ë › ?¤í? ì²˜ë¦¬ ?¤íŒ¨: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ë£°ë › ?¤í? ì²˜ë¦¬ ì¤??¤ë¥˜ê°€ ë°œìƒ?ˆìŠµ?ˆë‹¤."
        )


# ê´€ë¦¬ì??API
@router.get("/admin/stats", response_model=Dict[str, Any])
async def get_roulette_admin_stats(
    db = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    ?„ë¼?´ì¦ˆ ë£°ë › ê´€ë¦¬ì ?µê³„ë¥?ì¡°íšŒ?©ë‹ˆ??
    - ?¼ì¼ ?¤í? ?Ÿìˆ˜
    - ?í’ˆë³??¹ì²¨ ?µê³„
    - ??ŒŸ ë°œìƒ ?´ì—­
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ê´€ë¦¬ìë§??‘ê·¼?????ˆìŠµ?ˆë‹¤."
        )
    
    try:
        # ?¤ì œ ?µê³„ ?°ì´??ê³„ì‚° (?„ì¬??ëª¨ì˜ ?°ì´??
        today = datetime.now().date()
        
        # ëª¨ì˜ ?µê³„ ?°ì´???ì„±
        stats = {
            "today_stats": {
                "daily_spins": random.randint(50, 200),
                "active_users": random.randint(15, 50),
                "total_prizes_given": random.randint(100, 400),
                "jackpot_count": random.randint(0, 3)
            },
            "prize_distribution": {
                "coin_50": random.randint(20, 80),
                "coin_100": random.randint(15, 60),
                "coin_200": random.randint(10, 40),
                "gem_5": random.randint(5, 25),
                "gem_10": random.randint(2, 15),
                "jackpot": random.randint(0, 3)
            },
            "user_engagement": {
                "total_registered_users": random.randint(500, 1500),
                "daily_active_users": random.randint(50, 200),
                "retention_rate": round(random.uniform(0.3, 0.8), 2)
            },
            "revenue_metrics": {
                "coins_distributed": random.randint(10000, 50000),
                "gems_distributed": random.randint(500, 2000),
                "premium_conversions": random.randint(5, 25)
            }
        }
        
        return stats
    except Exception as e:
        logger.error(f"ê´€ë¦¬ì ?µê³„ ì¡°íšŒ ?¤íŒ¨: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ê´€ë¦¬ì ?µê³„ë¥?ë¶ˆëŸ¬?¤ëŠ” ì¤??¤ë¥˜ê°€ ë°œìƒ?ˆìŠµ?ˆë‹¤."
        )
