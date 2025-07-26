from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from pydantic import BaseModel
from typing import Optional, List
import logging

from ..database import get_db
from .. import models
from .auth import get_user_from_token

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)


class UserSummary(BaseModel):
    id: int
    site_id: str  # phone_number 필드를 사이트ID로 표시
    nickname: str
    phone_number: str  # 실제 전화번호 (추후 추가될 필드)
    rank: str
    cyber_token_balance: int
    created_at: datetime


class UserDetail(BaseModel):
    id: int
    site_id: str
    nickname: str
    phone_number: str
    rank: str
    cyber_token_balance: int
    created_at: datetime
    invite_code: str
    total_actions: int
    last_activity: Optional[datetime]


class RewardHistory(BaseModel):
    id: int
    reward_type: str
    amount: int
    description: str
    created_at: datetime


class ActionHistory(BaseModel):
    id: int
    action_type: str
    value: float
    timestamp: datetime


class UsersListResponse(BaseModel):
    users: List[UserSummary]
    total: int
    page: int
    per_page: int


class GiveRewardRequest(BaseModel):
    user_id: int
    reward_type: str  # "CYBER_TOKEN", "GIFT_CARD", "SHOP_ITEM"
    amount: int
    description: str


class GiftCardRequest(BaseModel):
    user_id: int
    card_type: str  # "STARBUCKS", "GOOGLE_PLAY", "APPLE_STORE"
    amount: int
    description: str


class ShopItemRequest(BaseModel):
    user_id: int
    item_name: str
    item_value: int
    description: str


def check_admin_permission(user_id: int):
    """관리자 권한 확인 (user_id == 1만 허용)"""
    if user_id != 1:
        raise HTTPException(status_code=403, detail="Admin permission required")


