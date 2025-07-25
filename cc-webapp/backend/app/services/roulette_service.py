"""Roulette game service."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
import random
import logging
import datetime
import math

from .token_service import TokenService
from ..repositories.game_repository import GameRepository
from .. import models

logger = logging.getLogger(__name__)


@dataclass
class RouletteSpinResult:
    """룰렛 스핀 결과 데이터."""

    winning_number: int
    result: str
    tokens_change: int
    balance: int
    animation: Optional[str]
    near_miss: bool = False
    near_miss_number: Optional[int] = None
    danger_zone: Optional[bool] = None


class RouletteService:
    """룰렛 게임 로직을 담당하는 서비스."""
    
    # 색상 매핑
    RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
    
    # 위험 구역 정의 (색상 베팅에 사용)
    DANGER_ZONES = {
        "red": {2, 4, 6, 8, 10, 26, 28, 29, 31, 33, 35},  # 레드 베팅 시 위험한 블랙 숫자들
        "black": {1, 3, 5, 7, 9, 16, 18, 19, 21, 23, 25}   # 블랙 베팅 시 위험한 레드 숫자들
    }
    
    def __init__(self, repository: GameRepository | None = None, token_service: TokenService | None = None, db: Optional[Session] = None) -> None:
        self.repo = repository or GameRepository()
        self.token_service = token_service or TokenService(db, self.repo)
    
    def _get_time_based_adjustment(self) -> float:
        """시간대별 승률 변동 조정값을 반환"""
        current_hour = datetime.datetime.now().hour
        
        # 오전 9시~12시, 오후 6시~10시에 승률 소폭 증가 (피크 타임)
        if 9 <= current_hour < 12 or 18 <= current_hour < 22:
            return -0.02  # 하우스 엣지 감소 = 유저 승률 증가
        # 오전 2시~6시에 승률 감소 (비활성 시간)
        elif 2 <= current_hour < 6:
            return 0.03  # 하우스 엣지 증가 = 유저 승률 감소
        # 그 외 시간에는 중립적
        else:
            return 0.0
            
    def _generate_near_miss_number(self, bet_number: int) -> int:
        """근접 실패 연출을 위한 랜덤 번호 생성"""
        # 선택 번호와 약간 다른 숫자를 선택 (1~5 차이)
        offset = random.randint(1, 5)
        if random.random() < 0.5:
            offset = -offset
        near_miss = (bet_number + offset) % 37
        if near_miss < 0:
            near_miss += 37
        return near_miss

    def spin(
        self,
        user_id: int,
        bet: int,
        bet_type: str,
        value: Optional[str],
        db: Session,
    ) -> RouletteSpinResult:
        """룰렛 스핀을 실행하고 결과를 반환."""
        # DB 세션을 TokenService에 설정
        if not self.token_service.db:
            self.token_service.db = db
        """룰렛 스핀을 실행하고 결과를 반환한다.

        Parameters
        ----------
        user_id: int
            사용자 ID
        bet: int
            베팅 금액(1~50 사이로 제한)
        bet_type: str
            'number', 'color', 'odd_even' 중 하나
        value: Optional[str]
            베팅 값 (숫자 또는 색상 등)
        db: Session
            데이터베이스 세션

        Returns
        -------
        RouletteSpinResult
            스핀 결과 데이터

        Raises
        ------
        ValueError
            토큰이 부족한 경우
        """

        bet = max(1, min(bet, 50))
        logger.info("룰렛 스핀 시작 user=%s bet=%s type=%s value=%s", user_id, bet, bet_type, value)

        deducted_tokens = self.token_service.deduct_tokens(user_id, bet)
        if deducted_tokens is None:
            logger.warning("토큰 차감 실패: 토큰 부족")
            raise ValueError("토큰이 부족합니다.")

        # 유저 정보 확인
        user = db.query(models.User).filter(models.User.id == user_id).first()
        segment = self.repo.get_user_segment(db, user_id)
        
        # 하우스 엣지 15%로 상향 조정 (체크리스트 요구사항)
        # 세그먼트별 차등 적용 + 기본 15%
        edge_map = {"Whale": 0.10, "Medium": 0.15, "Low": 0.20}
        house_edge = edge_map.get(segment, 0.15)
        
        # 신규 유저 확인 및 하우스 엣지 조정
        is_new_user = False
        if user:
            days_since_creation = (datetime.datetime.utcnow() - user.created_at).days
            if days_since_creation <= 7:
                is_new_user = True
                house_edge -= 0.05  # 신규 유저 혜택 (5% 감소)
                
        # VIP 유저 확인 및 하우스 엣지 조정
        is_vip = False
        if user and user.rank == "VIP":
            is_vip = True
            house_edge -= 0.03  # VIP 유저 혜택 (3% 감소)
        
        # 시간대별 조정
        house_edge += self._get_time_based_adjustment()
        
        # 최소 5%, 최대 25% 범위로 제한
        house_edge = max(0.05, min(house_edge, 0.25))

        # 근접 실패 처리를 위한 변수들
        near_miss = False
        near_miss_number = None
        danger_zone = False
        
        # 기본 승패 결정
        number = random.randint(0, 36)
        payout = 0
        result = "lose"
        animation = "lose"

        # 스트릭 정보 (연패 시 승률 보정)
        streak = self.repo.get_streak(user_id)

        # 7연패 이상인 경우 강제 승리 처리
        force_win = False
        if streak >= 7:
            force_win = True
            house_edge *= 0.5  # 하우스 엣지 절반으로 감소

        # 숫자 베팅 처리
        if bet_type == "number" and value is not None:
            bet_number = int(value)
            
            # 강제 승리가 아니고 패배한 경우, 근접 실패 연출 추가 (70% 확률)
            if not force_win and (random.random() > (1 - house_edge)):
                if random.random() < 0.7:  # 근접 실패 확률 70%
                    near_miss = True
                    number = self._generate_near_miss_number(bet_number)
                    near_miss_number = number
                    animation = "near_miss"
            else:  # 승리 처리
                number = bet_number
                payout = int(bet * 35 * (1 - house_edge))
                if number == 0:
                    # 0번 적중은 잭팟으로 처리
                    payout = int(bet * 50 * (1 - house_edge))
                    animation = "jackpot"
                    
        # 색상 베팅 처리
        elif bet_type == "color" and value in {"red", "black"}:
            color_map = {"red": self.RED_NUMBERS, "black": self.BLACK_NUMBERS}
            
            # 위험구역 개념 추가
            danger_check = random.random() < 0.3  # 30% 확률로 위험구역 활성화
            
            if danger_check and value in self.DANGER_ZONES:
                danger_zone = True
                danger_numbers = self.DANGER_ZONES[value]
                number = random.choice(list(danger_numbers))
            elif force_win or random.random() > house_edge:
                # 승리 처리
                valid_numbers = list(color_map[value])
                number = random.choice(valid_numbers)
                payout = int(bet * 2 * (1 - house_edge))
            # 패배 시 기본 랜덤 번호 유지
                
        # 홀짝 베팅 처리
        elif bet_type == "odd_even" and value in {"odd", "even"}:
            # 강제 승리이거나 확률에 따라 승리 처리
            if force_win or random.random() > house_edge:
                # 이긴 경우
                number_pool = [n for n in range(1, 37) if (n % 2 == 0) == (value == "even")]
                number = random.choice(number_pool)
                payout = int(bet * 2 * (1 - house_edge))
            else:
                # 근접 실패 연출 (홀수 -> 짝수 또는 그 반대로)
                if random.random() < 0.7:  # 70% 확률로 근접 실패
                    near_miss = True
                    nearby_numbers = []
                    for n in range(1, 37):
                        if (n % 2 == 0) != (value == "even"):
                            nearby_numbers.append(n)
                    number = random.choice(nearby_numbers)
                    near_miss_number = number
                    animation = "near_miss"

        if payout:
            result = "win" if animation != "jackpot" else "jackpot"
            animation = animation if animation != "lose" else "win"
            self.token_service.add_tokens(user_id, payout)
            streak = 0
        else:
            streak += 1
            
            # 근접 실패 애니메이션이 설정되지 않은 경우에만 기본 애니메이션 설정
            if animation != "near_miss":
                animation = "lose"

        balance = self.token_service.get_token_balance(user_id)
        self.repo.set_streak(user_id, streak)
        self.repo.record_action(db, user_id, "ROULETTE_SPIN", -bet)
        
        # 게임 결과 기록
        game = models.Game(
            user_id=user_id,
            game_type="roulette",
            bet_amount=bet,
            result=result,
            payout=payout
        )
        db.add(game)
        db.commit()

        logger.info(
            "스핀 결과 user=%s number=%s result=%s payout=%s streak=%s near_miss=%s danger_zone=%s", 
            user_id, number, result, payout, streak, near_miss, danger_zone
        )

        return RouletteSpinResult(
            number, 
            result, 
            payout - bet, 
            balance, 
            animation, 
            near_miss=near_miss, 
            near_miss_number=near_miss_number,
            danger_zone=danger_zone
        )
