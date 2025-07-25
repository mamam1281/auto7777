"""RPS (Rock-Paper-Scissors) 게임 서비스."""

from dataclasses import dataclass
from typing import Optional, Dict, List
import random
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .token_service import TokenService
from ..repositories.game_repository import GameRepository

logger = logging.getLogger(__name__)


@dataclass
class RPSResult:
    """RPS 게임 결과 데이터."""
    user_choice: str
    computer_choice: str
    result: str  # "win", "lose", "draw"
    tokens_change: int
    balance: int
    displayed_win_rate: float = 40.0  # 표시용 승률
    actual_win_rate: float = 30.0     # 실제 승률


class RPSService:
    """RPS (Rock-Paper-Scissors) 게임 로직을 담당하는 서비스."""
    
    VALID_CHOICES = ["rock", "paper", "scissors"]
    WINNING_COMBINATIONS = {
        "rock": "scissors",
        "paper": "rock", 
        "scissors": "paper"
    }
    
    # 실제 승률 설정 (수익성 최적화)
    ACTUAL_WIN_RATE = 0.30      # 실제 승률 30%
    DRAW_RATE = 0.10            # 무승부 확률 10%
    LOSE_RATE = 0.60            # 패배 확률 60%
    
    # 표시용 승률 (사용자 심리 고려)
    DISPLAYED_WIN_RATE = 40.0   # 표시 승률 40%

    def __init__(self, repository: Optional[GameRepository] = None, token_service: Optional[TokenService] = None, db: Optional[Session] = None) -> None:
        self.repo = repository or GameRepository()
        self.token_service = token_service or TokenService(db or None, self.repo)
        self._user_patterns: Dict[int, List[str]] = {}  # 유저 선택 패턴 추적
        
    def _get_winning_choice(self, user_choice: str) -> str:
        """사용자 선택을 이기는 AI 선택을 반환"""
        winning_map = {
            "rock": "paper",
            "paper": "scissors",
            "scissors": "rock"
        }
        return winning_map[user_choice]
    
    def _analyze_user_pattern(self, user_id: int, user_choice: str) -> str:
        """유저 선택 패턴 분석 및 AI 선택 알고리즘"""
        # 유저 패턴 기록 업데이트
        if user_id not in self._user_patterns:
            self._user_patterns[user_id] = []
        
        self._user_patterns[user_id].append(user_choice)
        
        # 최근 10게임만 유지
        if len(self._user_patterns[user_id]) > 10:
            self._user_patterns[user_id] = self._user_patterns[user_id][-10:]
        
        recent_choices = self._user_patterns[user_id]
        
        # 패턴이 3개 이상 있을 때 분석
        if len(recent_choices) >= 3:
            # 가장 자주 선택하는 것 분석
            choice_counts = {choice: recent_choices.count(choice) for choice in self.VALID_CHOICES}
            most_frequent = max(choice_counts, key=choice_counts.get)
            
            # 연속 패턴 분석
            if len(recent_choices) >= 2 and recent_choices[-1] == recent_choices[-2]:
                # 같은 선택 반복 시 해당 선택을 이기는 것 선택 (70% 확률)
                if random.random() < 0.7:
                    return self._get_winning_choice(user_choice)
            
            # 가장 자주 선택하는 것을 이기는 선택 (60% 확률)
            if random.random() < 0.6:
                return self._get_winning_choice(most_frequent)
        
        # 패턴이 없거나 랜덤 선택
        return random.choice(self.VALID_CHOICES)
    
    def _get_computer_choice(self, user_id: int, user_choice: str, streak: int, force_result: Optional[str] = None) -> tuple[str, str]:
        """AI 선택 및 결과 결정"""
        
        # 연승 제어 시스템: 3연승 후 90% 패배 확률
        if streak >= 3:
            if random.random() < 0.90:
                # 강제 패배
                computer_choice = self._get_winning_choice(user_choice)
                return computer_choice, "lose"
            else:
                # 10% 확률로 승리 허용
                computer_choice = self.WINNING_COMBINATIONS[user_choice]
                return computer_choice, "win"
        
        # 강제 결과가 지정된 경우
        if force_result:
            if force_result == "win":
                computer_choice = self.WINNING_COMBINATIONS[user_choice]
                return computer_choice, "win"
            elif force_result == "lose":
                computer_choice = self._get_winning_choice(user_choice)
                return computer_choice, "lose"
            elif force_result == "draw":
                return user_choice, "draw"
        
        # 일반적인 확률 기반 결정
        rand = random.random()
        
        if rand < self.ACTUAL_WIN_RATE:  # 30% 승률
            computer_choice = self.WINNING_COMBINATIONS[user_choice]
            result = "win"
        elif rand < self.ACTUAL_WIN_RATE + self.DRAW_RATE:  # 10% 무승부 (30% + 10% = 40%)
            computer_choice = user_choice
            result = "draw"
        else:  # 60% 패배 (40% 이후)
            computer_choice = self._get_winning_choice(user_choice)
            result = "lose"
        
        return computer_choice, result

    def play(self, user_id: int, user_choice: str, bet_amount: int, db: Session) -> RPSResult:
        """RPS 게임을 플레이하고 결과를 반환."""
        logger.info(f"RPS game started: user_id={user_id}, choice={user_choice}, bet_amount={bet_amount}")
        
        # 입력 검증
        if user_choice not in self.VALID_CHOICES:
            logger.warning(f"Invalid choice from user {user_id}: {user_choice}")
            raise ValueError("Invalid choice. Please select rock, paper, or scissors.")
        
        if bet_amount <= 0:
            logger.warning(f"Invalid bet amount from user {user_id}: {bet_amount}")
            raise ValueError("Bet amount must be greater than 0.")

        # 토큰 차감
        deducted_tokens = self.token_service.deduct_tokens(user_id, bet_amount)
        if deducted_tokens is None:
            logger.error(f"Insufficient tokens for user {user_id}")
            raise ValueError("Insufficient tokens")

        # 연승 상태 확인
        streak = self.repo.get_streak(user_id) or 0
        
        # 수익성 최적화된 AI 선택 알고리즘
        computer_choice, result = self._get_computer_choice(user_id, user_choice, streak)
        
        logger.info(f"Game result: user={user_choice}, computer={computer_choice}, result={result}, streak={streak}")
        
        # 연승 카운터 업데이트
        if result == "win":
            streak += 1
        else:
            streak = 0
        self.repo.set_streak(user_id, streak)
        
        # 토큰 변화량 계산 (심리적 보상 체계)
        tokens_change = 0
        if result == "win":
            # 승리 시 2배 보상 (베팅액 포함)
            reward = bet_amount * 2
            self.token_service.add_tokens(user_id, reward)
            tokens_change = reward - bet_amount  # 실제 순수익 = 베팅액
            logger.info(f"User {user_id} won: reward={reward}, net_change={tokens_change}")
        elif result == "draw":
            # 무승부 시 베팅 금액 환불
            self.token_service.add_tokens(user_id, bet_amount)
            tokens_change = 0
            logger.info(f"User {user_id} draw: bet refunded")
        else:  # lose
            # 패배 시 베팅 금액 손실
            tokens_change = -bet_amount
            logger.info(f"User {user_id} lost: lost={bet_amount}")

        # 현재 잔액 조회
        balance = self.token_service.get_token_balance(user_id)
        
        # 게임 기록
        self.repo.record_action(db, user_id, "RPS_PLAY", tokens_change)
        logger.debug(f"Game action recorded for user {user_id}")
        
        logger.info(f"RPS game completed: user_id={user_id}, result={result}, tokens_change={tokens_change}, balance={balance}")
        
        return RPSResult(
            user_choice=user_choice,
            computer_choice=computer_choice,
            result=result,
            tokens_change=tokens_change,
            balance=balance,
            displayed_win_rate=self.DISPLAYED_WIN_RATE,
            actual_win_rate=self.ACTUAL_WIN_RATE * 100
        )
    
    def get_user_stats(self, user_id: int) -> Dict[str, any]:
        """유저 통계 정보 반환 (표시용)"""
        streak = self.repo.get_streak(user_id) or 0
        pattern = self._user_patterns.get(user_id, [])
        
        return {
            "current_streak": streak,
            "displayed_win_rate": self.DISPLAYED_WIN_RATE,
            "recent_choices": pattern[-5:] if pattern else [],
            "pattern_analysis": len(pattern) >= 3
        }