@router.get("/users", response_model=UsersListResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search_site_id: Optional[str] = Query(None),
    search_nickname: Optional[str] = Query(None),
    search_phone: Optional[str] = Query(None),
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 전체 유저 조회 - 3가지 요소로 검색"""
    check_admin_permission(user_id)
    
    query = db.query(models.User)
    
    # 검색 조건 추가
    filters = []
    if search_site_id:
        filters.append(models.User.phone_number.ilike(f"%{search_site_id}%"))
    if search_nickname:
        filters.append(models.User.nickname.ilike(f"%{search_nickname}%"))
    # search_phone은 추후 실제 전화번호 필드 추가 시 구현
    
    if filters:
        query = query.filter(or_(*filters))
    
    # 전체 개수
    total = query.count()
    
    # 페이징
    offset = (page - 1) * per_page
    users = query.offset(offset).limit(per_page).all()
    
    # 응답 데이터 변환
    user_summaries = []
    for user in users:
        user_summaries.append(UserSummary(
            id=user.id,
            site_id=user.phone_number,  # phone_number를 사이트ID로 사용
            nickname=user.nickname,
            phone_number="미등록",  # 추후 실제 전화번호 필드 추가 시 변경
            rank=user.rank,
            cyber_token_balance=user.cyber_token_balance,
            created_at=user.created_at
        ))
    
    logger.info("Admin %s retrieved %d users (page %d)", user_id, len(user_summaries), page)
    
    return UsersListResponse(
        users=user_summaries,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/users/{target_user_id}", response_model=UserDetail)
async def get_user_detail(
    target_user_id: int,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 특정 유저 상세 정보 조회"""
    check_admin_permission(user_id)
    
    user = db.query(models.User).filter(models.User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 활동 통계 계산
    total_actions = db.query(models.UserAction).filter(
        models.UserAction.user_id == target_user_id
    ).count()
    
    last_activity = db.query(models.UserAction.timestamp).filter(
        models.UserAction.user_id == target_user_id
    ).order_by(models.UserAction.timestamp.desc()).first()
    
    logger.info("Admin %s viewed user detail for user %s", user_id, target_user_id)
    
    return UserDetail(
        id=user.id,
        site_id=user.phone_number,  # phone_number를 사이트ID로 사용
        nickname=user.nickname,
        phone_number="미등록",  # 추후 실제 전화번호 필드 추가 시 변경
        rank=user.rank,
        cyber_token_balance=user.cyber_token_balance,
        created_at=user.created_at,
        invite_code=user.invite_code,
        total_actions=total_actions,
        last_activity=last_activity[0] if last_activity else None
    )


@router.get("/users/{target_user_id}/rewards")
async def get_user_rewards(
    target_user_id: int,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 유저 보상 내역 조회"""
    check_admin_permission(user_id)
    
    user = db.query(models.User).filter(models.User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # UserReward 테이블에서 보상 내역 조회
    rewards = db.query(models.UserReward).filter(
        models.UserReward.user_id == target_user_id
    ).order_by(desc(models.UserReward.created_at)).limit(50).all()
    
    reward_history = []
    for reward in rewards:
        reward_history.append(RewardHistory(
            id=reward.id,
            reward_type=reward.reward_type,
            amount=reward.amount,
            description=reward.description or "",
            created_at=reward.created_at
        ))
    
    return {"rewards": reward_history}


@router.get("/users/{target_user_id}/actions")
async def get_user_actions(
    target_user_id: int,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 유저 활동 내역 조회"""
    check_admin_permission(user_id)
    
    user = db.query(models.User).filter(models.User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # UserAction 테이블에서 활동 내역 조회
    actions = db.query(models.UserAction).filter(
        models.UserAction.user_id == target_user_id
    ).order_by(desc(models.UserAction.timestamp)).limit(100).all()
    
    action_history = []
    for action in actions:
        action_history.append(ActionHistory(
            id=action.id,
            action_type=action.action_type,
            value=action.value,
            timestamp=action.timestamp
        ))
    
    return {"actions": action_history}


@router.put("/users/{target_user_id}/rank")
async def update_user_rank(
    target_user_id: int,
    new_rank: str,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 유저 랭크 변경"""
    check_admin_permission(user_id)
    
    valid_ranks = ["STANDARD", "PREMIUM", "VIP"]
    if new_rank not in valid_ranks:
        raise HTTPException(status_code=400, detail=f"Invalid rank. Must be one of: {valid_ranks}")
    
    user = db.query(models.User).filter(models.User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_rank = user.rank
    user.rank = new_rank
    db.commit()
    
    logger.info("Admin %s changed user %s rank from %s to %s", user_id, target_user_id, old_rank, new_rank)
    
    return {"message": f"User rank updated from {old_rank} to {new_rank}"}


@router.post("/rewards/cyber-tokens")
async def give_cyber_tokens(
    request: GiveRewardRequest,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 사이버 토큰 지급"""
    check_admin_permission(user_id)
    
    target_user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 사이버 토큰 지급
    target_user.cyber_token_balance += request.amount
    
    # 보상 내역 기록
    reward = models.UserReward(
        user_id=request.user_id,
        reward_type="CYBER_TOKEN",
        amount=request.amount,
        description=request.description,
        created_at=datetime.utcnow()
    )
    db.add(reward)
    
    # 활동 내역 기록
    action = models.UserAction(
        user_id=request.user_id,
        action_type="ADMIN_REWARD_CYBER_TOKEN",
        value=float(request.amount),
        timestamp=datetime.utcnow()
    )
    db.add(action)
    
    db.commit()
    
    logger.info("Admin %s gave %d cyber tokens to user %s", user_id, request.amount, request.user_id)
    
    return {
        "message": f"Successfully gave {request.amount} cyber tokens to user {request.user_id}",
        "new_balance": target_user.cyber_token_balance
    }


@router.post("/rewards/gift-card")
async def give_gift_card(
    request: GiftCardRequest,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 상품권 지급"""
    check_admin_permission(user_id)
    
    target_user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    valid_card_types = ["STARBUCKS", "GOOGLE_PLAY", "APPLE_STORE", "AMAZON", "GIFTICON"]
    if request.card_type not in valid_card_types:
        raise HTTPException(status_code=400, detail=f"Invalid card type. Must be one of: {valid_card_types}")
    
    # 상품권 지급 내역 기록
    reward = models.UserReward(
        user_id=request.user_id,
        reward_type=f"GIFT_CARD_{request.card_type}",
        amount=request.amount,
        description=request.description,
        created_at=datetime.utcnow()
    )
    db.add(reward)
    
    # 활동 내역 기록
    action = models.UserAction(
        user_id=request.user_id,
        action_type=f"ADMIN_REWARD_GIFT_CARD",
        value=float(request.amount),
        timestamp=datetime.utcnow()
    )
    db.add(action)
    
    db.commit()
    
    logger.info("Admin %s gave %s gift card (%d원) to user %s", 
                user_id, request.card_type, request.amount, request.user_id)
    
    return {
        "message": f"Successfully gave {request.card_type} gift card ({request.amount}원) to user {request.user_id}",
        "card_type": request.card_type,
        "amount": request.amount
    }


@router.post("/rewards/shop-item")
async def give_shop_item(
    request: ShopItemRequest,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 상점 아이템 지급"""
    check_admin_permission(user_id)
    
    target_user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 상점 아이템 지급 내역 기록
    reward = models.UserReward(
        user_id=request.user_id,
        reward_type="SHOP_ITEM",
        amount=request.item_value,
        description=f"{request.item_name}: {request.description}",
        created_at=datetime.utcnow()
    )
    db.add(reward)
    
    # 활동 내역 기록
    action = models.UserAction(
        user_id=request.user_id,
        action_type="ADMIN_REWARD_SHOP_ITEM",
        value=float(request.item_value),
        timestamp=datetime.utcnow()
    )
    db.add(action)
    
    db.commit()
    
    logger.info("Admin %s gave shop item '%s' (value: %d) to user %s", 
                user_id, request.item_name, request.item_value, request.user_id)
    
    return {
        "message": f"Successfully gave shop item '{request.item_name}' to user {request.user_id}",
        "item_name": request.item_name,
        "item_value": request.item_value
    }


@router.get("/rewards/statistics")
async def get_reward_statistics(
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """관리자용 보상 통계 조회"""
    check_admin_permission(user_id)
    
    # 전체 보상 통계
    total_cyber_tokens = db.query(models.UserReward).filter(
        models.UserReward.reward_type == "CYBER_TOKEN"
    ).count()
    
    total_gift_cards = db.query(models.UserReward).filter(
        models.UserReward.reward_type.like("GIFT_CARD_%")
    ).count()
    
    total_shop_items = db.query(models.UserReward).filter(
        models.UserReward.reward_type == "SHOP_ITEM"
    ).count()
    
    # 최근 7일 보상 내역
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_rewards = db.query(models.UserReward).filter(
        models.UserReward.created_at >= seven_days_ago
    ).order_by(desc(models.UserReward.created_at)).limit(20).all()
    
    recent_reward_list = []
    for reward in recent_rewards:
        user = db.query(models.User).filter(models.User.id == reward.user_id).first()
        recent_reward_list.append({
            "id": reward.id,
            "user_nickname": user.nickname if user else "Unknown",
            "reward_type": reward.reward_type,
            "amount": reward.amount,
            "description": reward.description,
            "created_at": reward.created_at
        })
    
    return {
        "statistics": {
            "total_cyber_tokens_given": total_cyber_tokens,
            "total_gift_cards_given": total_gift_cards,
            "total_shop_items_given": total_shop_items
        },
        "recent_rewards": recent_reward_list
    }
