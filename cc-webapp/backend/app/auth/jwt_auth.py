"""
JWT 토큰 기반 인증 시스템
- 토큰 생성, 검증, 리프레시 기능 구현
- VIP/PREMIUM/STANDARD 등급별 접근제어
- OAuth 호환 토큰 발급 엔드포인트
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# JWT 설정
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # 실제 환경에서는 환경변수로 관리해야 합니다
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 토큰 관련 모델
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: int  # Unix timestamp

class TokenData(BaseModel):
    user_id: Optional[int] = None
    rank: Optional[str] = None

# 사용자 관련 모델
class UserAuth(BaseModel):
    id: int
    nickname: str
    rank: str
    is_active: bool = True

class UserLogin(BaseModel):
    nickname: str
    invite_code: str

# JWT 토큰 생성
def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def create_tokens(user_id: int, rank: str) -> Token:
    """액세스 토큰과 리프레시 토큰 생성"""
    # 액세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"sub": str(user_id), "rank": rank},
        expires_delta=access_token_expires
    )
    
    # 리프레시 토큰 생성
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_jwt_token(
        data={"sub": str(user_id), "refresh": True},
        expires_delta=refresh_token_expires
    )
    
    # 만료 시간 계산 (Unix timestamp)
    expires_at = int((datetime.utcnow() + access_token_expires).timestamp())
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_at=expires_at
    )

# 액세스 토큰 검증
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserAuth:
    """현재 인증된 사용자 정보 가져오기"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        rank: str = payload.get("rank")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=int(user_id), rank=rank)
    except JWTError:
        raise credentials_exception
        
    # DB에서 사용자 정보 조회
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return UserAuth(
        id=user.id,
        nickname=user.nickname,
        rank=user.rank,
        is_active=True
    )

# 등급별 접근 제어
def get_user_by_rank(required_rank: str = "STANDARD"):
    """특정 랭크 이상의 사용자만 접근 가능"""
    async def get_user_if_has_rank(current_user: UserAuth = Depends(get_current_user)) -> UserAuth:
        rank_hierarchy = {
            "VIP": 3,
            "PREMIUM": 2, 
            "STANDARD": 1
        }
        
        user_level = rank_hierarchy.get(current_user.rank, 0)
        required_level = rank_hierarchy.get(required_rank, 1)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="접근 권한이 부족합니다"
            )
            
        return current_user
    
    return get_user_if_has_rank

# 토큰 리프레시
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Token:
    """리프레시 토큰으로 새 액세스 토큰 발급"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="리프레시 토큰이 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 리프레시 토큰 디코딩
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        is_refresh: bool = payload.get("refresh", False)
        
        if user_id is None or not is_refresh:
            raise credentials_exception
            
        # DB에서 사용자 정보 조회
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if user is None:
            raise credentials_exception
            
        # 새 토큰 발급
        return create_tokens(user.id, user.rank)
    except JWTError:
        raise credentials_exception
