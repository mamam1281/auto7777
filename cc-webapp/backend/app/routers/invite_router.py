"""
초�?코드 관??API ?�우??
- 초�?코드 ?�효??검�?API (/api/invite/validate)
- 고정 초�?코드: 6969, 6974, 2560
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body

from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.services.invite_service import InviteService
from app.schemas.invite_code import InviteCodeResponse, InviteCodeList
from app.core.error_handlers import UserServiceException

# 초�?코드 ?�성 ?�청 ?�키�?
class InviteCodeGenerateRequest(BaseModel):
    count: Optional[int] = 1
    length: Optional[int] = 6
    max_uses: Optional[int] = 1
    days_valid: Optional[int] = 30

# ?�우???�정
router = APIRouter(
    prefix="/api/invite",
    tags=["invite"],
    responses={404: {"description": "Not found"}},
)

@router.get("/validate/{code}", response_model=dict)
async def validate_invite_code(
    code: str = Path(..., description="검증할 초�?코드"),
    db = Depends(get_db)
):
    """
    초�?코드 ?�효??검�?API
    
    Args:
        code: 검증할 초�?코드
        db: ?�이?�베?�스 ?�션
        
    Returns:
        ?�효??검�?결과
        
    Raises:
        HTTPException: 초�?코드가 ?�효?��? ?��? 경우
    """
    invite_service = InviteService(db)
    try:
        result = invite_service.validate_invite_code(code)
        return {
            "valid": True,
            "detail": "?�효??초�?코드?�니??",
            "code": result["code"],
            "created_at": result["created_at"],
            "is_special": result["is_special"]
        }
    except UserServiceException as e:
        return {
            "valid": False,
            "detail": e.message,
            "error_code": e.error_code
        }

@router.get("/list", response_model=InviteCodeList)
async def list_invite_codes(
    limit: int = Query(10, description="조회??최�? ??�� ??),
    offset: int = Query(0, description="조회 ?�작??),
    db = Depends(get_db)
):
    """
    초�?코드 목록 조회
    
    Args:
        limit: 조회??최�? ??�� ??
        offset: 조회 ?�작??
        db: ?�이?�베?�스 ?�션
        
    Returns:
        초�?코드 목록
    """
    invite_service = InviteService(db)
    invite_codes = invite_service.list_invite_codes(limit, offset)
    
    return {
        "invite_codes": invite_codes
    }

@router.post("/generate", response_model=InviteCodeList)
async def generate_invite_codes(
    request: InviteCodeGenerateRequest = Body(...),
    db = Depends(get_db)
):
    """
    보안???��? 초�?코드 ?�성 API
    
    Args:
        request: 초�?코드 ?�성 ?�청 ?�보
        db: ?�이?�베?�스 ?�션
        
    Returns:
        ?�성??초�?코드 목록
    """
    invite_service = InviteService(db)
    
    # ?�라미터 검�?
    if request.count <= 0:
        return HTTPException(status_code=400, detail="?�성??코드 ?�는 1 ?�상?�어???�니??")
    if request.length < 4:
        return HTTPException(status_code=400, detail="코드 길이??최소 4???�상?�어???�니??")
    
    # ?�??초�?코드 ?�성
    invite_codes = invite_service.generate_bulk_invite_codes(
        count=request.count,
        length=request.length,
        max_uses=request.max_uses,
        days_valid=request.days_valid
    )
    
    return {
        "invite_codes": invite_codes
    }

@router.get("/{code}", response_model=InviteCodeResponse)
async def get_invite_code(
    code: str = Path(..., description="조회??초�?코드"),
    db = Depends(get_db)
):
    """
    ?�정 초�?코드 조회 API
    
    Args:
        code: 조회??초�?코드
        db: ?�이?�베?�스 ?�션
        
    Returns:
        초�?코드 ?�보
    """
    invite_service = InviteService(db)
    invite_code = invite_service.get_invite_code(code)
    
    if not invite_code:
        raise HTTPException(status_code=404, detail=f"초�?코드 {code}�?찾을 ???�습?�다.")
    
    return invite_code
