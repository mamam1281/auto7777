"""
간소화된 JWT 인증 서비스
- 중복 제거
- 핵심 기능만 포함
- 로그인/인증/회원가입 기본 틀
"""

import hashlib
import secrets
import uuid
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_

logger = logging.getLogger(__name__)

# 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "casino-club-secret-key-2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """간소화된 인증 서비스"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: int, session_id: str = None) -> str:
        """액세스 토큰 생성"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(user_id),
            "session_id": session_id or str(uuid.uuid4()),
            "jti": str(uuid.uuid4()),  # JWT ID 추가 (블랙리스트용)
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "access"
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token() -> str:
        """리프레시 토큰 생성"""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
        """액세스 토큰 검증 (블랙리스트 확인 포함)"""
        try:
            # 먼저 블랙리스트 확인
            if AuthService.is_token_blacklisted(token):
                logger.warning("Access denied: token is blacklisted")
                return None
            
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            if payload.get("type") != "access":
                return None
                
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return None
    
    @staticmethod
    def check_login_attempts(site_id: str, ip_address: str, db: Session) -> Tuple[bool, int]:
        """
        로그인 시도 횟수 확인
        
        Returns:
            (is_allowed, remaining_attempts)
        """
        try:
            from ..models.auth_clean import LoginAttempt
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            
            failed_attempts = db.query(LoginAttempt).filter(
                and_(
                    LoginAttempt.site_id == site_id,
                    LoginAttempt.ip_address == ip_address,
                    LoginAttempt.success == False,
                    LoginAttempt.attempted_at > cutoff_time
                )
            ).count()
            
            is_allowed = failed_attempts < MAX_LOGIN_ATTEMPTS
            remaining_attempts = max(0, MAX_LOGIN_ATTEMPTS - failed_attempts)
            
            return is_allowed, remaining_attempts
            
        except Exception as e:
            logger.error(f"Failed to check login attempts: {str(e)}")
            return True, MAX_LOGIN_ATTEMPTS
    
    @staticmethod
    def record_login_attempt(
        site_id: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        user_id: Optional[int] = None,
        failure_reason: Optional[str] = None,
        db: Session = None
    ):
        """로그인 시도 기록"""
        try:
            from ..models.auth_clean import LoginAttempt
            
            attempt = LoginAttempt(
                site_id=site_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
                attempted_at=datetime.utcnow()
            )
            
            db.add(attempt)
            db.commit()
            
            if not success:
                logger.warning(f"Failed login attempt for {site_id} from {ip_address}: {failure_reason}")
            else:
                logger.info(f"Successful login for {site_id} from {ip_address}")
                
        except Exception as e:
            logger.error(f"Failed to record login attempt: {str(e)}")
    
    @staticmethod
    def create_user_session(
        user_id: int,
        ip_address: str,
        user_agent: str,
        db: Session
    ) -> str:
        """사용자 세션 생성"""
        try:
            from ..models.auth_clean import UserSession
            
            session_id = str(uuid.uuid4())
            device_fingerprint = hashlib.sha256(
                f"{user_agent}:{ip_address}:{secrets.token_hex(8)}".encode()
            ).hexdigest()
            
            expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
            
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.add(session)
            db.commit()
            
            logger.info(f"Session created for user {user_id}: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            return str(uuid.uuid4())  # fallback
    
    @staticmethod
    def save_refresh_token(
        user_id: int,
        refresh_token: str,
        ip_address: str,
        user_agent: str,
        db: Session
    ):
        """리프레시 토큰 저장"""
        try:
            from ..models.auth_clean import RefreshToken
            
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            device_fingerprint = hashlib.sha256(
                f"{user_agent}:{ip_address}".encode()
            ).hexdigest()
            
            expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
            refresh_token_record = RefreshToken(
                user_id=user_id,
                token_hash=token_hash,
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.add(refresh_token_record)
            db.commit()
            
            logger.info(f"Refresh token saved for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to save refresh token: {str(e)}")
    
    @staticmethod
    def logout_user_session(
        user_id: int,
        session_id: Optional[str] = None,
        reason: str = "user_logout",
        db: Session = None
    ):
        """사용자 세션 로그아웃"""
        try:
            from ..models.auth_clean import UserSession
            
            query = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
            
            if session_id:
                query = query.filter(UserSession.session_id == session_id)
            
            sessions = query.all()
            
            for session in sessions:
                session.is_active = False
                session.logout_at = datetime.utcnow()
                session.logout_reason = reason
            
            db.commit()
            
            count = len(sessions)
            logger.info(f"Logged out {count} sessions for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to logout sessions: {str(e)}")
    
    @staticmethod
    def blacklist_token(token: str, reason: str = "logout") -> bool:
        """토큰을 블랙리스트에 추가"""
        try:
            # JWT 토큰에서 jti (JWT ID) 추출
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                jti = payload.get("jti")
                exp = payload.get("exp")
                
                if not jti:
                    logger.warning("Token has no JTI, cannot blacklist")
                    return False
                    
            except JWTError as e:
                logger.warning(f"Cannot decode token for blacklisting: {e}")
                return False
            
            # Redis에 블랙리스트 저장 (만료 시간까지)
            try:
                import redis
                redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
                
                # 토큰 만료까지 블랙리스트에 보관
                expire_time = datetime.fromtimestamp(exp) - datetime.utcnow()
                if expire_time.total_seconds() > 0:
                    redis_client.setex(
                        f"blacklist_token:{jti}",
                        int(expire_time.total_seconds()),
                        reason
                    )
                    logger.info(f"Token {jti} blacklisted for {reason}")
                    return True
                else:
                    logger.info(f"Token {jti} already expired, no need to blacklist")
                    return True
                    
            except Exception as redis_error:
                logger.warning(f"Redis not available, using memory fallback: {redis_error}")
                # Redis 없을 시 메모리 기반 fallback (재시작 시 초기화됨)
                if not hasattr(AuthService, '_memory_blacklist'):
                    AuthService._memory_blacklist = {}
                AuthService._memory_blacklist[jti] = {
                    'reason': reason,
                    'expires_at': exp
                }
                return True
                
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """토큰이 블랙리스트에 있는지 확인"""
        try:
            # JWT 토큰에서 jti 추출
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                jti = payload.get("jti")
                
                if not jti:
                    return False
                    
            except JWTError:
                return True  # 유효하지 않은 토큰은 차단
            
            # Redis에서 확인
            try:
                import redis
                redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
                
                blacklisted = redis_client.exists(f"blacklist_token:{jti}")
                if blacklisted:
                    logger.info(f"Token {jti} is blacklisted")
                    return True
                    
            except Exception as redis_error:
                logger.warning(f"Redis not available, checking memory fallback: {redis_error}")
                # 메모리 기반 fallback 확인
                if hasattr(AuthService, '_memory_blacklist'):
                    if jti in AuthService._memory_blacklist:
                        # 만료 시간 확인
                        exp = AuthService._memory_blacklist[jti]['expires_at']
                        if datetime.utcnow().timestamp() < exp:
                            return True
                        else:
                            # 만료된 토큰은 블랙리스트에서 제거
                            del AuthService._memory_blacklist[jti]
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False  # 오류 시 허용 (보안보다 가용성 우선)
    
    @staticmethod
    def logout_all_user_sessions(
        user_id: int,
        reason: str = "user_logout_all",
        db: Session = None
    ):
        """사용자의 모든 세션 로그아웃"""
        try:
            from ..models.auth_clean import UserSession
            
            sessions = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).all()
            
            for session in sessions:
                session.is_active = False
                session.logout_at = datetime.utcnow()
                session.logout_reason = reason
            
            db.commit()
            
            count = len(sessions)
            logger.info(f"Logged out all {count} sessions for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to logout all sessions: {str(e)}")


# 전역 인스턴스
auth_service = AuthService()
