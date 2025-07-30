"""
고급 인증 API 라우터
- 리프레시 토큰 지원
- 세션 관리
- 로그인 시도 제한
- 강제 로그아웃
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..database import get_db
from ..models.user import User
from ..models.user_session import UserSession, LoginAttempt
from ..auth.advanced_jwt_handler import jwt_handler
from ..services.login_security import login_security
from ..services import token_service
from passlib.context import CryptContext
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def get_client_ip(request: Request) -> str:
    """클라이언트 IP 주소 추출"""
    # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 사용 시)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # X-Real-IP 헤더 확인
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 직접 연결된 클라이언트 IP
    if hasattr(request, "client") and request.client:
        return request.client.host
    
    return "unknown"


# Pydantic 스키마
class LoginRequest(BaseModel):
    site_id: str
    password: str
    device_info: Optional[str] = None


class SignUpRequest(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    site_id: str
    nickname: str
    phone_number: str
    cyber_token_balance: int
    rank: str
    last_login_at: Optional[datetime]
    login_count: int
    
    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: int
    device_info: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    last_used_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


def get_client_ip(request: Request) -> str:
    """클라이언트 IP 주소 추출"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host


def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)) -> User:
    """현재 사용자 인증"""
    try:
        # 토큰에서 Bearer 제거
        token = token.credentials
        
        # 토큰 검증
        payload = jwt_handler.verify_token(token, "access")
        user_id = int(payload.get("sub"))
        jti = payload.get("jti")
        
        # 블랙리스트 확인
        if jwt_handler.is_token_blacklisted(jti, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # 사용자 조회
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/signup", response_model=TokenResponse)
async def signup(
    data: SignUpRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    """회원가입"""
    # 기존 중복 검사 로직
    if db.query(User).filter(User.site_id == data.site_id).first():
        raise HTTPException(status_code=400, detail="Site ID already taken")
    
    if db.query(User).filter(User.nickname == data.nickname).first():
        raise HTTPException(status_code=400, detail="Nickname already taken")
    
    if db.query(User).filter(User.phone_number == data.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone number already taken")
    
    # 초대코드 검증
    from ..models.invite_code import InviteCode
    invite = db.query(InviteCode).filter(InviteCode.code == data.invite_code).first()
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid invite code")
    
    # 비밀번호 길이 체크
    if len(data.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
    
    # 사용자 생성
    password_hash = pwd_context.hash(data.password)
    user = User(
        site_id=data.site_id,
        nickname=data.nickname,
        phone_number=data.phone_number,
        password_hash=password_hash,
        invite_code=data.invite_code
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 초기 토큰 지급
    token_service.add_tokens(user.id, 200)
    
    # 세션 생성
    ip_address = get_client_ip(request)
    device_info = request.headers.get("User-Agent")
    session = jwt_handler.create_session(user.id, device_info, ip_address, db)
    
    # 액세스 토큰 생성
    access_token, access_jti = jwt_handler.create_access_token(user.id)
    session.access_token_jti = access_jti
    db.commit()
    
    logger.info(f"Signup success for site_id {data.site_id}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=session.refresh_token,
        expires_in=jwt_handler.access_token_expire_minutes * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """로그인"""
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    try:
        # 로그인 시도 전 검증
        login_security.validate_login_attempt(data.site_id, ip_address, db)
        
        # 사용자 조회
        user = db.query(User).filter(User.site_id == data.site_id).first()
        if not user:
            login_security.record_login_attempt(
                data.site_id, ip_address, False, "user_not_found", user_agent, db
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid site ID or password"
            )
        
        # 비밀번호 검증
        if not pwd_context.verify(data.password, user.password_hash):
            login_security.record_login_attempt(
                data.site_id, ip_address, False, "invalid_password", user_agent, db
            )
            login_security.update_login_failure(user, db)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid site ID or password"
            )
        
        # 로그인 성공
        login_security.record_login_attempt(
            data.site_id, ip_address, True, None, user_agent, db
        )
        login_security.update_login_success(user, db)
        
        # 세션 생성
        session = jwt_handler.create_session(
            user.id, data.device_info or user_agent, ip_address, db
        )
        
        # 액세스 토큰 생성
        access_token, access_jti = jwt_handler.create_access_token(user.id)
        session.access_token_jti = access_jti
        db.commit()
        
        logger.info(f"Login success for site_id {data.site_id}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=session.refresh_token,
            expires_in=jwt_handler.access_token_expire_minutes * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for site_id {data.site_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """토큰 갱신"""
    try:
        access_token, access_jti = jwt_handler.refresh_access_token(data.refresh_token, db)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=data.refresh_token,  # 기존 리프레시 토큰 유지
            expires_in=jwt_handler.access_token_expire_minutes * 60
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db)
):
    """로그아웃"""
    try:
        jwt_handler.logout_session(data.refresh_token, db)
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )


@router.post("/logout-all")
async def logout_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """모든 세션 강제 로그아웃"""
    jwt_handler.logout_all_sessions(current_user.id, "user_logout_all", db)
    return {"message": "All sessions logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """현재 사용자 정보 조회"""
    return current_user


@router.get("/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 활성 세션 목록"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).order_by(UserSession.last_used_at.desc()).all()
    
    return sessions


@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 세션 종료"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    jwt_handler.logout_session(session.refresh_token, db)
    return {"message": "Session terminated successfully"}


@router.post("/admin/force-logout/{user_id}")
async def admin_force_logout(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관리자: 사용자 강제 로그아웃"""
    # 관리자 권한 확인
    if current_user.rank != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    jwt_handler.logout_all_sessions(user_id, "admin_force_logout", db)
    return {"message": f"User {target_user.site_id} forcefully logged out"}


@router.post("/admin/unlock-account/{user_id}")
async def admin_unlock_account(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관리자: 계정 잠금 해제"""
    # 관리자 권한 확인
    if current_user.rank != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    login_security.unlock_account(target_user, db)
    return {"message": f"Account {target_user.site_id} unlocked successfully"}
