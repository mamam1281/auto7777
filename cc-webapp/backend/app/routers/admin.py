"""
?› ï¸?ê°„ë‹¨??ê´€ë¦¬ì API ?¼ìš°??
ê´€ë¦¬ì ?„ìš© ê¸°ëŠ¥?¤ì„ ?œê³µ?©ë‹ˆ??
"""

from fastapi import APIRouter, Depends, HTTPException, status

from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.auth_models import User
from app.auth.auth_service import AuthService

router = APIRouter(
    prefix="/admin",
    tags=["?› ï¸?ê´€ë¦¬ì"],
    responses={404: {"description": "Not found"}},
)

def get_current_admin(db = Depends(get_db)) -> User:
    """ê´€ë¦¬ì ê¶Œí•œ???ˆëŠ” ?„ì¬ ?¬ìš©??ë°˜í™˜"""
    # ?¤ì œ êµ¬í˜„?ì„œ??? í°?ì„œ ?¬ìš©???•ë³´ë¥?ê°€?¸ì?????
    # ì§€ê¸ˆì? ?ŒìŠ¤?¸ìš©?¼ë¡œ ê´€ë¦¬ì ?¬ìš©?ë? ë°˜í™˜
    admin_user = db.query(User).filter(User.nickname.like("%admin%")).first()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ê´€ë¦¬ì ê¶Œí•œ???„ìš”?©ë‹ˆ??
        )
    return admin_user

@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """ëª¨ë“  ?¬ìš©??ì¡°íšŒ (ê´€ë¦¬ì ?„ìš©)"""
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
    """ê´€ë¦¬ì ?€?œë³´???µê³„"""
    total_users = db.query(User).count()
    
    return {
        "total_users": total_users,
        "active_users": total_users,  # ?„ì‹œë¡?ê°™ì? ê°?
        "admin_count": db.query(User).filter(User.nickname.like("%admin%")).count(),
        "system_status": "healthy"
    }

@router.get("/health")
async def admin_health_check():
    """ê´€ë¦¬ì API ?íƒœ ?•ì¸"""
    return {"status": "healthy", "timestamp": datetime.now()}
