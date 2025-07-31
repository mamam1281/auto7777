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
        """액세스 토큰 검증"""
        try:
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


# 전역 인스턴스
auth_service = AuthService()
