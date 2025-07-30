"""
단순 초대코드 기반 인증 라우터
- 복잡한 JWT, 비밀번호, 이메일 인증 제거  
- 초대코드로 즉시 가입 → 모든 서비스 접근 가능
- 랭크 시스템으로 서비스 레벨 제어
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserRegister, UserResponse, InviteCodeCreate, InviteCodeResponse, InviteCodeList
from app.auth.simple_auth import SimpleAuth
from app.models import InviteCode, User
from typing import List
import time

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
def register_with_invite_code(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """초대코드로 즉시 가입 - 모든 서비스 바로 이용 가능"""
    try:
        user = SimpleAuth.register_with_invite_code(
            invite_code=user_data.invite_code,
            nickname=user_data.nickname,
            db=db
        )
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/check-invite/{code}", response_model=dict)
def check_invite_code(
    code: str,
    db: Session = Depends(get_db)
):
    """초대코드 유효성 검사"""
    invite = db.query(InviteCode).filter(
        InviteCode.code == code
    ).first()
    
    if not invite:
        return {"valid": False, "message": "존재하지 않는 초대코드입니다"}
    
    if invite.is_used:
        return {"valid": False, "message": "이미 사용된 초대코드입니다"}
        
    return {"valid": True, "message": "유효한 초대코드입니다"}

@router.post("/invite-codes", response_model=List[InviteCodeResponse])
def create_invite_codes(
    invite_data: InviteCodeCreate,
    db: Session = Depends(get_db)
):
    """관리자용 초대코드 생성"""
    codes = []
    for _ in range(invite_data.count):
        code = InviteCode(
            code=SimpleAuth.generate_invite_code()
        )
        db.add(code)
        codes.append(code)
    
    db.commit()
    return codes

@router.get("/invite-codes", response_model=InviteCodeList)
def list_invite_codes(
    limit: int = 50,
    used: bool = None,
    db: Session = Depends(get_db)
):
    """초대코드 목록 조회"""
    query = db.query(InviteCode)
    
    if used is not None:
        query = query.filter(InviteCode.is_used == used)
    
    codes = query.order_by(InviteCode.created_at.desc()).limit(limit).all()
    total = query.count()
    
    return {
        "codes": codes,
        "total": total,
        "used_count": db.query(InviteCode).filter(InviteCode.is_used == True).count(),
        "available_count": db.query(InviteCode).filter(InviteCode.is_used == False).count()
    }

@router.get("/users/{nickname}", response_model=UserResponse)
def get_user_by_nickname(nickname: str, db: Session = Depends(get_db)):
    """닉네임으로 사용자 조회"""
    from app.models import User
    user = db.query(User).filter(User.nickname == nickname).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user
