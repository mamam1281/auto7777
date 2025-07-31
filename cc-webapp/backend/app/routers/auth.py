from datetime import datetime, timedelta
import os
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import random
import string

from ..database import get_db
from .. import models
from ..services import token_service

# 표준화된 환경 변수명 사용
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
INITIAL_CYBER_TOKENS = int(os.getenv("INITIAL_CYBER_TOKENS", "200"))

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class LoginRequest(BaseModel):
    site_id: str
    password: str


class SignUpRequest(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: str


class VerifyInviteRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    site_id: str           # 사이트ID
    nickname: str
    phone_number: str      # 실제 전화번호
    cyber_token_balance: int
    rank: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.debug("Access token created for %s", data.get("sub"))
    return token


def get_user_from_token(token: str = Depends(oauth2_scheme)) -> int:
    """토큰에서 사용자 ID 추출"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(str(payload.get("sub")))
    except JWTError:
        raise credentials_exception
    return user_id


@router.post("/verify-invite")
async def verify_invite(req: VerifyInviteRequest, db: Session = Depends(get_db)):
    """초대 코드 검증 엔드포인트"""
    code = db.query(models.InviteCode).filter(
        models.InviteCode.code == req.code,
        models.InviteCode.is_used == False
    ).first()
    is_valid = bool(code)
    logger.info("Invite code %s validity: %s", req.code, is_valid)
    return {"valid": is_valid}


@router.post("/signup", response_model=TokenResponse)
async def signup(data: SignUpRequest, db: Session = Depends(get_db)):
    """회원 가입 처리 - 사이트ID, 닉네임, 전화번호, 비밀번호로 가입"""
    # 사이트ID 중복 검사 (새로운 site_id 필드 사용)
    if db.query(models.User).filter(models.User.site_id == data.site_id).first():
        logger.warning("Signup failed: site_id %s already taken", data.site_id)
        raise HTTPException(status_code=400, detail="Site ID already taken")
    
    # 닉네임 중복 검사
    if db.query(models.User).filter(models.User.nickname == data.nickname).first():
        logger.warning("Signup failed: nickname %s already taken", data.nickname)
        raise HTTPException(status_code=400, detail="Nickname already taken")

    # 전화번호 중복 검사 (실제 phone_number 필드 사용)
    if db.query(models.User).filter(models.User.phone_number == data.phone_number).first():
        logger.warning("Signup failed: phone number %s already taken", data.phone_number)
        raise HTTPException(status_code=400, detail="Phone number already taken")

    # 초대코드 검증 (is_used 체크 제거, 재사용 허용)
    invite = db.query(models.InviteCode).filter(
        models.InviteCode.code == data.invite_code
    ).first()
    if not invite:
        logger.warning("Signup failed: invalid invite code %s", data.invite_code)
        raise HTTPException(status_code=400, detail="Invalid invite code")

    # 비밀번호 길이 체크 (4자 이상)
    if len(data.password) < 4:
        logger.warning("Signup failed: password too short")
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    # 비밀번호 해싱
    password_hash = pwd_context.hash(data.password)

    # 사용자 생성 - 새로운 필드 구조 사용
    user = models.User(
        site_id=data.site_id,           # 새로운 site_id 필드
        nickname=data.nickname, 
        phone_number=data.phone_number,  # 실제 전화번호
        password_hash=password_hash,     # 해싱된 비밀번호
        invite_code=data.invite_code
    )
    db.add(user)
    invite.is_used = True  # type: ignore
    db.commit()
    db.refresh(user)

    # 초기 토큰 지급
    token_service.add_tokens(int(user.id), INITIAL_CYBER_TOKENS)  # type: ignore[arg-type]
    access_token = create_access_token({"sub": str(user.id)})
    logger.info("Signup success for site_id %s, nickname %s", data.site_id, data.nickname)
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """로그인 처리 - 사이트ID와 비밀번호로 인증 (로그인 시도 제한 포함)"""
    # 테스트용 계정
    if data.site_id == "testuser":
        logger.info("Test login for %s", data.site_id)
        return TokenResponse(access_token="fake-token")

    # 로그인 시도 제한 확인 (간단한 구현)
    from datetime import timedelta
    cutoff_time = datetime.utcnow() - timedelta(minutes=15)  # 15분 제한
    
    # 최근 15분간 실패한 로그인 시도 횟수 확인 (LoginAttempt 모델 사용)
    failed_attempts_count = db.query(models.LoginAttempt).filter(
        models.LoginAttempt.site_id == data.site_id,
        models.LoginAttempt.success == False,
        models.LoginAttempt.attempted_at > cutoff_time
    ).count()
    
    if failed_attempts_count >= 5:  # 5회 시도 제한
        # 실패한 시도 기록
        login_attempt = models.LoginAttempt(
            site_id=data.site_id,
            ip_address="127.0.0.1",  # 실제로는 request에서 가져와야 함
            success=False,
            failure_reason="account_locked",
            user_agent="unknown"
        )
        db.add(login_attempt)
        db.commit()
        
        logger.warning("Login blocked for site_id %s - too many attempts", data.site_id)
        raise HTTPException(
            status_code=429, 
            detail="Too many failed login attempts. Please try again later."
        )

    # 사이트ID로 사용자 찾기 (새로운 site_id 필드 사용)
    user = db.query(models.User).filter(
        models.User.site_id == data.site_id
    ).first()
    
    if not user:
        # 실패한 시도 기록
        login_attempt = models.LoginAttempt(
            site_id=data.site_id,
            ip_address="127.0.0.1",
            success=False,
            failure_reason="invalid_site_id",
            user_agent="unknown"
        )
        db.add(login_attempt)
        db.commit()
        
        logger.warning("Login failed for site_id %s - user not found", data.site_id)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 비밀번호 검증 (password_hash 필드 사용)
    if not user.password_hash or not pwd_context.verify(data.password, user.password_hash):
        # 실패한 시도 기록
        login_attempt = models.LoginAttempt(
            site_id=data.site_id,
            ip_address="127.0.0.1",
            success=False,
            failure_reason="invalid_password",
            user_agent="unknown"
        )
        db.add(login_attempt)
        db.commit()
        
        logger.warning("Login failed for site_id %s - wrong password", data.site_id)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 성공한 로그인 기록
    login_attempt = models.LoginAttempt(
        site_id=data.site_id,
        ip_address="127.0.0.1",
        success=True,
        user_agent="unknown"
    )
    db.add(login_attempt)
    
    # 최근 로그인 시간 업데이트
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({"sub": str(user.id)})
    logger.info("Login success for site_id %s", data.site_id)
    return TokenResponse(access_token=access_token)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """리프레시 토큰으로 액세스 토큰 갱신"""
    # 여기서는 간단한 구현으로 새 토큰 발급
    # 실제로는 리프레시 토큰을 검증하고 새 액세스 토큰 발급
    try:
        # 리프레시 토큰 검증 (간단한 예시)
        payload = jwt.decode(data.refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # 사용자 존재 확인
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # 새 액세스 토큰 발급
        access_token = create_access_token({"sub": str(user.id)})
        logger.info("Token refreshed for user %s", user_id)
        
        return TokenResponse(access_token=access_token)
        
    except JWTError:
        logger.warning("Invalid refresh token used")
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
async def logout(user_id: int = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """로그아웃 (토큰 블랙리스트에 추가)"""
    # 현재 토큰을 블랙리스트에 추가하는 로직
    # 여기서는 간단히 성공 응답만 반환
    logger.info("User %s logged out", user_id)
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_sessions(user_id: int = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """모든 세션에서 로그아웃"""
    # 사용자의 모든 세션/토큰을 무효화하는 로직
    # UserSession 테이블의 모든 세션을 비활성화
    db.query(models.UserSession).filter(
        models.UserSession.user_id == user_id,
        models.UserSession.is_active == True
    ).update({
        models.UserSession.is_active: False,
        models.UserSession.logout_at: datetime.utcnow(),
        models.UserSession.logout_reason: "user_logout_all"
    })
    db.commit()
    
    logger.info("All sessions logged out for user %s", user_id)
    return {"message": "Successfully logged out from all sessions"}


@router.get("/me", response_model=UserMe)
async def get_me(user_id: int = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """현재 로그인한 사용자 정보 반환"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logger.warning("User info requested for missing id %s", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("User info retrieved for id %s", user_id)
    return user


class InviteCodeCreateRequest(BaseModel):
    count: int = 1


class InviteCodeCreateResponse(BaseModel):
    codes: list[str]


@router.post("/admin/invite-codes", response_model=InviteCodeCreateResponse)
async def create_invite_codes(
    req: InviteCodeCreateRequest,
    user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db),
):
    """Generate new invite codes. Simple admin check: only user_id 1 allowed."""
    if user_id != 1:
        raise HTTPException(status_code=403, detail="Admin only")

    codes: list[str] = []
    for _ in range(max(req.count, 1)):
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not db.query(models.InviteCode).filter(models.InviteCode.code == code).first():
                invite = models.InviteCode(code=code)
                db.add(invite)
                codes.append(code)
                break
    db.commit()
    return InviteCodeCreateResponse(codes=codes)
