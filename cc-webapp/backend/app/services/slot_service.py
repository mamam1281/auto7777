from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
import random
import datetime

from .token_service import TokenService
from ..repositories.game_repository import GameRepository
from .. import models


@dataclass
class SlotSpinResult:
    result: str
    tokens_change: int
    balance: int
    streak: int
    animation: Optional[str]


class SlotService:
    """슬롯 머신 로직을 담당하는 서비스 계층."""

    def __init__(self, repository: GameRepository | None = None, token_service: TokenService | None = None, db: Optional[Session] = None) -> None:
        self.repo = repository or GameRepository()
        self.token_service = token_service or TokenService(db, self.repo)

    def _get_time_based_adjustment(self) -> float:
        """시간대별 승률 변동 조정값을 반환"""
        current_hour = datetime.datetime.now().hour
        
        # 오전 9시~12시, 오후 6시~10시에 승률 소폭 증가 (피크 타임)
        if 9 <= current_hour < 12 or 18 <= current_hour < 22:
            return 0.03
        # 오전 2시~6시에 승률 감소 (비활성 시간)
        elif 2 <= current_hour < 6:
            return -0.05
        # 그 외 시간에는 중립적
        else:
            return 0.0

    def spin(self, user_id: int, db: Session) -> SlotSpinResult:
        """슬롯 스핀을 실행하고 결과를 반환."""
        # DB 세션을 TokenService에 설정
        if not self.token_service.db:
            self.token_service.db = db
            
        # 토큰 차감. 부족하면 ValueError 발생
        deducted_tokens = self.token_service.deduct_tokens(user_id, 2)
        if deducted_tokens is None:
            raise ValueError("토큰이 부족합니다.")

        segment = self.repo.get_user_segment(db, user_id)
        streak = self.repo.get_streak(user_id)
        
        # 기본 확률 설정 (체크리스트 기반)
        # 소액 승리: 38%, 대박: 2%, 패배: 60%
        small_win_prob = 0.38
        jackpot_prob = 0.02
        
        # 유저 타입별 승률 차등 적용
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        # 신규 유저 확인 (가입 후 7일 이내)
        is_new_user = False
        if user:
            days_since_creation = (datetime.datetime.utcnow() - user.created_at).days
            if days_since_creation <= 7:
                is_new_user = True
                small_win_prob += 0.15  # 신규 유저 +15% 승률
        
        # VIP 유저 확인
        is_vip = False
        if user and user.rank == "VIP":
            is_vip = True
            small_win_prob += 0.06  # VIP 유저 +6% 승률
            
        # 시간대별 승률 변동 적용
        time_adjustment = self._get_time_based_adjustment()
        small_win_prob += time_adjustment
        
        # 연패 보상 시스템 (기존 유지)
        force_win = False
        if streak >= 7:
            force_win = True
            
        # 결과 계산
        spin = random.random()
        result = "lose"
        reward = 0
        animation = "lose"
        
        if force_win:
            # 연패 보상으로 강제 승리 (소액 승리)
            result = "win"
            reward = random.randint(2, 3)  # 110-120% 보상
            animation = "force_win"
            streak = 0
        elif spin < jackpot_prob:
            # 대박 (베팅액의 200-300%)
            result = "jackpot"
            reward = random.randint(4, 6)  # 200-300% 보상
            animation = "jackpot"
            streak = 0
        elif spin < jackpot_prob + small_win_prob:
            # 소액 승리 (베팅액의 110-120%)
            result = "win"
            reward = random.randint(2, 3)  # 110-120% 보상
            animation = "win"
            streak = 0
        else:
            # 패배
            result = "lose"
            reward = 0
            animation = "lose"
            streak += 1
            
            # 근접 실패 애니메이션 구현 (80% 확률로 발생)
            if random.random() < 0.80:
                animation = "near_miss"

        if reward:
            self.token_service.add_tokens(user_id, reward)

        self.repo.set_streak(user_id, streak)
        balance = self.token_service.get_token_balance(user_id)
        self.repo.record_action(db, user_id, "SLOT_SPIN", -2)
        
        # 슬롯 결과 기록
        game = models.Game(
            user_id=user_id,
            game_type="slot",
            bet_amount=2,
            result=result,
            payout=reward
        )
        db.add(game)
        db.commit()
        
        return SlotSpinResult(result, reward - 2, balance, streak, animation)
