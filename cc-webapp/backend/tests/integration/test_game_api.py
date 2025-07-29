"""
게임 API 통합 테스트
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

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
        nickname="gameuser",
        email="game@example.com",
        hashed_password="$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12",
        rank="STANDARD",
        regular_coins=5000,
        premium_coins=500,
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


@pytest.fixture
def vip_user(db_session):
    """VIP 등급 테스트용 사용자 생성 및 DB 저장"""
    user = User(
        nickname="vipuser",
        email="vip@example.com",
        hashed_password="$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12",
        rank="VIP",
        regular_coins=10000,
        premium_coins=1000,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def vip_auth_headers(vip_user):
    """VIP 사용자 인증 헤더 생성"""
    tokens = create_tokens(user_id=vip_user.id, rank=vip_user.rank)
    return {"Authorization": f"Bearer {tokens.access_token}"}


class TestSlotMachineAPI:
    
    def test_spin_successful(self, client, auth_headers):
        """성공적인 슬롯 머신 스핀 테스트"""
        # 스핀 요청 데이터
        spin_data = {
            "bet_amount": 100
        }
        
        # 서비스 계층을 모킹하여 결과를 고정
        with patch('app.api.routes.game.get_slot_machine_service') as mock_get_service:
            # 모의 슬롯 서비스 설정
            mock_service = mock_get_service.return_value
            mock_service.spin.return_value = {
                "symbols": ["CHERRY", "CHERRY", "CHERRY"],
                "win_amount": 300,
                "multiplier": 3,
                "is_jackpot": False
            }
            
            # 스핀 요청
            response = client.post("/api/games/slots/spin", json=spin_data, headers=auth_headers)
            
            # 응답 검증
            assert response.status_code == 200
            data = response.json()
            assert data["symbols"] == ["CHERRY", "CHERRY", "CHERRY"]
            assert data["win_amount"] == 300
            assert data["multiplier"] == 3
            assert data["is_jackpot"] is False
    
    def test_spin_unauthorized(self, client):
        """인증되지 않은 사용자의 스핀 요청 실패 테스트"""
        # 스핀 요청 데이터
        spin_data = {
            "bet_amount": 100
        }
        
        # 인증 토큰 없이 스핀 요청
        response = client.post("/api/games/slots/spin", json=spin_data)
        
        # 응답 검증
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_spin_invalid_bet(self, client, auth_headers):
        """유효하지 않은 베팅액으로 스핀 요청 실패 테스트"""
        # 유효하지 않은 베팅액 (음수)
        invalid_data = {
            "bet_amount": -50
        }
        
        # 스핀 요청
        response = client.post("/api/games/slots/spin", json=invalid_data, headers=auth_headers)
        
        # 응답 검증
        assert response.status_code == 422  # 검증 오류
        data = response.json()
        assert "detail" in data
    
    def test_jackpot_info(self, client, auth_headers):
        """잭팟 정보 조회 테스트"""
        # 서비스 계층을 모킹하여 잭팟 정보를 고정
        with patch('app.api.routes.game.get_jackpot_service') as mock_get_service:
            # 모의 잭팟 서비스 설정
            mock_service = mock_get_service.return_value
            mock_service.get_current_jackpot_info.return_value = {
                "current_jackpot": 50000,
                "last_winner": "lucky_user",
                "last_won_amount": 45000,
                "last_won_time": "2023-09-01T15:30:00"
            }
            
            # 잭팟 정보 요청
            response = client.get("/api/games/jackpot/info", headers=auth_headers)
            
            # 응답 검증
            assert response.status_code == 200
            data = response.json()
            assert data["current_jackpot"] == 50000
            assert data["last_winner"] == "lucky_user"
            assert data["last_won_amount"] == 45000
            assert "last_won_time" in data


class TestCardGameAPI:
    
    def test_premium_game_access_with_vip(self, client, vip_auth_headers):
        """VIP 사용자의 프리미엄 게임 액세스 테스트"""
        # 서비스 계층 모킹
        with patch('app.api.routes.game.get_card_game_service') as mock_get_service:
            # 모의 카드 게임 서비스 설정
            mock_service = mock_get_service.return_value
            mock_service.start_premium_game.return_value = {
                "game_id": "premium-123",
                "status": "started",
                "premium_coins_required": 100
            }
            
            # 프리미엄 게임 시작 요청
            response = client.post("/api/games/cards/premium/start", headers=vip_auth_headers)
            
            # 응답 검증
            assert response.status_code == 200
            data = response.json()
            assert data["game_id"] == "premium-123"
            assert data["status"] == "started"
    
    def test_premium_game_access_with_standard(self, client, auth_headers):
        """일반 사용자의 프리미엄 게임 액세스 실패 테스트"""
        # 프리미엄 게임 시작 요청
        response = client.post("/api/games/cards/premium/start", headers=auth_headers)
        
        # 응답 검증 (접근 권한 부족)
        assert response.status_code == 403
        assert "접근 권한이 부족합니다" in response.json()["detail"]
