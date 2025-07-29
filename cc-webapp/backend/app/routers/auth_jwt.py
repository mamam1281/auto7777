"""
JWT 인증 관련 API 엔드포인트
- 토큰 발급 (로그인)
- 토큰 리프레시
- 닉네임+초대코드 로그인
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.jwt_auth import (
    create_tokens, refresh_access_token,
    UserAuth, UserLogin, Token
)
from app.auth.simple_auth import SimpleAuth
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["인증"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 호환 토큰 발급 엔드포인트
    - username: 닉네임
    - password: 초대코드
    """
    # 닉네임과 초대코드로 사용자 조회
    user = db.query(User).filter(
        User.nickname == form_data.username,
        User.invite_code == form_data.password
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 닉네임 또는 초대코드입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성
    return create_tokens(user.id, user.rank)

@router.post("/login", response_model=Token)
async def login_with_nickname_invite(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    닉네임과 초대코드를 이용한 로그인 (JWT 토큰 발급)
    """
    # 닉네임과 초대코드로 사용자 조회
    user = db.query(User).filter(
        User.nickname == login_data.nickname,
        User.invite_code == login_data.invite_code
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 닉네임 또는 초대코드입니다"
        )
    
    # 토큰 생성
    return create_tokens(user.id, user.rank)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    리프레시 토큰을 사용하여 새 액세스 토큰 발급
    """
    return refresh_access_token(refresh_token, db)
