"""
단순 인증 시스템 테스트
- 고정 초대코드로 회원가입 테스트
- 초대코드 유효성 검사 테스트
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base, InviteCode, User

# 인메모리 SQLite DB 설정
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB 초기화 및 의존성 재정의
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # 테스트 DB 스키마 설정
    Base.metadata.create_all(bind=engine)
    
    # 고정 초대코드 추가
    db = TestingSessionLocal()
    for code in ["5882", "6969", "6974"]:
        invite = InviteCode(code=code, is_used=False)
        db.add(invite)
    db.commit()
    
    # 테스트 클라이언트 생성
    client = TestClient(app)
    yield client
    
    # 테스트 DB 정리
    Base.metadata.drop_all(bind=engine)

def test_register_with_invite_code(client):
    """초대코드로 회원가입 테스트"""
    response = client.post(
        "/api/auth/register",
        json={"invite_code": "5882", "nickname": "테스터1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "테스터1"
    assert data["rank"] == "STANDARD"
    assert data["cyber_token_balance"] == 200

def test_register_with_invalid_code(client):
    """잘못된 초대코드로 회원가입 테스트"""
    response = client.post(
        "/api/auth/register",
        json={"invite_code": "1111", "nickname": "테스터2"}
    )
    assert response.status_code == 400
    assert "잘못된 초대코드입니다" in response.json()["detail"]

def test_check_invite_code(client):
    """초대코드 유효성 검사 테스트"""
    # 유효한 코드
    response = client.get("/api/auth/check-invite/6969")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    
    # 유효하지 않은 코드
    response = client.get("/api/auth/check-invite/1111")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == False

def test_list_invite_codes(client):
    """초대코드 목록 조회 테스트"""
    response = client.get("/api/auth/invite-codes")
    assert response.status_code == 200
    data = response.json()
    assert len(data["codes"]) == 3
    assert data["total"] == 3
    assert data["available_count"] == 3
    assert data["used_count"] == 0

def test_used_invite_code_check(client):
    """사용된 초대코드 확인 테스트"""
    # 회원가입으로 초대코드 사용
    client.post(
        "/api/auth/register",
        json={"invite_code": "5882", "nickname": "테스터3"}
    )
    
    # 사용된 초대코드 확인
    response = client.get("/api/auth/check-invite/5882")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == False
    assert "이미 사용된" in data["message"]
    
    # 사용된/미사용 초대코드 목록 필터링
    response = client.get("/api/auth/invite-codes?used=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["codes"]) == 1
    assert data["used_count"] == 1
    
    response = client.get("/api/auth/invite-codes?used=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data["codes"]) == 2
    assert data["available_count"] == 2
