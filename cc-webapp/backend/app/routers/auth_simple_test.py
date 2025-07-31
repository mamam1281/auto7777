"""
최소한의 인증 라우터 - 테스트용
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/test")
async def test_auth():
    """테스트 엔드포인트"""
    return {"message": "Auth router is working!", "status": "success"}

@router.get("/health")
async def auth_health():
    """인증 헬스체크"""
    return {"status": "healthy", "service": "auth"}
