"""
?���?간단??관리자 API ?�우??
관리자 ?�용 기능?�을 ?�공?�니??
"""

from fastapi import APIRouter, Depends, HTTPException, status

from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.auth_models import User
from app.auth.auth_service import AuthService

router = APIRouter(
    prefix="/admin",
    tags=["?���?관리자"],
    responses={404: {"description": "Not found"}},
)

def get_current_admin(db = Depends(get_db)) -> User:
    """관리자 권한???�는 ?�재 ?�용??반환"""
    # ?�제 구현?�서???�큰?�서 ?�용???�보�?가?��?????
    # 지금�? ?�스?�용?�로 관리자 ?�용?��? 반환
    admin_user = db.query(User).filter(User.nickname.like("%admin%")).first()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한???�요?�니??
        )
    return admin_user

@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """모든 ?�용??조회 (관리자 ?�용)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return {
        "total": len(users),
        "users": [
            {
                "id": user.id,
                "nickname": user.nickname,
                "rank": user.rank,
                "created_at": user.created_at,
                "last_login": user.last_login,
            }
            for user in users
        ]
    }

@router.get("/stats")
async def get_admin_stats(
    db = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """관리자 ?�?�보???�계"""
    total_users = db.query(User).count()
    
    return {
        "total_users": total_users,
        "active_users": total_users,  # ?�시�?같�? �?
        "admin_count": db.query(User).filter(User.nickname.like("%admin%")).count(),
        "system_status": "healthy"
    }

@router.get("/health")
async def admin_health_check():
    """관리자 API ?�태 ?�인"""
    return {"status": "healthy", "timestamp": datetime.now()}
