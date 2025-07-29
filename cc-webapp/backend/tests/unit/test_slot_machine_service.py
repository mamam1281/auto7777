"""
슬롯머신 서비스 단위 테스트
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.game.slot_machine_service import SlotMachineService
from app.schemas.game import SlotSpinRequest, SlotSpinResult, Symbol
from app.core.exceptions import InsufficientFundsError, InvalidGameStateError


@pytest.fixture
def slot_service():
    # 레포지토리 모의객체 생성
    mock_user_repo = MagicMock()
    mock_action_repo = MagicMock()
    mock_reward_repo = MagicMock()
    mock_streak_repo = MagicMock()
    
    # 서비스 인스턴스 생성 및 반환
    return SlotMachineService(
        user_repo=mock_user_repo,
        action_repo=mock_action_repo,
        reward_repo=mock_reward_repo,
        streak_repo=mock_streak_repo,
        redis_client=MagicMock()
    )


class TestSlotMachineService:
    
    def test_spin_insufficient_funds(self, slot_service):
        """잔액 부족 시 스핀 실패 테스트"""
        # 유저 목 설정
        mock_user = MagicMock()
        mock_user.regular_coins = 50
        
        # 스핀 요청 생성 (베팅 금액이 잔액보다 높음)
        spin_request = SlotSpinRequest(bet_amount=100)
        
        # 예외 발생 확인
        with pytest.raises(InsufficientFundsError):
            slot_service.spin(user=mock_user, spin_request=spin_request)
    
    @patch('app.services.game.slot_machine_service.SlotMachineService._generate_spin_result')
    @patch('app.services.game.slot_machine_service.SlotMachineService._get_user_streak_info')
    def test_spin_successful(self, mock_get_streak, mock_generate_result, slot_service):
        """성공적인 스핀 테스트"""
        # 스트릭 정보 목 설정
        mock_get_streak.return_value = (0, False)  # 스트릭 카운트, 스트릭 만료 여부
        
        # 생성할 결과 목 설정
        mock_result = SlotSpinResult(
            symbols=[Symbol.CHERRY, Symbol.CHERRY, Symbol.CHERRY],
            win_amount=300,
            multiplier=3,
            is_jackpot=False
        )
        mock_generate_result.return_value = mock_result
        
        # 유저 목 설정
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.regular_coins = 500
        mock_user.rank = "STANDARD"
        
        # 스핀 요청 생성
        spin_request = SlotSpinRequest(bet_amount=100)
        
        # 스핀 실행
        result = slot_service.spin(user=mock_user, spin_request=spin_request)
        
        # 검증
        assert result == mock_result
        # 유저 코인 차감 확인
        assert mock_user.regular_coins == 700  # 시작 500 - 베팅 100 + 당첨 300
        # 액션 로그 저장 확인
        slot_service._action_repo.create_action.assert_called_once()
        # 리워드 저장 확인
        slot_service._reward_repo.create_reward.assert_called_once()
        # Redis 업데이트 확인
        slot_service._redis_client.setex.assert_called()
    
    @patch('app.services.game.slot_machine_service.random.choices')
    def test_generate_spin_result(self, mock_choices, slot_service):
        """스핀 결과 생성 테스트"""
        # random.choices 목킹
        mock_choices.return_value = [Symbol.SEVEN, Symbol.SEVEN, Symbol.SEVEN]
        
        # 스핀 결과 생성
        bet_amount = 100
        streak_count = 2
        user_rank = "PREMIUM"
        
        result = slot_service._generate_spin_result(
            bet_amount=bet_amount,
            streak_count=streak_count,
            user_rank=user_rank
        )
        
        # 검증
        assert result.symbols == [Symbol.SEVEN, Symbol.SEVEN, Symbol.SEVEN]
        assert result.is_jackpot is True  # 7-7-7은 잭팟
        assert result.multiplier > 1  # 스트릭이 있으므로 멀티플라이어 증가
        assert result.win_amount > bet_amount  # 당첨 금액이 베팅보다 커야 함
    
    @patch('app.services.game.slot_machine_service.time.time')
    def test_get_user_streak_info_active_streak(self, mock_time, slot_service):
        """활성화된 스트릭 정보 가져오기 테스트"""
        # 현재 시간 목킹
        current_time = 1600000000
        mock_time.return_value = current_time
        
        # Redis 클라이언트 목킹
        mock_redis = slot_service._redis_client
        # 스트릭 카운트와 마지막 액션 시간 설정
        mock_redis.get.side_effect = [
            "3",  # 스트릭 카운트
            str(current_time - 300)  # 마지막 액션 시간 (5분 전)
        ]
        
        # 스트릭 정보 가져오기
        user_id = 1
        streak_count, streak_expired = slot_service._get_user_streak_info(user_id)
        
        # 검증
        assert streak_count == 3
        assert streak_expired is False  # 스트릭 만료 안됨 (10분 내에 플레이)
    
    @patch('app.services.game.slot_machine_service.time.time')
    def test_get_user_streak_info_expired_streak(self, mock_time, slot_service):
        """만료된 스트릭 정보 가져오기 테스트"""
        # 현재 시간 목킹
        current_time = 1600000000
        mock_time.return_value = current_time
        
        # Redis 클라이언트 목킹
        mock_redis = slot_service._redis_client
        # 스트릭 카운트와 마지막 액션 시간 설정
        mock_redis.get.side_effect = [
            "5",  # 스트릭 카운트
            str(current_time - 700)  # 마지막 액션 시간 (11분 이상 전)
        ]
        
        # 스트릭 정보 가져오기
        user_id = 1
        streak_count, streak_expired = slot_service._get_user_streak_info(user_id)
        
        # 검증
        assert streak_count == 0  # 스트릭 리셋
        assert streak_expired is True  # 스트릭 만료됨
