"""
초대코드 기반 인증 시스템 테스트
RFM 세그먼테이션 유지 + 인증 단순화
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base
from app.models import User, InviteCode, UserSegment
from app.auth.simple_auth import SimpleAuth

# 테스트용 인메모리 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """FastAPI 테스트 클라이언트"""
    Base.metadata.create_all(bind=engine)
    try:
        with TestClient(app) as c:
            yield c
    finally:
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_invite_code():
    """테스트용 초대코드 생성"""
    db = TestingSessionLocal()
    try:
        # 기존 초대코드 삭제
        db.query(InviteCode).delete()
        
        # 새 초대코드 생성
        invite_code = InviteCode(
            code="VIP123",
            is_used=False
        )
        db.add(invite_code)
        db.commit()
        return invite_code.code
    finally:
        db.close()

class TestAuthAPI:
    """초대코드 기반 인증 API 테스트"""
    
    def test_register_success(self, client, sample_invite_code):
        """정상 가입 테스트"""
        response = client.post(
            "/api/auth/register",
            json={
                "invite_code": sample_invite_code,
                "nickname": "테스트유저",
                "site_id": "testuser123",
                "phone_number": "010-1234-5678",
                "password": "testpass123"
            }
        )
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("nickname") == "테스트유저"
        assert data["rank"] == "STANDARD"
        assert data["cyber_token_balance"] == 200
