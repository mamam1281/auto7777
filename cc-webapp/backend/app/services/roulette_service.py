"""경품추첨 룰렛 서비스"""
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from ..repositories.game_repository import GameRepository


@dataclass
class Prize:
    """경품 정보"""
    id: str
    name: str
    value: int
    color: str
    probability: float


@dataclass
class PrizeRouletteSpinResult:
    """경품 룰렛 스핀 결과"""
    success: bool
    prize: Optional[Prize]
    message: str
    spins_left: int
    cooldown_expires: Optional[datetime]


class RouletteService:
    """룰렛 서비스"""
    
    # 경품 목록 (하우스 엣지 15% 적용하여 조정된 확률)
    # 총 기댓값을 스핀 비용 대비 85%로 설정하여 15% 하우스 엣지 확보
    PRIZES = [
        Prize("coins_100", "코인 100개", 100, "#FFD700", 0.35),    # 35% (증가)
        Prize("coins_500", "코인 500개", 500, "#FFA500", 0.20),    # 20% (감소)
        Prize("coins_1000", "코인 1000개", 1000, "#FF6B35", 0.15), # 15% (감소)
        Prize("gems_10", "젬 10개", 10, "#9D4EDD", 0.18),          # 18% (증가)
        Prize("gems_50", "젬 50개", 50, "#7209B7", 0.10),          # 10% (증가)
        Prize("jackpot", "잭팟! 젬 200개", 200, "#FF0080", 0.015),  # 1.5% (감소)
        Prize("bonus", "보너스 스핀", 1, "#00FF88", 0.005)          # 0.5% (감소)
    ]
    
    MAX_DAILY_SPINS = 3
    
    def __init__(self, repository: GameRepository):
        self.repo = repository
        self._daily_spins: Dict[int, Dict[str, Any]] = {}  # 임시 저장소 (실제론 DB 사용)

    def spin_prize_roulette(self, user_id: int) -> PrizeRouletteSpinResult:
        """경품 룰렛 스핀"""
        # 일일 스핀 횟수 확인
        spins_left = self.get_spins_left(user_id)
        
        if spins_left <= 0:
            # 쿨다운 시간 계산 (다음날 자정)
            now = datetime.now()
            tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            
            return PrizeRouletteSpinResult(
                success=False,
                prize=None,
                message="오늘의 스핀 횟수를 모두 사용했습니다. 내일 다시 도전하세요!",
                spins_left=0,
                cooldown_expires=tomorrow
            )
        
        # 경품 추첨
        prize = self._select_random_prize()
        
        # 스핀 횟수 차감
        self._record_spin(user_id)
        
        # 경품 지급 (실제론 사용자 인벤토리에 추가)
        self._award_prize(user_id, prize)
        
        return PrizeRouletteSpinResult(
            success=True,
            prize=prize,
            message=f"축하합니다! {prize.name}을(를) 획득했습니다!",
            spins_left=spins_left - 1,
            cooldown_expires=None
        )

    def _select_random_prize(self) -> Prize:
        """확률에 따른 경품 선택"""
        weights = [prize.probability for prize in self.PRIZES]
        selected_prize = random.choices(self.PRIZES, weights=weights, k=1)[0]
        return selected_prize

    def _record_spin(self, user_id: int):
        """스핀 기록"""
        today = datetime.now().date().isoformat()
        
        if user_id not in self._daily_spins:
            self._daily_spins[user_id] = {}
        
        if today not in self._daily_spins[user_id]:
            self._daily_spins[user_id][today] = 0
        
        self._daily_spins[user_id][today] += 1

    def _award_prize(self, user_id: int, prize: Prize):
        """경품 지급 (실제론 데이터베이스에 저장)"""
        # TODO: 실제 구현에서는 사용자 인벤토리에 경품을 추가
        print(f"User {user_id} awarded: {prize.name}")

    def get_spins_left(self, user_id: int) -> int:
        """남은 스핀 횟수 조회"""
        today = datetime.now().date().isoformat()
        
        if user_id not in self._daily_spins:
            return self.MAX_DAILY_SPINS
        
        if today not in self._daily_spins[user_id]:
            return self.MAX_DAILY_SPINS
        
        used_spins = self._daily_spins[user_id][today]
        return max(0, self.MAX_DAILY_SPINS - used_spins)

    def get_prizes(self) -> List[Dict[str, Any]]:
        """경품 목록 조회"""
        return [
            {
                "id": prize.id,
                "name": prize.name,
                "value": prize.value,
                "color": prize.color,
                "probability": prize.probability
            }
            for prize in self.PRIZES
        ]

    # 기존 룰렛 관련 메소드들 (호환성 유지)
    def spin(self, user_id: int, bet: int, bet_type: str, value: str, db: Session):
        """기존 룰렛 스핀 (deprecated)"""
        raise NotImplementedError("Old roulette system has been replaced with prize roulette")


# 기존 RouletteSpinResult 클래스 (호환성 유지)
@dataclass
class RouletteSpinResult:
    """기존 룰렛 스핀 결과 (deprecated)"""
    winning_number: int
    result: str
    tokens_change: int
    balance: int
    animation: str
