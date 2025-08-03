"""?¸ì¦ ê´€??API ?¼ìš°??""
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

# ë¡œê±° ?¤ì •
logger = logging.getLogger(__name__)

# Auth service ?¸ìŠ¤?´ìŠ¤
auth_service = AuthService()

# OAuth2 ?¤í‚¤ë§?
oauth2_scheme = HTTPBearer()

# ?¤ì •ê°’ë“¤
JWT_EXPIRE_MINUTES = settings.jwt_expire_minutes
INITIAL_CYBER_TOKENS = getattr(settings, 'initial_cyber_tokens', 200)

router = APIRouter(tags=["authentication"])


@router.post("/signup", response_model=Token)
async def signup(
    data: UserCreate,
    db = Depends(get_db)
):
    """?¬ìš©???Œì›ê°€??(?„ìˆ˜ 5ê°??…ë ¥: ?¬ì´?¸ì•„?´ë””, ?‰ë„¤?? ?„í™”ë²ˆí˜¸, ì´ˆë?ì½”ë“œ, ë¹„ë?ë²ˆí˜¸)"""
    try:
        logger.info(f"?Œì›ê°€???œë„: site_id={data.site_id}, nickname={data.nickname}")
        
        # AuthServiceë¥??µí•œ ?¬ìš©???ì„±
        user = auth_service.create_user(db, data)
        
        # ? í° ?ì„±
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # ?¬ìš©???‘ë‹µ ?°ì´???ì„±
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
        
        logger.info(f"?Œì›ê°€???±ê³µ: user_id={user.id}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="?Œì›ê°€??ì²˜ë¦¬ ì¤??¤ë¥˜ê°€ ë°œìƒ?ˆìŠµ?ˆë‹¤")


@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db = Depends(get_db)
):
    """?¬ìš©??ë¡œê·¸??""
    try:
        logger.info(f"ë¡œê·¸???œë„: site_id={form_data.site_id}")
        
        # ?¬ìš©???¸ì¦
        user = auth_service.authenticate_user(form_data.site_id, form_data.password, db)
        if not user:
            logger.warning(f"ë¡œê·¸???¤íŒ¨: ?˜ëª»???ê²© ì¦ëª… - site_id={form_data.site_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="?˜ëª»???¬ì´??ID ?ëŠ” ë¹„ë?ë²ˆí˜¸?…ë‹ˆ??,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # ? í° ?ì„±
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # ë§ˆì?ë§?ë¡œê·¸???œê°„ ?…ë°?´íŠ¸
        user.last_login = datetime.utcnow()
        db.commit()
        
        # ?¬ìš©???‘ë‹µ ?°ì´???ì„±
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
        
        logger.info(f"ë¡œê·¸???±ê³µ: user_id={user.id}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="ë¡œê·¸??ì²˜ë¦¬ ì¤??¤ë¥˜ê°€ ë°œìƒ?ˆìŠµ?ˆë‹¤")
