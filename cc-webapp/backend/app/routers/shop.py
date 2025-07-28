from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .. import models
from ..database import get_db

router = APIRouter()

class ShopPurchaseRequest(BaseModel):
    user_id: int
    item_id: int
    item_name: str
    price: int
    description: Optional[str] = None

class ShopPurchaseResponse(BaseModel):
    success: bool
    message: str
    new_gold_balance: int
    item_id: int
    item_name: str
    new_item_count: int

@router.post("/shop/purchase", response_model=ShopPurchaseResponse)
def purchase_shop_item(request: ShopPurchaseRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.cyber_token_balance < request.price:
        return ShopPurchaseResponse(
            success=False,
            message="골드(토큰)가 부족합니다.",
            new_gold_balance=user.cyber_token_balance,
            item_id=request.item_id,
            item_name=request.item_name,
            new_item_count=0
        )
    # 차감
    user.cyber_token_balance -= request.price
    # 보유 아이템 증가 (UserReward에 기록)
    reward = models.UserReward(
        user_id=user.id,
        reward_type="SHOP_ITEM",
        reward_value=str(request.item_id),
        awarded_at=datetime.utcnow(),
        source_description=f"{request.item_name}: {request.description or ''}"
    )
    db.add(reward)
    db.commit()
    # 현재 보유 개수 계산
    item_count = db.query(models.UserReward).filter(
        models.UserReward.user_id == user.id,
        models.UserReward.reward_type == "SHOP_ITEM",
        models.UserReward.reward_value == str(request.item_id)
    ).count()
    return ShopPurchaseResponse(
        success=True,
        message=f"{request.item_name} 구매 성공!",
        new_gold_balance=user.cyber_token_balance,
        item_id=request.item_id,
        item_name=request.item_name,
        new_item_count=item_count
    )
