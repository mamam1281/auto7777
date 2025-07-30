"""
Prize Roulette API Router
경품 룰렛 시스템을 위한 FastAPI 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    """상품 정보"""
    id: str
    name: str
    value: int
    color: str
    probability: float
    icon: Optional[str] = None

class PrizeRouletteInfoResponse(BaseModel):
    """룰렛 정보 응답"""
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    next_reset_time: datetime

class PrizeRouletteSpinRequest(BaseModel):
    """룰렛 스핀 요청"""
    user_id: Optional[str] = "temp_user"  # 임시 사용자 ID

class PrizeRouletteSpinResponse(BaseModel):
    """룰렛 스핀 응답"""
    success: bool
    prize: Optional[Prize] = None
    message: str
    spins_left: int
    cooldown_expires: Optional[datetime] = None
    is_near_miss: Optional[bool] = False
    animation_type: Optional[str] = "normal"

# === Constants ===

PRIZES = [
    Prize(id="coins_100", name="코인 100개", value=100, color="#FFD700", probability=0.35, icon="🪙"),
    Prize(id="coins_500", name="코인 500개", value=500, color="#FFA500", probability=0.20, icon="💰"),
    Prize(id="coins_1000", name="코인 1000개", value=1000, color="#FF6B35", probability=0.15, icon="💎"),
    Prize(id="gems_10", name="젬 10개", value=10, color="#9D4EDD", probability=0.18, icon="💜"),
    Prize(id="gems_50", name="젬 50개", value=50, color="#7209B7", probability=0.10, icon="🔮"),
    Prize(id="jackpot", name="잭팟! 젬 200개", value=200, color="#FF0080", probability=0.015, icon="🎰"),
    Prize(id="bonus", name="보너스 스핀", value=1, color="#00FF88", probability=0.005, icon="🎁")
]

DAILY_SPIN_LIMIT = 3
SPIN_COOLDOWN_MINUTES = 0  # 스핀 간 쿨다운 없음 (일일 제한만)

# === Service Functions ===

def get_user_spin_data(user_id: str, db: Session) -> Dict[str, Any]:
    """사용자 스핀 데이터 조회 (임시: 메모리 기반)"""
    # 실제 구현에서는 데이터베이스에서 조회
    # 현재는 임시로 메모리 기반 구현
    today = datetime.now().date()
    
    # 임시 데이터 구조 (실제로는 DB 테이블)
    return {
        "user_id": user_id,
        "date": today,
        "spins_used": 0,  # 실제로는 DB에서 조회
        "last_spin_time": None
    }

def update_user_spin_data(user_id: str, db: Session) -> None:
    """사용자 스핀 데이터 업데이트 (임시: 메모리 기반)"""
    # 실제 구현에서는 데이터베이스에 저장
    pass

def select_prize_with_probability() -> Prize:
    """확률 기반 상품 선택"""
    random_value = random.random()
    cumulative_prob = 0.0
    
    for prize in PRIZES:
        cumulative_prob += prize.probability
        if random_value <= cumulative_prob:
            return prize
    
    # 확률 오차로 인해 아무것도 선택되지 않은 경우 첫 번째 상품 반환
    return PRIZES[0]

def is_near_miss(selected_prize: Prize, user_preferences: Optional[Dict] = None) -> bool:
    """근접 실패 여부 판단"""
    # 고가치 상품 근처에서 벗어난 경우를 근접 실패로 판단
    high_value_prizes = ["jackpot", "gems_50", "coins_1000"]
    
    if selected_prize.id not in high_value_prizes:
        # 40% 확률로 근접 실패 연출
        return random.random() < 0.4
    
    return False

# === API Endpoints ===

@router.get("/info", response_model=PrizeRouletteInfoResponse)
async def get_prize_roulette_info(
    user_id: str = "temp_user",
    db: Session = Depends(get_db)
):
    """
    룰렛 정보 조회
    - 남은 스핀 횟수
    - 쿨다운 상태
    - 다음 리셋 시간
    """
    try:
        spin_data = get_user_spin_data(user_id, db)
        
        # 오늘 사용한 스핀 횟수 계산
        spins_used = spin_data.get("spins_used", 0)
        spins_left = max(0, DAILY_SPIN_LIMIT - spins_used)
        
        # 다음 리셋 시간 (자정)
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return PrizeRouletteInfoResponse(
            spins_left=spins_left,
            next_reset_time=tomorrow
        )
        
    except Exception as e:
        logger.error(f"룰렛 정보 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 정보를 조회할 수 없습니다."
        )

@router.post("/spin", response_model=PrizeRouletteSpinResponse)
async def spin_roulette(
    request: PrizeRouletteSpinRequest,
    db: Session = Depends(get_db)
):
    """
    룰렛 스핀 실행
    - 유저 타입별 차등 확률 적용
    - 시간대별 승률 조정
    - 근접 실패 로직 적용
    """
    try:
        from ..services.roulette_service import RouletteService
        from ..repositories.game_repository import GameRepository
        
        # 서비스 초기화
        game_repo = GameRepository()
        roulette_service = RouletteService(game_repo)
        
        # 사용자 ID 처리 (임시로 숫자 변환)
        user_id = hash(request.user_id) % 1000000  # 문자열을 숫자로 변환
        
        # 룰렛 스핀 실행 (DB 세션 전달)
        result = roulette_service.spin_prize_roulette(user_id, db)
        
        # 응답 변환
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
        logger.error(f"룰렛 스핀 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"룰렛 스핀 중 오류가 발생했습니다: {str(e)}"
        )
    """
    룰렛 스핀 실행
    - 확률 기반 상품 선택
    - 사용자 제한 확인
    - 상품 지급 처리
    """
    try:
        user_id = request.user_id or "temp_user"
        
        # 사용자 스핀 데이터 조회
        spin_data = get_user_spin_data(user_id, db)
        spins_used = spin_data.get("spins_used", 0)
        
        # 스핀 횟수 제한 확인
        if spins_used >= DAILY_SPIN_LIMIT:
            return PrizeRouletteSpinResponse(
                success=False,
                message="오늘의 스핀 횟수를 모두 사용했습니다. 내일 다시 도전하세요!",
                spins_left=0
            )
        
        # 상품 선택
        selected_prize = select_prize_with_probability()
        
        # 근접 실패 여부 판단
        near_miss = is_near_miss(selected_prize)
        
        # 애니메이션 타입 결정
        animation_type = "normal"
        if selected_prize.id == "jackpot":
            animation_type = "jackpot"
        elif near_miss:
            animation_type = "near_miss"
        
        # 스핀 데이터 업데이트
        update_user_spin_data(user_id, db)
        
        # 상품 지급 처리 (실제 구현 시)
        # award_prize_to_user(user_id, selected_prize, db)
        
        # 성공 응답
        return PrizeRouletteSpinResponse(
            success=True,
            prize=selected_prize,
            message=f"축하합니다! {selected_prize.name}을(를) 획득했습니다!",
            spins_left=max(0, DAILY_SPIN_LIMIT - spins_used - 1),
            is_near_miss=near_miss,
            animation_type=animation_type
        )
        
    except Exception as e:
        logger.error(f"룰렛 스핀 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 스핀 중 오류가 발생했습니다."
        )

@router.get("/prizes", response_model=List[Prize])
async def get_available_prizes():
    """
    사용 가능한 상품 목록 조회
    """
    return PRIZES

@router.get("/history")
async def get_spin_history(
    user_id: str = "temp_user",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    사용자 스핀 히스토리 조회 (향후 구현)
    """
    # 실제 구현에서는 데이터베이스에서 히스토리 조회
    return {
        "message": "스핀 히스토리 기능은 준비 중입니다.",
        "history": []
    }
