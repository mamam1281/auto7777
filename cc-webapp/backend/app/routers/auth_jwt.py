"""
JWT 인증 라우터
Casino-Club F2P 백엔드 JWT 토큰 기반 인증 시스템
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import base64
import hashlib
import hmac
from pydantic import BaseModel

from ..database import get_db
from ..core.logging import get_logger, log_service_call
from ..core.error_handlers import AuthenticationException, AuthorizationException

# 라우터 생성
router = APIRouter(prefix="/auth", tags=["authentication", "jwt"])

# 로거 및 설정
logger = get_logger("auth")
security = HTTPBearer()

# JWT 설정 (모의 구현)
JWT_SECRET_KEY = "casino_club_secret_key_2025"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# 간단한 JWT 모의 구현
class SimpleJWT:
    @staticmethod
    def encode(payload: dict, secret: str, algorithm: str = "HS256") -> str:
        """간단한 JWT 인코딩"""
        header = {"alg": algorithm, "typ": "JWT"}
        
        # Base64 인코딩
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).decode().rstrip('=')
        
        # 서명 생성
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        signature_b64 = base64.urlsafe_b64encode(signature.encode()).decode().rstrip('=')
        
        return f"{header_b64}.{payload_b64}.{signature_b64}"
    
    @staticmethod
    def decode(token: str, secret: str, algorithms: list = None) -> dict:
        """간단한 JWT 디코딩"""
        try:
            header_b64, payload_b64, signature_b64 = token.split('.')
            
            # 서명 검증
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
            expected_signature_b64 = base64.urlsafe_b64encode(expected_signature.encode()).decode().rstrip('=')
            
            if signature_b64 != expected_signature_b64:
                raise ValueError("Invalid signature")
            
            # 페이로드 디코딩
            payload_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_padded)
            payload = json.loads(payload_bytes.decode())
            
            # 만료 시간 확인
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                if isinstance(exp_timestamp, str):
                    exp_dt = datetime.fromisoformat(exp_timestamp.replace('Z', '+00:00'))
                else:
                    exp_dt = datetime.fromtimestamp(exp_timestamp)
                
                if datetime.utcnow() > exp_dt:
                    raise ValueError("Token expired")
            
            return payload
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")

# 간단한 패스워드 해싱
def hash_password(password: str) -> str:
    """간단한 패스워드 해싱"""
    salt = "casino_club_salt_2025"
    combined = f"{password}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """패스워드 검증"""
    return hash_password(password) == hashed

# 요청/응답 모델
class LoginRequest(BaseModel):
    invite_code: str
    nickname: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    nickname: Optional[str] = None
    rank: Optional[str] = None
    expires_at: Optional[datetime] = None

# 유틸리티 함수
def create_access_token(user_data: Dict[str, Any]) -> str:
    """JWT 액세스 토큰 생성"""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = {
        "user_id": user_data["id"],
        "nickname": user_data["nickname"],
        "rank": user_data.get("rank", "STANDARD"),
        "exp": expiration.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "type": "access_token"
    }
    
    token = SimpleJWT.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token: str) -> Dict[str, Any]:
    """JWT 토큰 검증"""
    try:
        payload = SimpleJWT.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except ValueError as e:
        error_msg = str(e)
        if "expired" in error_msg.lower():
            raise AuthenticationException("토큰이 만료되었습니다.")
        else:
            raise AuthenticationException("유효하지 않은 토큰입니다.")

# 의존성 함수
async def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """현재 사용자 토큰 검증"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise AuthenticationException("인증에 실패했습니다.")

async def get_current_user(token_payload: Dict[str, Any] = Depends(get_current_user_token)) -> Dict[str, Any]:
    """현재 사용자 정보 반환"""
    return {
        "id": token_payload["user_id"],
        "nickname": token_payload["nickname"],
        "rank": token_payload["rank"]
    }

async def require_vip_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """VIP 이상 사용자 권한 필요"""
    if current_user["rank"] not in ["VIP", "PREMIUM"]:
        raise AuthorizationException("VIP 등급 이상이 필요합니다.")
    return current_user

async def require_premium_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """PREMIUM 사용자 권한 필요"""
    if current_user["rank"] != "PREMIUM":
        raise AuthorizationException("PREMIUM 등급이 필요합니다.")
    return current_user

