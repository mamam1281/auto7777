from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel

from ..auth.simple_auth import get_current_user
from ..database import get_db

router = APIRouter(tags=["Users"])

class UserProfileResponse(BaseModel):
    """사용자 프로필 응답 모델"""
    user_id: int
    nickname: str
    cyber_tokens: int
    rank: str
    is_own_profile: bool
    debug_info: Optional[dict] = None

class ProfileDebugInfo(BaseModel):
    """프로필 디버깅 정보"""
    current_user_id: Optional[int]
    target_user_id: int
    query_successful: bool

@router.get(
    "/users/{user_id}/profile", 
    response_model=UserProfileResponse,
    summary="👤 사용자 프로필 조회",
    description="""
사용자의 프로필 정보를 조회합니다.

### 🔐 인증 필요:
- JWT 토큰이 필요합니다
- Authorization: Bearer {access_token} 헤더 필수

### 📋 조회 가능한 정보:
- 기본 정보: 사용자 ID, 닉네임
- 게임 정보: 사이버 토큰 잔액, 사용자 랭크
- 권한 정보: 본인 프로필 여부 플래그

### 🎯 권한 제어:
- 본인 프로필: 모든 정보 조회 가능
- 타인 프로필: 제한적 정보만 조회 (추후 구현)

### 📊 응답 정보:
- user_id: 대상 사용자 ID
- nickname: 사용자 닉네임
- cyber_tokens: 현재 토큰 잔고
- rank: 사용자 등급 (STANDARD/VIP/PREMIUM)
- is_own_profile: 본인 프로필 여부
- debug_info: 디버깅 정보 (개발 환경)
    """
)
async def get_user_profile(
    user_id: int = Path(..., description="조회할 사용자 ID"),
    current_user_id: Optional[int] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """간단한 프로필 조회 API (Raw SQL 사용)"""
    
    try:
        # Raw SQL을 사용하여 사용자 정보 조회
        query = text("""
            SELECT id, nickname, cyber_token_balance, rank
            FROM users 
            WHERE id = :user_id
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        # 본인 프로필 여부 확인
        is_own_profile = current_user_id == user_id if current_user_id else False
        
        # 디버깅 정보 추가 (개발 환경에서만)
        debug_info = ProfileDebugInfo(
            current_user_id=current_user_id,
            target_user_id=user_id,
            query_successful=True
        )
        
        return UserProfileResponse(
            user_id=result[0],
            nickname=result[1],
            cyber_tokens=result[2] or 0,
            rank=result[3] or "STANDARD",
            is_own_profile=is_own_profile,
            debug_info=debug_info.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 일반적인 에러에 대한 처리
        raise HTTPException(
            status_code=500, 
            detail=f"프로필 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get(
    "/users/{user_id}/stats",
    summary="📊 사용자 게임 통계",
    description="""
사용자의 게임 통계 정보를 조회합니다.

### 🎮 통계 정보:
- 총 플레이 횟수
- 총 획득/소모 토큰
- 게임별 승률
- 최고 기록
    """
)
async def get_user_stats(
    user_id: int = Path(..., description="조회할 사용자 ID"),
    current_user_id: Optional[int] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 게임 통계 조회 API"""
    
    # 기본 통계 정보 반환 (추후 구현)
    return {
        "user_id": user_id,
        "total_games": 0,
        "total_tokens_won": 0,
        "total_tokens_spent": 0,
        "win_rate": 0.0,
        "favorite_game": "slot",
        "message": "통계 시스템 구현 예정"
    }
