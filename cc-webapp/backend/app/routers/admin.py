from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
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

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

@router.get("/users", response_model=List[UserAdminResponse])
def list_users(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
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
def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent activities
    activities = db.query(UserActivity).filter(
        UserActivity.user_id == user_id
    ).order_by(UserActivity.timestamp.desc()).limit(10).all()
    
    # Get recent rewards
    rewards = db.query(Reward).filter(
        Reward.user_id == user_id
    ).order_by(Reward.created_at.desc()).limit(10).all()
    
    return {
        "id": user.id,
        "site_id": user.site_id,
        "nickname": user.nickname,
        "phone_number": user.phone_number,
        "cyber_token_balance": user.cyber_token_balance,
        "rank": user.rank,
        "created_at": user.created_at,
        "recent_activities": activities,
        "recent_rewards": rewards
    }

@router.get("/activities", response_model=List[ActivityResponse])
def list_activities(
    skip: int = 0, 
    limit: int = 100, 
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List user activities with optional user filtering
    """
    query = db.query(UserActivity).join(User)
    
    if user_id:
        query = query.filter(UserActivity.user_id == user_id)
    
    activities = query.order_by(UserActivity.timestamp.desc()).offset(skip).limit(limit).all()
    return activities

@router.post("/rewards", response_model=RewardResponse)
def give_reward(reward_data: GiveRewardRequest, db: Session = Depends(get_db)):
    """
    Give a reward to a user
    """
    # Check if user exists
    user = db.query(User).filter(User.id == reward_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create reward record
    new_reward = Reward(
        user_id=reward_data.user_id,
        reward_type=reward_data.reward_type,
        amount=reward_data.amount,
        reason=reward_data.reason,
    # dependencies=[Depends(get_current_admin)]  # TODO: 관리자 인증/권한 처리
        admin_id=reward_data.admin_id,
        created_at=datetime.now()
    )
    db.add(new_reward)
    
    # Update user's cyber token balance
    user.cyber_token_balance += reward_data.amount
    
    # Create an activity record for this reward
    activity = UserActivity(
        user_id=reward_data.user_id,
        activity_type="REWARD_RECEIVED",
        details=f"Received {reward_data.amount} {reward_data.reward_type} tokens. Reason: {reward_data.reason}"
    )
    db.add(activity)
    
    db.commit()
    db.refresh(new_reward)
    
    return new_reward
