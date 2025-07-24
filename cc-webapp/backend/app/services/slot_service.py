from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
import random

from .token_service import TokenService
from ..repositories.game_repository import GameRepository


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

        # 기본 승리 확률과 잭팟 확률 설정
        win_prob = 0.10 + min(streak * 0.01, 0.05)
        if segment == "Whale":
            win_prob += 0.02
        elif segment == "Low":
            win_prob -= 0.02
        jackpot_prob = 0.01

        spin = random.random()
        result = "lose"
        reward = 0
        animation = "lose"
        if streak >= 7:
            # 연패 보상으로 강제 승리
            result = "win"
            reward = 10
            animation = "force_win"
            streak = 0
        elif spin < jackpot_prob:
            result = "jackpot"
            reward = 100
            animation = "jackpot"
            streak = 0
        elif spin < jackpot_prob + win_prob:
            result = "win"
            reward = 10
            animation = "win"
            streak = 0
        else:
            streak += 1

        if reward:
            self.token_service.add_tokens(user_id, reward)

        self.repo.set_streak(user_id, streak)
        balance = self.token_service.get_token_balance(user_id)
        self.repo.record_action(db, user_id, "SLOT_SPIN", -2)
        return SlotSpinResult(result, reward - 2, balance, streak, animation)
