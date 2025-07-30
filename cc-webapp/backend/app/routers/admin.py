from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models import User, UserActivity, Reward
from app.schemas.admin import (
    UserAdminResponse,
    ActivityResponse,
    UserDetailResponse,
    GiveRewardRequest,
    RewardResponse
)

# JWT 인증 의존성 임포트
from app.routers.auth_jwt import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

def require_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """관리자 권한 필요"""
    if current_user["rank"] not in ["ADMIN", "PREMIUM"]:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return current_user

@router.get("/users", response_model=List[UserAdminResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_user)
):
    """
    Get a list of all users with basic information for admin dashboard
    """
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.nickname.ilike(f"%{search}%")) |
            (User.site_id.ilike(f"%{search}%")) |
            (User.phone_number.ilike(f"%{search}%"))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserDetailResponse)
def get_user_detail(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_user)
):
    """
    Get detailed information about a specific user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user activities
    activities = db.query(UserActivity).filter(UserActivity.user_id == user_id).order_by(UserActivity.timestamp.desc()).limit(10).all()
    
    # Get user rewards
    rewards = db.query(Reward).filter(Reward.user_id == user_id).order_by(Reward.created_at.desc()).limit(10).all()
    
    return UserDetailResponse(
        id=user.id,
        site_id=user.site_id,
        nickname=user.nickname,
        phone_number=user.phone_number,
        rank=user.rank,
        cyber_token_balance=user.cyber_token_balance,
        created_at=user.created_at,
        activities=[ActivityResponse(
            id=activity.id,
            activity_type=activity.activity_type,
            timestamp=activity.timestamp,
            details=activity.details
        ) for activity in activities],
        rewards=[RewardResponse(
            id=reward.id,
            reward_type=reward.reward_type,
            amount=reward.amount,
            reason=reward.reason,
            created_at=reward.created_at
        ) for reward in rewards]
    )

@router.get("/activities", response_model=List[ActivityResponse])
def list_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_user)
):
    """
    Get a list of recent user activities
    """
    activities = db.query(UserActivity).order_by(UserActivity.timestamp.desc()).offset(skip).limit(limit).all()
    return activities

@router.post("/users/{user_id}/reward", response_model=RewardResponse)
def give_reward(
    user_id: int,
    reward_request: GiveRewardRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_user)
):
    """
    Give a reward to a specific user
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create reward record
    reward = Reward(
        user_id=user_id,
        reward_type=reward_request.reward_type,
        amount=reward_request.amount,
        reason=reward_request.reason,
        admin_id=current_user["id"]
    )
    
    db.add(reward)
    
    # Update user balance if it's a token reward
    if reward_request.reward_type == "CYBER_TOKEN":
        user.cyber_token_balance += reward_request.amount
    
    # Log the activity
    activity = UserActivity(
        user_id=user_id,
        activity_type=f"REWARD_GIVEN_{reward_request.reward_type}",
        details=f"Received {reward_request.amount} {reward_request.reward_type} from admin. Reason: {reward_request.reason}"
    )
    
    db.add(activity)
    db.commit()
    db.refresh(reward)
    
    return reward
