"""
초대코드 관련 API 라우터
- 초대코드 유효성 검증 API (/api/invite/validate)
- 고정 초대코드: 6969, 6974, 2560
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.services.invite_service import InviteService
from app.schemas.invite_code import InviteCodeResponse, InviteCodeList
from app.core.error_handlers import UserServiceException

# 초대코드 생성 요청 스키마
class InviteCodeGenerateRequest(BaseModel):
    count: Optional[int] = 1
    length: Optional[int] = 6
    max_uses: Optional[int] = 1
    days_valid: Optional[int] = 30

# 라우터 설정
router = APIRouter(
    prefix="/api/invite",
    tags=["invite"],
    responses={404: {"description": "Not found"}},
)

@router.get("/validate/{code}", response_model=dict)
async def validate_invite_code(
    code: str = Path(..., description="검증할 초대코드"),
    db: Session = Depends(get_db)
):
    """
    초대코드 유효성 검증 API
    
    Args:
        code: 검증할 초대코드
        db: 데이터베이스 세션
        
    Returns:
        유효성 검증 결과
        
    Raises:
        HTTPException: 초대코드가 유효하지 않은 경우
    """
    invite_service = InviteService(db)
    try:
        result = invite_service.validate_invite_code(code)
        return {
            "valid": True,
            "detail": "유효한 초대코드입니다.",
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
    limit: int = Query(10, description="조회할 최대 항목 수"),
    offset: int = Query(0, description="조회 시작점"),
    db: Session = Depends(get_db)
):
    """
    초대코드 목록 조회
    
    Args:
        limit: 조회할 최대 항목 수
        offset: 조회 시작점
        db: 데이터베이스 세션
        
    Returns:
        초대코드 목록
    """
    invite_service = InviteService(db)
    invite_codes = invite_service.list_invite_codes(limit, offset)
    
    return {
        "invite_codes": invite_codes
    }

@router.post("/generate", response_model=InviteCodeList)
async def generate_invite_codes(
    request: InviteCodeGenerateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    보안성 높은 초대코드 생성 API
    
    Args:
        request: 초대코드 생성 요청 정보
        db: 데이터베이스 세션
        
    Returns:
        생성된 초대코드 목록
    """
    invite_service = InviteService(db)
    
    # 파라미터 검증
    if request.count <= 0:
        return HTTPException(status_code=400, detail="생성할 코드 수는 1 이상이어야 합니다.")
    if request.length < 4:
        return HTTPException(status_code=400, detail="코드 길이는 최소 4자 이상이어야 합니다.")
    
    # 대량 초대코드 생성
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
    code: str = Path(..., description="조회할 초대코드"),
    db: Session = Depends(get_db)
):
    """
    특정 초대코드 조회 API
    
    Args:
        code: 조회할 초대코드
        db: 데이터베이스 세션
        
    Returns:
        초대코드 정보
    """
    invite_service = InviteService(db)
    invite_code = invite_service.get_invite_code(code)
    
    if not invite_code:
        raise HTTPException(status_code=404, detail=f"초대코드 {code}를 찾을 수 없습니다.")
    
    return invite_code
