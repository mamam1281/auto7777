"""
고급 JWT 인증 핸들러
- 액세스/리프레시 토큰 관리
- 세션 관리
- 토큰 블랙리스트
- 동시 세션 제한
"""
import os
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user_session import UserSession, BlacklistedToken
from ..models.user import User


class AdvancedJWTHandler:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "changeme_secret_key")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "60"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "30"))
        self.max_sessions_per_user = int(os.getenv("MAX_SESSIONS_PER_USER", "5"))
    
    def generate_jti(self) -> str:
        """JWT ID 생성"""
        return str(uuid.uuid4())
    
    def create_access_token(self, user_id: int, jti: Optional[str] = None) -> Tuple[str, str]:
        """액세스 토큰 생성"""
        if jti is None:
            jti = self.generate_jti()
        
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "jti": jti,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti
    
    def create_refresh_token(self, user_id: int) -> Tuple[str, str]:
        """리프레시 토큰 생성"""
        jti = self.generate_jti()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": str(user_id),
            "jti": jti,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 토큰 타입 확인
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def is_token_blacklisted(self, jti: str, db: Session) -> bool:
        """토큰이 블랙리스트에 있는지 확인"""
        blacklisted = db.query(BlacklistedToken).filter(
            BlacklistedToken.jti == jti,
            BlacklistedToken.expires_at > datetime.utcnow()
        ).first()
        return blacklisted is not None
    
    def blacklist_token(self, jti: str, token_type: str, user_id: int, reason: str, db: Session):
        """토큰을 블랙리스트에 추가"""
        # 토큰 만료 시간 계산
        if token_type == "access":
            expires_at = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        else:
            expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        blacklisted_token = BlacklistedToken(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason
        )
        db.add(blacklisted_token)
        db.commit()
    
    def create_session(self, user_id: int, device_info: Optional[str], ip_address: Optional[str], db: Session) -> UserSession:
        """새 세션 생성"""
        # 기존 활성 세션 수 확인
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).count()
        
        # 최대 세션 수 초과 시 가장 오래된 세션 비활성화
        if active_sessions >= self.max_sessions_per_user:
            oldest_session = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).order_by(UserSession.last_used_at).first()
            
            if oldest_session:
                oldest_session.is_active = False
                db.commit()
        
        # 리프레시 토큰 생성
        refresh_token, refresh_jti = self.create_refresh_token(user_id)
        
        # 새 세션 생성
        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def refresh_access_token(self, refresh_token: str, db: Session) -> Tuple[str, str]:
        """리프레시 토큰으로 새 액세스 토큰 발급"""
        # 리프레시 토큰 검증
        payload = self.verify_token(refresh_token, "refresh")
        jti = payload.get("jti")
        user_id = int(payload.get("sub"))
        
        # 토큰이 블랙리스트에 있는지 확인
        if self.is_token_blacklisted(jti, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # 세션 확인
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )
        
        # 새 액세스 토큰 생성
        access_token, access_jti = self.create_access_token(user_id)
        
        # 세션 업데이트
        session.access_token_jti = access_jti
        session.last_used_at = datetime.utcnow()
        db.commit()
        
        return access_token, access_jti
    
    def logout_session(self, refresh_token: str, db: Session):
        """세션 로그아웃"""
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        ).first()
        
        if session:
            # 세션 비활성화
            session.is_active = False
            
            # 토큰들을 블랙리스트에 추가
            refresh_payload = self.verify_token(refresh_token, "refresh")
            self.blacklist_token(
                refresh_payload.get("jti"), "refresh", 
                session.user_id, "logout", db
            )
            
            if session.access_token_jti:
                self.blacklist_token(
                    session.access_token_jti, "access",
                    session.user_id, "logout", db
                )
            
            db.commit()
    
    def logout_all_sessions(self, user_id: int, reason: str, db: Session):
        """사용자의 모든 세션 강제 로그아웃"""
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        for session in sessions:
            # 세션 비활성화
            session.is_active = False
            
            # 리프레시 토큰 블랙리스트
            try:
                refresh_payload = self.verify_token(session.refresh_token, "refresh")
                self.blacklist_token(
                    refresh_payload.get("jti"), "refresh",
                    user_id, reason, db
                )
            except:
                pass  # 이미 만료된 토큰일 수 있음
            
            # 액세스 토큰 블랙리스트
            if session.access_token_jti:
                self.blacklist_token(
                    session.access_token_jti, "access",
                    user_id, reason, db
                )
        
        db.commit()
    
    def cleanup_expired_tokens(self, db: Session):
        """만료된 토큰 정리"""
        now = datetime.utcnow()
        
        # 만료된 블랙리스트 토큰 삭제
        db.query(BlacklistedToken).filter(
            BlacklistedToken.expires_at <= now
        ).delete()
        
        # 만료된 세션 비활성화
        expired_sessions = db.query(UserSession).filter(
            UserSession.expires_at <= now,
            UserSession.is_active == True
        ).all()
        
        for session in expired_sessions:
            session.is_active = False
        
        db.commit()


# 전역 인스턴스
jwt_handler = AdvancedJWTHandler()


# 기존 호환성을 위한 래퍼 클래스
class JWTHandler:
    @staticmethod
    def create_access_token(user_data: Dict[str, Any]) -> str:
        """기존 호환성을 위한 액세스 토큰 생성"""
        token, _ = jwt_handler.create_access_token(user_data["id"])
        return token
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """기존 호환성을 위한 리프레시 토큰 생성"""
        token, _ = jwt_handler.create_refresh_token(user_id)
        return token
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """기존 호환성을 위한 토큰 검증"""
        return jwt_handler.verify_token(token, "access")
