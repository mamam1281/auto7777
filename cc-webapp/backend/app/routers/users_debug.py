"""
간단한 프로필 API 버전 (디버깅용)
"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Optional

from app.auth.simple_auth import get_current_user
from app.database import get_db
from app.models.auth_clean import User

router = APIRouter()

@router.get("/users/{user_id}/profile")
async def get_user_profile_simple(
    user_id: int = Path(..., description="조회할 사용자 ID"),
    current_user_id: Optional[int] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """간단한 프로필 조회 API (디버깅용)"""
    
    print(f"[DEBUG] current_user_id: {current_user_id}")
    print(f"[DEBUG] target user_id: {user_id}")
    
    # 조회 대상 사용자 확인
    target_user = db.query(User).filter(User.id == user_id).first()
    print(f"[DEBUG] target_user found: {target_user is not None}")
    
    if not target_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 간단한 응답 반환
    return {
        "user_id": target_user.id,
        "nickname": target_user.nickname,
        "rank": target_user.rank,
        "cyber_tokens": target_user.cyber_token_balance,
        "is_own_profile": current_user_id == user_id,
        "debug_info": {
            "current_user_id": current_user_id,
            "target_user_id": user_id
        }
    }
