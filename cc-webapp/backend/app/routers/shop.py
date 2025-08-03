from fastapi import APIRouter, Depends, HTTPException
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

from ..services.shop_service import ShopService

def get_shop_service(db = Depends(get_db)) -> ShopService:
    """Dependency provider for ShopService."""
    return ShopService(db)

@router.post("/purchase", response_model=ShopPurchaseResponse, summary="?�이??구매", description="?�용?�의 ?�큰???�용?�여 ?�점???�이?�을 구매?�니??")
def purchase_shop_item(
    request: ShopPurchaseRequest,
    shop_service: ShopService = Depends(get_shop_service)
):
    """
    ### ?�청 본문:
    - **user_id**: ?�이?�을 구매?�는 ?�용??ID
    - **item_id**: 구매???�이?�의 ID
    - **item_name**: 구매???�이?�의 ?�름
    - **price**: ?�이??가�?
    - **description**: ?�이???�명 (?�택 ?�항)

    ### ?�답:
    - **success**: 구매 ?�공 ?��?
    - **message**: 처리 결과 메시지
    - **new_gold_balance**: 구매 ???�용?�의 ???�큰 ?�액
    - **item_id, item_name, new_item_count**: 구매???�이???�보 �?보유 개수
    """
    try:
        result = shop_service.purchase_item(
            user_id=request.user_id,
            item_id=request.item_id,
            item_name=request.item_name,
            price=request.price,
            description=request.description
        )
        if not result["success"]:
            # Handle the case of insufficient funds gracefully
            return ShopPurchaseResponse(
                success=False,
                message=result["message"],
                new_gold_balance=result["new_balance"],
                item_id=request.item_id,
                item_name=request.item_name,
                new_item_count=0
            )

        return ShopPurchaseResponse(
            success=True,
            message=result["message"],
            new_gold_balance=result["new_balance"],
            item_id=result["item_id"],
            item_name=result["item_name"],
            new_item_count=result["new_item_count"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
