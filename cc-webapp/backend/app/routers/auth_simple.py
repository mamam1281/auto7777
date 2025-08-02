"""인증 관련 API 라우터 - 간소화된 버전"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth import UserCreate, UserLogin, AdminLogin, UserResponse, Token
from ..services.auth_service import AuthService
from ..models.auth_models import User

# 로거 설정
logger = logging.getLogger(__name__)

# Router 설정
router = APIRouter(tags=["authentication"])

# OAuth2 스키마
oauth2_scheme = HTTPBearer()

@router.get("/health")
async def health_check():
    """Auth 헬스체크"""
    return {"status": "healthy", "service": "auth"}

@router.post("/signup", response_model=Token)
async def signup(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    """회원가입"""
    try:
        # AuthService를 통해 사용자 생성
        user = AuthService.create_user(db, data)
        
        # JWT 토큰 생성
        access_token = AuthService.create_access_token(
            data={"sub": user.site_id, "user_id": user.id, "is_admin": user.is_admin}
        )
        
        # 마지막 로그인 시간 업데이트
        AuthService.update_last_login(db, user)
        
        # 사용자 응답 객체 생성
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            phone_number=user.phone_number,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="회원가입 처리 중 오류가 발생했습니다")

@router.post("/login", response_model=Token)
async def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    """로그인"""
    try:
        # 사용자 인증
        user = AuthService.authenticate_user(db, data.site_id, data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사이트 아이디 또는 비밀번호가 잘못되었습니다"
            )
        
        # JWT 토큰 생성
        access_token = AuthService.create_access_token(
            data={"sub": user.site_id, "user_id": user.id, "is_admin": user.is_admin}
        )
        
        # 마지막 로그인 시간 업데이트
        AuthService.update_last_login(db, user)
        
        # 사용자 응답 객체 생성
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            phone_number=user.phone_number,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="로그인 처리 중 오류가 발생했습니다")

@router.post("/admin/login", response_model=Token)
async def admin_login(
    data: AdminLogin,
    db: Session = Depends(get_db)
):
    """관리자 로그인"""
    try:
        # 관리자 인증
        user = AuthService.authenticate_admin(db, data.site_id, data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="관리자 아이디 또는 비밀번호가 잘못되었습니다"
            )
        
        # JWT 토큰 생성
        access_token = AuthService.create_access_token(
            data={"sub": user.site_id, "user_id": user.id, "is_admin": user.is_admin}
        )
        
        # 마지막 로그인 시간 업데이트
        AuthService.update_last_login(db, user)
        
        # 사용자 응답 객체 생성
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname or "관리자",
            phone_number=user.phone_number or "관리자",
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="관리자 로그인 처리 중 오류가 발생했습니다")

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """현재 사용자 정보 조회"""
    user = AuthService.get_current_user(db, credentials)
    return UserResponse(
        id=user.id,
        site_id=user.site_id,
        nickname=user.nickname,
        phone_number=user.phone_number,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login
    )
