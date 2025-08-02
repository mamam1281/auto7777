"""인증 관련 API 라우터"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth import UserCreate, UserLogin, AdminLogin, UserResponse, Token
from ..services.auth_service import AuthService, security
from ..models.auth_models import User
from ..models.invite_code import InviteCode
from ..config import settings

# 로거 설정
logger = logging.getLogger(__name__)

# Auth service 인스턴스
auth_service = AuthService()

# OAuth2 스키마
oauth2_scheme = HTTPBearer()

# 설정값들
JWT_EXPIRE_MINUTES = settings.jwt_expire_minutes
INITIAL_CYBER_TOKENS = getattr(settings, 'initial_cyber_tokens', 200)

router = APIRouter(tags=["authentication"])


@router.post("/signup", response_model=Token)
async def signup(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    """사용자 회원가입 (필수 5개 입력: 사이트아이디, 닉네임, 전화번호, 초대코드, 비밀번호)"""
    try:
        logger.info(f"회원가입 시도: site_id={data.site_id}, nickname={data.nickname}")
        
        # AuthService를 통한 사용자 생성
        user = auth_service.create_user(data, db)
        
        # 토큰 생성
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # 사용자 응답 데이터 생성
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            phone_number=user.phone_number,
            cyber_token_balance=user.cyber_token_balance,
            created_at=user.created_at,
            last_login=user.last_login,
            is_admin=user.is_admin,
            is_active=user.is_active
        )
        
        logger.info(f"회원가입 성공: user_id={user.id}")
        
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
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    """사용자 로그인"""
    try:
        logger.info(f"로그인 시도: site_id={form_data.site_id}")
        
        # 사용자 인증
        user = auth_service.authenticate_user(form_data.site_id, form_data.password, db)
        if not user:
            logger.warning(f"로그인 실패: 잘못된 자격 증명 - site_id={form_data.site_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 사이트 ID 또는 비밀번호입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 토큰 생성
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        db.commit()
        
        # 사용자 응답 데이터 생성
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            phone_number=user.phone_number,
            cyber_token_balance=user.cyber_token_balance,
            created_at=user.created_at,
            last_login=user.last_login,
            is_admin=user.is_admin,
            is_active=user.is_active
        )
        
        logger.info(f"로그인 성공: user_id={user.id}")
        
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
