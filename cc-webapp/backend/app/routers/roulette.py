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

from app.db.database import get_db
from app.db.models import User
from app.core.auth import get_current_active_user
from app.schemas.game_schemas import RouletteInfoResponse, RouletteSpinRequest, RouletteSpinResponse
from app.services.game_service import PrizeRouletteService

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/roulette",
    tags=["roulette"],
    responses={404: {"description": "Not found"}},
)

# 프라이즈 룰렛 서비스 인스턴스 생성
roulette_service = PrizeRouletteService()

@router.get("/info", response_model=RouletteInfoResponse)
async def get_roulette_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    사용자의 프라이즈 룰렛 정보를 조회합니다.
    - 남은 스핀 횟수
    - 다음 스핀까지 남은 시간 (있는 경우)
    - 과거 스핀 내역 요약
    """
    try:
        info = await roulette_service.get_user_roulette_info(db, current_user.id)
        return info
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
    current_user: User = Depends(get_current_active_user)
):
    """
    프라이즈 룰렛을 돌리고 결과를 반환합니다.
    - 스핀 결과 (당첨 상품)
    - 애니메이션 타입 (일반, 잭팟, 니어미스)
    - 결과 메시지
    - 남은 스핀 횟수
    """
    try:
        # 사용자가 스핀할 수 있는지 확인
        can_spin = await roulette_service.check_user_can_spin(db, current_user.id)
        if not can_spin["can_spin"]:
            return RouletteSpinResponse(
                success=False,
                message=can_spin["message"],
                spins_left=can_spin["spins_left"],
                cooldown_expires=can_spin.get("cooldown_expires")
            )
            
        # 스핀 실행 및 결과 반환
        result = await roulette_service.spin_roulette(db, current_user.id)
        return result
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
    current_user: User = Depends(get_current_active_user)
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
        stats = await roulette_service.get_admin_stats(db)
        return stats
    except Exception as e:
        logger.error(f"관리자 통계 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="관리자 통계를 불러오는 중 오류가 발생했습니다."
        )
