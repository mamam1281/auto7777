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
    nickname: str
    phone_number: str


class SignUpRequest(BaseModel):
    nickname: str
    phone_number: str
    invite_code: str


class VerifyInviteRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nickname: str
    cyber_token_balance: int


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
    """회원 가입 처리 - 닉네임과 전화번호로 가입"""
    # 닉네임 중복 검사
    if db.query(models.User).filter(models.User.nickname == data.nickname).first():
        logger.warning("Signup failed: nickname %s already taken", data.nickname)
        raise HTTPException(status_code=400, detail="Nickname already taken")
    
    # 전화번호 중복 검사
    if db.query(models.User).filter(models.User.phone_number == data.phone_number).first():
        logger.warning("Signup failed: phone number %s already taken", data.phone_number)
        raise HTTPException(status_code=400, detail="Phone number already taken")
    
    # 초대코드 검증
    invite = db.query(models.InviteCode).filter(
        models.InviteCode.code == data.invite_code,
        models.InviteCode.is_used == False
    ).first()
    if not invite:
        logger.warning("Signup failed: invalid invite code %s", data.invite_code)
        raise HTTPException(status_code=400, detail="Invalid invite code")
    
    # 사용자 생성 (비밀번호 없이)
    user = models.User(
        nickname=data.nickname, 
        phone_number=data.phone_number,
        invite_code=data.invite_code
    )
    db.add(user)
    invite.is_used = True  # type: ignore
    db.commit()
    db.refresh(user)
    
    # 초기 토큰 지급
    token_service.add_tokens(int(user.id), INITIAL_CYBER_TOKENS)  # type: ignore[arg-type]
    access_token = create_access_token({"sub": str(user.id)})
    logger.info("Signup success for nickname %s, phone %s", data.nickname, data.phone_number)
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """로그인 처리 - 닉네임과 전화번호로 인증"""
    # 테스트용 계정
    if data.nickname == "testuser" and data.phone_number == "010-1234-5678":
        logger.info("Test login for %s", data.nickname)
        return TokenResponse(access_token="fake-token")

    # 닉네임과 전화번호로 사용자 찾기
    user = db.query(models.User).filter(
        models.User.nickname == data.nickname,
        models.User.phone_number == data.phone_number
    ).first()
    
    if not user:
        logger.warning("Login failed for nickname %s, phone %s", data.nickname, data.phone_number)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": str(user.id)})
    logger.info("Login success for nickname %s, phone %s", data.nickname, data.phone_number)
    return TokenResponse(access_token=access_token)


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
