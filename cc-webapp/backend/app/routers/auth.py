"""?�증 관??API ?�우??""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ..database import get_db
from ..schemas.auth import UserCreate, UserLogin, AdminLogin, UserResponse, Token
from ..services.auth_service import AuthService, security
from ..models.auth_models import User, InviteCode
from ..config_simple import settings

# 로거 ?�정
logger = logging.getLogger(__name__)

# Auth service ?�스?�스
auth_service = AuthService()

# OAuth2 ?�키�?
oauth2_scheme = HTTPBearer()

# ?�정값들
JWT_EXPIRE_MINUTES = settings.jwt_expire_minutes
INITIAL_CYBER_TOKENS = getattr(settings, 'initial_cyber_tokens', 200)

router = APIRouter(tags=["authentication"])


@router.post("/signup", response_model=Token)
async def signup(
    data: UserCreate,
    db = Depends(get_db)
):
    """?�용???�원가??(?�수 5�??�력: ?�이?�아?�디, ?�네?? ?�화번호, 초�?코드, 비�?번호)"""
    try:
        logger.info(f"?�원가???�도: site_id={data.site_id}, nickname={data.nickname}")
        
        # AuthService�??�한 ?�용???�성
        user = auth_service.create_user(db, data)
        
        # ?�큰 ?�성
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # ?�용???�답 ?�이???�성
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
        
        logger.info(f"?�원가???�공: user_id={user.id}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="?�원가??처리 �??�류가 발생?�습?�다")


@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db = Depends(get_db)
):
    """?�용??로그??""
    try:
        logger.info(f"로그???�도: site_id={form_data.site_id}")
        
        # ?�용???�증
        user = auth_service.authenticate_user(form_data.site_id, form_data.password, db)
        if not user:
            logger.warning(f"로그???�패: ?�못???�격 증명 - site_id={form_data.site_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="?�못???�이??ID ?�는 비�?번호?�니??,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # ?�큰 ?�성
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # 마�?�?로그???�간 ?�데?�트
        user.last_login = datetime.utcnow()
        db.commit()
        
        # ?�용???�답 ?�이???�성
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
        
        logger.info(f"로그???�공: user_id={user.id}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="로그??처리 �??�류가 발생?�습?�다")