# API 엔드포인트
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    사용자 로그인 (초대 코드 + 닉네임)
    
    Args:
        request: 로그인 요청 (초대 코드, 닉네임)
    
    Returns:
        JWT 액세스 토큰과 사용자 정보
    """
    log_service_call("auth", "login", nickname=request.nickname)
    
    try:
        # 초대 코드 검증 (간단한 모의 구현)
        valid_invite_codes = ["WELCOME2025", "VIP2025", "PREMIUM2025", "TEST123"]
        if request.invite_code not in valid_invite_codes:
            raise AuthenticationException("유효하지 않은 초대 코드입니다.")
        
        # 사용자 등급 결정
        rank = "STANDARD"
        if request.invite_code == "VIP2025":
            rank = "VIP"
        elif request.invite_code == "PREMIUM2025":
            rank = "PREMIUM"
        
        # 모의 사용자 데이터 (실제로는 DB에서 조회/생성)
        user_data = {
            "id": hash(request.nickname) % 10000,  # 간단한 ID 생성
            "nickname": request.nickname,
            "rank": rank,
            "created_at": datetime.utcnow(),
            "tokens": 1000,  # 초기 토큰
            "gems": 100      # 초기 젬
        }
        
        # JWT 토큰 생성
        access_token = create_access_token(user_data)
        
        logger.info(f"User {request.nickname} logged in successfully with rank {rank}")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_HOURS * 3600,  # 초 단위
            user={
                "id": user_data["id"],
                "nickname": user_data["nickname"],
                "rank": user_data["rank"],
                "tokens": user_data["tokens"],
                "gems": user_data["gems"]
            }
        )
    
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {request.nickname}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다."
        )

@router.post("/validate", response_model=TokenValidationResponse)
async def validate_token(
    current_user: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    JWT 토큰 유효성 검증
    
    Returns:
        토큰 유효성 및 사용자 정보
    """
    log_service_call("auth", "validate_token", user_id=current_user.get("user_id"))
    
    return TokenValidationResponse(
        valid=True,
        user_id=current_user["user_id"],
        nickname=current_user["nickname"],
        rank=current_user["rank"],
        expires_at=datetime.fromtimestamp(current_user["exp"])
    )

@router.post("/refresh")
async def refresh_token(
    current_user: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    JWT 토큰 갱신
    
    Returns:
        새로운 JWT 토큰
    """
    log_service_call("auth", "refresh_token", user_id=current_user["user_id"])
    
    # 새로운 토큰 생성
    user_data = {
        "id": current_user["user_id"],
        "nickname": current_user["nickname"],
        "rank": current_user["rank"]
    }
    
    new_token = create_access_token(user_data)
    
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600
    }

@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회
    
    Returns:
        사용자 정보
    """
    log_service_call("auth", "get_current_user_info", user_id=current_user["id"])
    
    return {
        "success": True,
        "user": current_user
    }

@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    사용자 로그아웃 (토큰 무효화)
    
    Note: JWT는 stateless이므로 실제로는 클라이언트에서 토큰을 삭제해야 함
    """
    log_service_call("auth", "logout", user_id=current_user["id"])
    
    return {
        "success": True,
        "message": "로그아웃되었습니다.",
        "user_id": current_user["id"]
    }

@router.get("/test/standard")
async def test_standard_access(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    표준 사용자 접근 테스트 (모든 등급 접근 가능)
    """
    return {
        "success": True,
        "message": "표준 사용자 접근 성공",
        "user": current_user,
        "access_level": "STANDARD"
    }

@router.get("/test/vip")
async def test_vip_access(
    current_user: Dict[str, Any] = Depends(require_vip_user)
):
    """
    VIP 사용자 접근 테스트 (VIP, PREMIUM만 접근 가능)
    """
    return {
        "success": True,
        "message": "VIP 사용자 접근 성공",
        "user": current_user,
        "access_level": "VIP"
    }

@router.get("/test/premium")
async def test_premium_access(
    current_user: Dict[str, Any] = Depends(require_premium_user)
):
    """
    PREMIUM 사용자 접근 테스트 (PREMIUM만 접근 가능)
    """
    return {
        "success": True,
        "message": "PREMIUM 사용자 접근 성공",
        "user": current_user,
        "access_level": "PREMIUM"
    }

@router.get("/invite-codes")
async def get_valid_invite_codes():
    """
    유효한 초대 코드 목록 조회 (개발/테스트용)
    """
    return {
        "success": True,
        "invite_codes": [
            {"code": "WELCOME2025", "rank": "STANDARD", "description": "기본 사용자"},
            {"code": "VIP2025", "rank": "VIP", "description": "VIP 사용자"},
            {"code": "PREMIUM2025", "rank": "PREMIUM", "description": "프리미엄 사용자"},
            {"code": "TEST123", "rank": "STANDARD", "description": "테스트용"}
        ]
    }

# 헬스체크
@router.get("/health")
async def auth_health():
    """인증 시스템 헬스체크"""
    return {
        "status": "healthy",
        "service": "jwt_auth",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
