"""간단한 인증 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth_models import User

router = APIRouter()
security = HTTPBearer()


@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "service": "simple_auth"}


@router.get("/users/me")
async def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """현재 사용자 정보 조회"""
    # 임시로 기본 응답 반환
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "is_active": True
    }


@router.post("/login")
async def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """로그인"""
    # 임시로 기본 토큰 반환
    return {
        "access_token": "dummy_token",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": username,
            "email": f"{username}@example.com"
        }
    }


@router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """회원가입"""
    # 임시로 기본 응답 반환
    return {
        "message": "User registered successfully",
        "user": {
            "id": 1,
            "username": username,
            "email": email,
            "is_active": True
        }
    }
