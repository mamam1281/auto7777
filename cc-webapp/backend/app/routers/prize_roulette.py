"""
Prize Roulette API Router
경품 룰렛 ?�스?�을 ?�한 FastAPI ?�우??
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
    """?�품 ?�보"""
    id: str
    name: str
    value: int
    color: str
    probability: float
    icon: Optional[str] = None

class PrizeRouletteInfoResponse(BaseModel):
    """룰렛 ?�보 ?�답"""
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    next_reset_time: datetime

class PrizeRouletteSpinRequest(BaseModel):
    """룰렛 ?��? ?�청"""
    user_id: Optional[str] = "temp_user"  # ?�시 ?�용??ID

class PrizeRouletteSpinResponse(BaseModel):
    """룰렛 ?��? ?�답"""
    success: bool
    prize: Optional[Prize] = None
    message: str
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    is_near_miss: Optional[bool] = False
    animation_type: Optional[str] = "normal"

# === Constants ===

PRIZES = [
    Prize(id="coins_100", name="코인 100�?, value=100, color="#FFD700", probability=0.35, icon="?��"),
    Prize(id="coins_500", name="코인 500�?, value=500, color="#FFA500", probability=0.20, icon="?��"),
    Prize(id="coins_1000", name="코인 1000�?, value=1000, color="#FF6B35", probability=0.15, icon="?��"),
    Prize(id="gems_10", name="??10�?, value=10, color="#9D4EDD", probability=0.18, icon="?��"),
    Prize(id="gems_50", name="??50�?, value=50, color="#7209B7", probability=0.10, icon="?��"),
    Prize(id="jackpot", name="??��! ??200�?, value=200, color="#FF0080", probability=0.015, icon="?��"),
    Prize(id="bonus", name="보너???��?", value=1, color="#00FF88", probability=0.005, icon="?��")
]

DAILY_SPIN_LIMIT = 3
SPIN_COOLDOWN_MINUTES = 0  # ?��? �?쿨다???�음 (?�일 ?�한�?

# === Service Functions ===

def get_user_spin_data(user_id: str, db: Session) -> Dict[str, Any]:
    """?�용???��? ?�이??조회 (?�시: 메모�?기반)"""
    # ?�제 구현?�서???�이?�베?�스?�서 조회
    # ?�재???�시�?메모�?기반 구현
    today = datetime.now().date()
    
    # ?�시 ?�이??구조 (?�제로는 DB ?�이�?
    return {
        "user_id": user_id,
        "date": today,
        "spins_used": 0,  # ?�제로는 DB?�서 조회
        "last_spin_time": None
    }

def update_user_spin_data(user_id: str, db: Session) -> None:
    """?�용???��? ?�이???�데?�트 (?�시: 메모�?기반)"""
    # ?�제 구현?�서???�이?�베?�스???�??
    pass

def select_prize_with_probability() -> Prize:
    """?�률 기반 ?�품 ?�택"""
    random_value = random.random()
    cumulative_prob = 0.0
    
    for prize in PRIZES:
        cumulative_prob += prize.probability
        if random_value <= cumulative_prob:
            return prize
    
    # ?�률 ?�차�??�해 ?�무것도 ?�택?��? ?��? 경우 �?번째 ?�품 반환
    return PRIZES[0]

def is_near_miss(selected_prize: Prize, user_preferences: Optional[Dict] = None) -> bool:
    """근접 ?�패 ?��? ?�단"""
    # 고�?�??�품 근처?�서 벗어??경우�?근접 ?�패�??�단
    high_value_prizes = ["jackpot", "gems_50", "coins_1000"]
    
    if selected_prize.id not in high_value_prizes:
        # 40% ?�률�?근접 ?�패 ?�출
        return random.random() < 0.4
    
    return False

# === API Endpoints ===

@router.get("/info", response_model=PrizeRouletteInfoResponse)
async def get_prize_roulette_info(
    user_id: str = "temp_user",
    db = Depends(get_db)
):
    """
    룰렛 ?�보 조회
    - ?��? ?��? ?�수
    - 쿨다???�태
    - ?�음 리셋 ?�간
    """
    try:
        spin_data = get_user_spin_data(user_id, db)
        
        # ?�늘 ?�용???��? ?�수 계산
        spins_used = spin_data.get("spins_used", 0)
        spins_left = max(0, DAILY_SPIN_LIMIT - spins_used)
        
        # ?�음 리셋 ?�간 (?�정)
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return PrizeRouletteInfoResponse(
            spins_left=spins_left,
            next_reset_time=tomorrow
        )
        
    except Exception as e:
        logger.error(f"룰렛 ?�보 조회 ?�패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 ?�보�?조회?????�습?�다."
        )

@router.post("/spin", response_model=PrizeRouletteSpinResponse)
async def spin_roulette(
    request: PrizeRouletteSpinRequest,
    db = Depends(get_db)
):
    """
    룰렛 ?��? ?�행
    - ?��? ?�?�별 차등 ?�률 ?�용
    - ?�간?��??�률 조정
    - 근접 ?�패 로직 ?�용
    """
    try:
        from ..services.roulette_service import RouletteService
        from ..repositories.game_repository import GameRepository
        
        # ?�비??초기??
        game_repo = GameRepository()
        roulette_service = RouletteService(game_repo)
        
        # ?�용??ID 처리 (?�시�??�자 변??
        user_id = hash(request.user_id) % 1000000  # 문자?�을 ?�자�?변??
        
        # 룰렛 ?��? ?�행 (DB ?�션 ?�달)
        result = roulette_service.spin_prize_roulette(user_id, db)
        
        # ?�답 변??
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
        logger.error(f"룰렛 ?��? ?�패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"룰렛 ?��? �??�류가 발생?�습?�다: {str(e)}"
        )
    """
    룰렛 ?��? ?�행
    - ?�률 기반 ?�품 ?�택
    - ?�용???�한 ?�인
    - ?�품 지�?처리
    """
    try:
        user_id = request.user_id or "temp_user"
        
        # ?�용???��? ?�이??조회
        spin_data = get_user_spin_data(user_id, db)
        spins_used = spin_data.get("spins_used", 0)
        
        # ?��? ?�수 ?�한 ?�인
        if spins_used >= DAILY_SPIN_LIMIT:
            return PrizeRouletteSpinResponse(
                success=False,
                message="?�늘???��? ?�수�?모두 ?�용?�습?�다. ?�일 ?�시 ?�전?�세??",
                spins_left=0
            )
        
        # ?�품 ?�택
        selected_prize = select_prize_with_probability()
        
        # 근접 ?�패 ?��? ?�단
        near_miss = is_near_miss(selected_prize)
        
        # ?�니메이???�??결정
        animation_type = "normal"
        if selected_prize.id == "jackpot":
            animation_type = "jackpot"
        elif near_miss:
            animation_type = "near_miss"
        
        # ?��? ?�이???�데?�트
        update_user_spin_data(user_id, db)
        
        # ?�품 지�?처리 (?�제 구현 ??
        # award_prize_to_user(user_id, selected_prize, db)
        
        # ?�공 ?�답
        return PrizeRouletteSpinResponse(
            success=True,
            prize=selected_prize,
            message=f"축하?�니?? {selected_prize.name}??�? ?�득?�습?�다!",
            spins_left=max(0, DAILY_SPIN_LIMIT - spins_used - 1),
            is_near_miss=near_miss,
            animation_type=animation_type
        )
        
    except Exception as e:
        logger.error(f"룰렛 ?��? ?�패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 ?��? �??�류가 발생?�습?�다."
        )

@router.get("/prizes", response_model=List[Prize])
async def get_available_prizes():
    """
    ?�용 가?�한 ?�품 목록 조회
    """
    return PRIZES

@router.get("/history")
async def get_spin_history(
    user_id: str = "temp_user",
    limit: int = 10,
    db = Depends(get_db)
):
    """
    ?�용???��? ?�스?�리 조회 (?�후 구현)
    """
    # ?�제 구현?�서???�이?�베?�스?�서 ?�스?�리 조회
    return {
        "message": "?��? ?�스?�리 기능?� 준�?중입?�다.",
        "history": []
    }
