"""
사용자 API 통합 테스트
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.auth.jwt_auth import create_tokens


@pytest.fixture
def client():
    """테스트 클라이언트 생성"""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """테스트용 사용자 생성 및 DB 저장"""
    user = User(
        nickname="testuser",
        email="test@example.com",
        hashed_password="$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12",
        rank="STANDARD",
        regular_coins=1000,
        premium_coins=100,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """인증 헤더 생성"""
    tokens = create_tokens(user_id=test_user.id, rank=test_user.rank)
    return {"Authorization": f"Bearer {tokens.access_token}"}


class TestUserRoutes:
    
    def test_get_current_user_profile(self, client, test_user, auth_headers):
        """현재 사용자 프로필 조회 테스트"""
        # 인증된 사용자 프로필 조회
        response = client.get("/api/users/me", headers=auth_headers)
        
        # 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["nickname"] == test_user.nickname
        assert data["email"] == test_user.email
        assert data["rank"] == test_user.rank
        assert data["regular_coins"] == test_user.regular_coins
        assert data["premium_coins"] == test_user.premium_coins
        assert "hashed_password" not in data
    
    def test_get_user_profile_unauthorized(self, client):
        """인증되지 않은 사용자의 프로필 조회 실패 테스트"""
        # 인증 토큰 없이 프로필 조회 시도
        response = client.get("/api/users/me")
        
        # 응답 검증
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_update_user_profile(self, client, test_user, auth_headers, db_session):
        """사용자 프로필 업데이트 테스트"""
        # 업데이트할 데이터 준비
        update_data = {
            "nickname": "updateduser",
            "email": "updated@example.com"
        }
        
        # 프로필 업데이트 요청
        response = client.patch("/api/users/me", json=update_data, headers=auth_headers)
        
        # 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == update_data["nickname"]
        assert data["email"] == update_data["email"]
        
        # DB에도 변경사항이 반영되었는지 확인
        db_session.refresh(test_user)
        assert test_user.nickname == update_data["nickname"]
        assert test_user.email == update_data["email"]
    
    def test_update_user_profile_invalid_data(self, client, auth_headers):
        """잘못된 데이터로 사용자 프로필 업데이트 실패 테스트"""
        # 유효하지 않은 이메일 형식
        invalid_data = {
            "email": "not-an-email"
        }
        
        # 프로필 업데이트 요청
        response = client.patch("/api/users/me", json=invalid_data, headers=auth_headers)
        
        # 응답 검증
        assert response.status_code == 422  # 검증 오류
        data = response.json()
        assert "detail" in data
    
    def test_get_user_balance(self, client, test_user, auth_headers):
        """사용자 잔액 조회 테스트"""
        # 잔액 조회 요청
        response = client.get("/api/users/me/balance", headers=auth_headers)
        
        # 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert data["regular_coins"] == test_user.regular_coins
        assert data["premium_coins"] == test_user.premium_coins
    
    def test_get_leaderboard(self, client, test_user, db_session):
        """리더보드 조회 테스트"""
        # 추가 사용자 생성
        users = [
            User(
                nickname=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password="$2b$12$abcdefg",
                rank="STANDARD",
                regular_coins=1000 + i * 500,
                premium_coins=100 + i * 50,
                is_active=True
            )
            for i in range(1, 5)
        ]
        
        # DB에 저장
        for user in users:
            db_session.add(user)
        db_session.commit()
        
        # 리더보드 조회 요청
        response = client.get("/api/users/leaderboard?limit=10")
        
        # 응답 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
        
        # 코인순으로 정렬되었는지 확인
        for i in range(1, len(data)):
            assert data[i-1]["regular_coins"] >= data[i]["regular_coins"]
