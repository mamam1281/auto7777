"""
간소화된 인증 라우터
- 회원가입, 로그인, 토큰 갱신, 로그아웃
- 로그인 시도 제한 포함
- 중복 제거된 버전
"""

from datetime import datetime, timedelta
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
import logging
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models.auth_clean import User, InviteCode  # 우리가 만든 모델 사용
from ..auth.auth_service import auth_service  # 우리가 만든 서비스 사용

# 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "casino-club-secret-key-2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
INITIAL_CYBER_TOKENS = int(os.getenv("INITIAL_CYBER_TOKENS", "200"))

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic 모델들
class LoginRequest(BaseModel):
    site_id: str
    password: str


class SignUpRequest(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = JWT_EXPIRE_MINUTES * 60


class UserInfo(BaseModel):
    id: int
    site_id: str
    nickname: str
    phone_number: str
    cyber_token_balance: int
    rank: str
    last_login_at: Optional[datetime] = None


class VerifyInviteRequest(BaseModel):
    code: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# 유틸리티 함수들
def get_client_ip(request: Request) -> str:
    """클라이언트 IP 주소 추출"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def get_user_agent(request: Request) -> str:
    """User-Agent 헤더 추출"""
    return request.headers.get("User-Agent", "unknown")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """토큰에서 사용자 ID 추출"""
    payload = auth_service.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(payload.get("sub"))


# API 엔드포인트들
@router.post("/verify-invite")
async def verify_invite(req: VerifyInviteRequest, db: Session = Depends(get_db)):
    """초대 코드 검증"""
    code = db.query(InviteCode).filter(
        InviteCode.code == req.code,
        InviteCode.is_used == False
    ).first()
    
    is_valid = bool(code)
    logger.info("Invite code %s validity: %s", req.code, is_valid)
    return {"valid": is_valid}


@router.post(
    "/signup", 
    response_model=TokenResponse,
    summary="🔐 회원가입",
    description="""
    **초대코드를 사용하여 새 계정을 생성합니다.**
    
    ### ✨ 가입 특징:
    - 초대코드 + 닉네임만으로 간편 가입
    - 가입 즉시 200개 사이버 토큰 지급
    - 모든 게임 서비스 즉시 이용 가능
    
    ### 🎫 사용 가능한 초대코드:
    - `5858`: 일반 초대코드
    - `1234`: 테스트 초대코드  
    - `0000`: 개발자 초대코드
    - `6969`: 특별 초대코드
    
    ### 📝 필수 정보:
    - `site_id`: 사용자 고유 ID (3-20자)
    - `nickname`: 닉네임 (2-20자)
    - `phone_number`: 휴대폰 번호 (인증용)
    - `password`: 비밀번호 (8자 이상)
    - `invite_code`: 초대코드 (4자리)
    """
)
async def signup(
    request: Request,
    data: SignUpRequest,
    db: Session = Depends(get_db)
):
    """회원가입"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # 중복 검사들
    if db.query(User).filter(User.site_id == data.site_id).first():
        logger.warning("Signup failed: site_id %s already taken", data.site_id)
        raise HTTPException(status_code=400, detail="Site ID already taken")
    
    if db.query(User).filter(User.nickname == data.nickname).first():
        logger.warning("Signup failed: nickname %s already taken", data.nickname)
        raise HTTPException(status_code=400, detail="Nickname already taken")

    if db.query(User).filter(User.phone_number == data.phone_number).first():
        logger.warning("Signup failed: phone number %s already taken", data.phone_number)
        raise HTTPException(status_code=400, detail="Phone number already taken")

    # 초대코드 검증
    invite = db.query(InviteCode).filter(InviteCode.code == data.invite_code).first()
    if not invite:
        logger.warning("Signup failed: invalid invite code %s", data.invite_code)
        raise HTTPException(status_code=400, detail="Invalid invite code")

    # 비밀번호 검증
    if len(data.password) < 4:
        logger.warning("Signup failed: password too short")
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    # 사용자 생성
    password_hash = auth_service.hash_password(data.password)
    user = User(
        site_id=data.site_id,
        nickname=data.nickname,
        phone_number=data.phone_number,
        password_hash=password_hash,
        invite_code=data.invite_code,
        cyber_token_balance=INITIAL_CYBER_TOKENS
    )
    
    db.add(user)
    invite.is_used = True
    db.commit()
    db.refresh(user)

    # 토큰 생성
    session_id = auth_service.create_user_session(user.id, ip_address, user_agent, db)
    access_token = auth_service.create_access_token(user.id, session_id)
    refresh_token = auth_service.create_refresh_token()
    auth_service.save_refresh_token(user.id, refresh_token, ip_address, user_agent, db)

    logger.info("Signup success for site_id %s, nickname %s", data.site_id, data.nickname)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="🔑 로그인",
    description="""
    **사용자 계정으로 로그인하여 인증 토큰을 발급받습니다.**
    
    ### 🔒 보안 기능:
    - 로그인 시도 제한 (5회 실패 시 10분 제한)
    - IP 기반 접근 제한
    - JWT 액세스 토큰 + 리프레시 토큰 발급
    
    ### 📝 필수 정보:
    - `site_id`: 회원가입 시 설정한 사용자 ID
    - `password`: 계정 비밀번호
    
    ### 🎫 응답 토큰:
    - `access_token`: API 접근용 토큰 (60분 유효)
    - `refresh_token`: 토큰 갱신용 토큰 (7일 유효)
    - `token_type`: "bearer" (Authorization 헤더 형식)
    - `expires_in`: 토큰 만료 시간 (초 단위)
    """
)
async def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """로그인 (시도 제한 포함)"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # 로그인 시도 제한 확인
    is_allowed, remaining = auth_service.check_login_attempts(data.site_id, ip_address, db)
    if not is_allowed:
        auth_service.record_login_attempt(
            data.site_id, ip_address, user_agent, False, None, "account_locked", db
        )
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed login attempts. Try again later."
        )

    # 사용자 찾기
    user = db.query(User).filter(User.site_id == data.site_id).first()
    if not user:
        auth_service.record_login_attempt(
            data.site_id, ip_address, user_agent, False, None, "invalid_site_id", db
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 비밀번호 검증
    if not auth_service.verify_password(data.password, user.password_hash):
        auth_service.record_login_attempt(
            data.site_id, ip_address, user_agent, False, user.id, "invalid_password", db
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 성공 처리
    auth_service.record_login_attempt(
        data.site_id, ip_address, user_agent, True, user.id, None, db
    )
    
    # 최근 로그인 시간 업데이트
    user.last_login_at = datetime.utcnow()
    db.commit()

    # 토큰 생성
    session_id = auth_service.create_user_session(user.id, ip_address, user_agent, db)
    access_token = auth_service.create_access_token(user.id, session_id)
    refresh_token = auth_service.create_refresh_token()
    auth_service.save_refresh_token(user.id, refresh_token, ip_address, user_agent, db)

    logger.info("Login success for site_id %s", data.site_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """리프레시 토큰으로 액세스 토큰 갱신"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    payload = auth_service.verify_refresh_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = int(payload.get("sub"))
    refresh_jti = payload.get("jti")
    
    # 리프레시 토큰 유효성 확인
    if not auth_service.is_refresh_token_valid(user_id, refresh_jti, ip_address, db):
        raise HTTPException(status_code=401, detail="Refresh token not valid")
    
    # 새 토큰들 생성
    session_id = auth_service.create_user_session(user_id, ip_address, user_agent, db)
    access_token = auth_service.create_access_token(user_id, session_id)
    new_refresh_token = auth_service.create_refresh_token()
    
    # 기존 리프레시 토큰 무효화 및 새 토큰 저장
    auth_service.invalidate_refresh_token(user_id, refresh_jti, db)
    auth_service.save_refresh_token(user_id, new_refresh_token, ip_address, user_agent, db)
    
    logger.info("Token refreshed for user %s", user_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """로그아웃 (토큰 블랙리스트 포함)"""
    # Authorization 헤더에서 토큰 추출
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        # 토큰을 블랙리스트에 추가
        auth_service.blacklist_token(token, "user_logout")
    
    # 세션 로그아웃
    auth_service.logout_user_session(current_user_id, None, "user_logout", db)
    logger.info("User %s logged out with token blacklisted", current_user_id)
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_sessions(
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """모든 세션에서 로그아웃 (현재 토큰 블랙리스트 포함)"""
    # 현재 토큰을 블랙리스트에 추가
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        auth_service.blacklist_token(token, "user_logout_all")
    
    # 모든 세션 로그아웃
    auth_service.logout_all_user_sessions(current_user_id, "user_logout_all", db)
    logger.info("All sessions logged out for user %s with token blacklisted", current_user_id)
    return {"message": "Successfully logged out from all sessions"}


@router.get("/me", response_model=UserInfo)
async def get_me(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """현재 사용자 정보"""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfo(
        id=user.id,
        site_id=user.site_id,
        nickname=user.nickname,
        phone_number=user.phone_number,
        cyber_token_balance=user.cyber_token_balance,
        rank=user.rank,
        last_login_at=user.last_login_at
    )
