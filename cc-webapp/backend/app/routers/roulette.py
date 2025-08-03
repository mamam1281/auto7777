"""
PrizeRoulette 게임 API ?�우??

?�론?�엔?�의 PrizeRoulette.tsx 컴포?�트?�서 ?�용?�는 
??개의 주요 ?�드?�인?��? ?�공?�니??
1. GET /api/roulette/info - ?�용?�별 룰렛 ?�보 조회
2. POST /api/roulette/spin - 룰렛 ?��? ?�행 �?결과 반환
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

# 로깅 ?�정
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/roulette",
    tags=["roulette"],
    responses={404: {"description": "Not found"}},
)

# ?�라?�즈 룰렛 ?�비???�스?�스 ?�성
# ?�비???�존??주입???�한 ?�수
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
    ?�용?�의 ?�라?�즈 룰렛 ?�보�?조회?�니??
    - ?��? ?��? ?�수
    - ?�음 ?��?까�? ?��? ?�간 (?�는 경우)
    - 과거 ?��? ?�역 ?�약
    """
    try:
        # ?�제 ?�용???�이??기반 룰렛 ?�보 계산
        user_id = current_user.id
        
        # ?�늘???��? ?�수 계산 (기본�? 3??
        daily_limit = 3
        spins_used_today = 0  # ?�제로는 DB?�서 조회
        spins_left = max(0, daily_limit - spins_used_today)
        
        # ?�음 ?��? 가???�간 (쿨다?�이 ?�다�?
        next_spin_time = None
        if spins_left == 0:
            # ?�정??리셋
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
        logger.error(f"룰렛 ?�보 조회 ?�패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 ?�보�?불러?�는 �??�류가 발생?�습?�다."
        )


@router.post("/spin", response_model=RouletteSpinResponse)
async def spin_roulette(
    request: Optional[RouletteSpinRequest] = None,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    ?�라?�즈 룰렛???�리�?결과�?반환?�니??
    - ?��? 결과 (?�첨 ?�품)
    - ?�니메이???�??(?�반, ??��, ?�어미스)
    - 결과 메시지
    - ?��? ?��? ?�수
    """
    try:
        user_id = current_user.id
        
        # ?��? 가???��? 체크
        daily_limit = 3
        spins_used_today = 0  # ?�제로는 DB?�서 조회
        spins_left = max(0, daily_limit - spins_used_today)
        
        if spins_left <= 0:
            return RouletteSpinResponse(
                success=False,
                message="?�늘???��? ?�수�?모두 ?�용?�습?�다. ?�일 ?�시 ?�도?�주?�요!",
                spins_left=0,
                cooldown_expires=datetime.now() + timedelta(hours=24)
            )
        
        # 룰렛 ?��? ?��??�이??
        prizes = [
            {"id": "coin_50", "name": "50 코인", "probability": 30, "type": "normal"},
            {"id": "coin_100", "name": "100 코인", "probability": 25, "type": "normal"},
            {"id": "coin_200", "name": "200 코인", "probability": 20, "type": "normal"},
            {"id": "gem_5", "name": "5 ??, "probability": 15, "type": "rare"},
            {"id": "gem_10", "name": "10 ??, "probability": 8, "type": "rare"},
            {"id": "jackpot", "name": "??��! 1000 코인", "probability": 2, "type": "jackpot"}
        ]
        
        # ?�률 기반 ?�첨 결정
        rand = random.randint(1, 100)
        cumulative = 0
        selected_prize = prizes[0]  # 기본�?
        
        for prize in prizes:
            cumulative += prize["probability"]
            if rand <= cumulative:
                selected_prize = prize
                break
        
        # 결과 메시지 ?�성
        message = f"?�� {selected_prize['name']}??�? ?�득?�습?�다!"
        animation_type = selected_prize["type"]
        
        if selected_prize["type"] == "jackpot":
            message = f"?�� JACKPOT! {selected_prize['name']}??�? ?�득?�습?�다!"
        
        # ?��? ???��? ?�수
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
        logger.error(f"룰렛 ?��? 처리 ?�패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 ?��? 처리 �??�류가 발생?�습?�다."
        )


# 관리자??API
@router.get("/admin/stats", response_model=Dict[str, Any])
async def get_roulette_admin_stats(
    db = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    ?�라?�즈 룰렛 관리자 ?�계�?조회?�니??
    - ?�일 ?��? ?�수
    - ?�품�??�첨 ?�계
    - ??�� 발생 ?�역
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자�??�근?????�습?�다."
        )
    
    try:
        # ?�제 ?�계 ?�이??계산 (?�재??모의 ?�이??
        today = datetime.now().date()
        
        # 모의 ?�계 ?�이???�성
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
        logger.error(f"관리자 ?�계 조회 ?�패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="관리자 ?�계�?불러?�는 �??�류가 발생?�습?�다."
        )
