"""
JWT 토큰 생성 및 검증 핸들러
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import os

# JWT 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-casino-club-secret-key-12345")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24시간

class JWTHandler:
    @staticmethod
    def create_access_token(user_data: Dict[str, Any]) -> str:
        """JWT 액세스 토큰 생성"""
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
        
        payload = {
            "user_id": user_data["id"],
            "nickname": user_data["nickname"],
            "rank": user_data["rank"],
            "site_id": user_data["site_id"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """JWT 리프레시 토큰 생성 (7일 만료)"""
        expire = datetime.utcnow() + timedelta(days=7)
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """JWT 토큰 검증 및 페이로드 반환"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # 토큰 만료 확인
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="토큰이 만료되었습니다"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다"
            )
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db) -> str:
        """리프레시 토큰으로 새 액세스 토큰 발급"""
        payload = JWTHandler.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="리프레시 토큰이 아닙니다"
            )
        
        from app.models import User
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다"
            )
        
        user_data = {
            "id": user.id,
            "nickname": user.nickname,
            "rank": user.rank.value,
            "site_id": user.site_id
        }
        
        return JWTHandler.create_access_token(user_data)
