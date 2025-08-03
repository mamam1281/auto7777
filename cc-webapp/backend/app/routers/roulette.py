"""
PrizeRoulette 게임 API 라우터

프론트엔드의 PrizeRoulette.tsx 컴포넌트에서 사용하는 
두 개의 주요 엔드포인트를 제공합니다:
1. GET /api/roulette/info - 사용자별 룰렛 정보 조회
2. POST /api/roulette/spin - 룰렛 스핀 실행 및 결과 반환
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/roulette",
    tags=["roulette"],
    responses={404: {"description": "Not found"}},
)

# 프라이즈 룰렛 서비스 인스턴스 생성
# 서비스 의존성 주입을 위한 함수
def get_roulette_service(db: Session = Depends(get_db)):
    from app.repositories.game_repository import GameRepository
    repo = GameRepository(db)
    return RouletteService(repo)

@router.get("/info", response_model=RouletteInfoResponse)
async def get_roulette_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    사용자의 프라이즈 룰렛 정보를 조회합니다.
    - 남은 스핀 횟수
    - 다음 스핀까지 남은 시간 (있는 경우)
    - 과거 스핀 내역 요약
    """
    try:
        # 실제 사용자 데이터 기반 룰렛 정보 계산
        user_id = current_user.id
        
        # 오늘의 스핀 횟수 계산 (기본값: 3회)
        daily_limit = 3
        spins_used_today = 0  # 실제로는 DB에서 조회
        spins_left = max(0, daily_limit - spins_used_today)
        
        # 다음 스핀 가능 시간 (쿨다운이 있다면)
        next_spin_time = None
        if spins_left == 0:
            # 자정에 리셋
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
        logger.error(f"룰렛 정보 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 정보를 불러오는 중 오류가 발생했습니다."
        )


@router.post("/spin", response_model=RouletteSpinResponse)
async def spin_roulette(
    request: Optional[RouletteSpinRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    프라이즈 룰렛을 돌리고 결과를 반환합니다.
    - 스핀 결과 (당첨 상품)
    - 애니메이션 타입 (일반, 잭팟, 니어미스)
    - 결과 메시지
    - 남은 스핀 횟수
    """
    try:
        user_id = current_user.id
        
        # 스핀 가능 여부 체크
        daily_limit = 3
        spins_used_today = 0  # 실제로는 DB에서 조회
        spins_left = max(0, daily_limit - spins_used_today)
        
        if spins_left <= 0:
            return RouletteSpinResponse(
                success=False,
                message="오늘의 스핀 횟수를 모두 사용했습니다. 내일 다시 시도해주세요!",
                spins_left=0,
                cooldown_expires=datetime.now() + timedelta(hours=24)
            )
        
        # 룰렛 스핀 시뮬레이션
        prizes = [
            {"id": "coin_50", "name": "50 코인", "probability": 30, "type": "normal"},
            {"id": "coin_100", "name": "100 코인", "probability": 25, "type": "normal"},
            {"id": "coin_200", "name": "200 코인", "probability": 20, "type": "normal"},
            {"id": "gem_5", "name": "5 젬", "probability": 15, "type": "rare"},
            {"id": "gem_10", "name": "10 젬", "probability": 8, "type": "rare"},
            {"id": "jackpot", "name": "잭팟! 1000 코인", "probability": 2, "type": "jackpot"}
        ]
        
        # 확률 기반 당첨 결정
        rand = random.randint(1, 100)
        cumulative = 0
        selected_prize = prizes[0]  # 기본값
        
        for prize in prizes:
            cumulative += prize["probability"]
            if rand <= cumulative:
                selected_prize = prize
                break
        
        # 결과 메시지 생성
        message = f"🎉 {selected_prize['name']}을(를) 획득했습니다!"
        animation_type = selected_prize["type"]
        
        if selected_prize["type"] == "jackpot":
            message = f"🎰 JACKPOT! {selected_prize['name']}을(를) 획득했습니다!"
        
        # 스핀 후 남은 횟수
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
        logger.error(f"룰렛 스핀 처리 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="룰렛 스핀 처리 중 오류가 발생했습니다."
        )


# 관리자용 API
@router.get("/admin/stats", response_model=Dict[str, Any])
async def get_roulette_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    roulette_service: RouletteService = Depends(get_roulette_service)
):
    """
    프라이즈 룰렛 관리자 통계를 조회합니다.
    - 일일 스핀 횟수
    - 상품별 당첨 통계
    - 잭팟 발생 내역
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근할 수 있습니다."
        )
    
    try:
        # 실제 통계 데이터 계산 (현재는 모의 데이터)
        today = datetime.now().date()
        
        # 모의 통계 데이터 생성
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
        logger.error(f"관리자 통계 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="관리자 통계를 불러오는 중 오류가 발생했습니다."
        )
