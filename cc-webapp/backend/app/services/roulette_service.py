"""경품추첨 룰렛 서비스"""
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from ..repositories.game_repository import GameRepository
from ..utils.segment_utils import get_user_segment


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
    is_near_miss: bool = False
    animation_type: str = 'normal'


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

    def get_user_type_bonus(self, user_id: int, db: Session) -> float:
        """유저 타입별 승률 보너스 계산"""
        try:
            user_segment = get_user_segment(user_id, db)
            
            # 유저 타입별 승률 보너스
            if user_segment == "NEW":
                return 0.15  # 신규 유저 +15%
            elif user_segment in ["VIP", "WHALE"]:
                return 0.06  # VIP 유저 +6%
            elif user_segment == "RETURNING":
                return 0.08  # 복귀 유저 +8%
            else:
                return 0.0   # 일반 유저 보너스 없음
        except Exception:
            return 0.0  # 오류 시 기본값

    def get_time_based_modifier(self) -> float:
        """시간대별 승률 조정"""
        current_hour = datetime.now().hour
        
        # 피크 시간대 (19-23시): -5% 승률 페널티
        if 19 <= current_hour <= 23:
            return -0.05
        # 새벽 시간대 (01-06시): +3% 승률 보너스
        elif 1 <= current_hour <= 6:
            return 0.03
        # 점심 시간대 (12-14시): +2% 승률 보너스
        elif 12 <= current_hour <= 14:
            return 0.02
        else:
            return 0.0  # 기본 시간대

    def calculate_near_miss_probability(self, user_id: int) -> bool:
        """근접 실패 발생 여부 계산"""
        # 40% 확률로 근접 실패 연출
        return random.random() < 0.4

    def adjust_probabilities_for_user(self, user_id: int, db: Session) -> List[Prize]:
        """유저별 조정된 확률 테이블 생성"""
        base_prizes = self.PRIZES.copy()
        
        # 유저 타입별 보너스
        user_bonus = self.get_user_type_bonus(user_id, db)
        
        # 시간대별 조정
        time_modifier = self.get_time_based_modifier()
        
        # 총 보너스 계산
        total_bonus = user_bonus + time_modifier
        
        # 확률 조정 (고가치 상품 확률 증가)
        adjusted_prizes = []
        for prize in base_prizes:
            adjusted_prize = Prize(
                id=prize.id,
                name=prize.name,
                value=prize.value,
                color=prize.color,
                probability=prize.probability
            )
            
            # 보너스가 양수면 고가치 상품 확률 증가
            if total_bonus > 0:
                if prize.value >= 500:  # 고가치 상품
                    adjusted_prize.probability *= (1 + total_bonus)
                else:  # 저가치 상품 확률 감소
                    adjusted_prize.probability *= (1 - total_bonus * 0.5)
            # 보너스가 음수면 고가치 상품 확률 감소
            elif total_bonus < 0:
                if prize.value >= 500:  # 고가치 상품
                    adjusted_prize.probability *= (1 + total_bonus)
                else:  # 저가치 상품 확률 증가
                    adjusted_prize.probability *= (1 - total_bonus * 0.5)
            
            adjusted_prizes.append(adjusted_prize)
        
        # 확률 정규화 (총합이 1이 되도록)
        total_probability = sum(p.probability for p in adjusted_prizes)
        for prize in adjusted_prizes:
            prize.probability /= total_probability
        
        return adjusted_prizes

    def spin_prize_roulette(self, user_id: int, db: Session = None) -> PrizeRouletteSpinResult:
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
                cooldown_expires=tomorrow,
                is_near_miss=False,
                animation_type='normal'
            )
        
        # 근접 실패 여부 결정
        is_near_miss = self.calculate_near_miss_probability(user_id)
        
        # 유저별 조정된 확률로 경품 추첨
        if db:
            adjusted_prizes = self.adjust_probabilities_for_user(user_id, db)
            prize = self._select_random_prize_from_list(adjusted_prizes)
        else:
            prize = self._select_random_prize()
        
        # 근접 실패 처리
        if is_near_miss and prize.value >= 500:  # 고가치 상품 당첨 시 근접 실패로 변경
            # 저가치 상품으로 변경 (하지만 사용자에게는 아쉬운 느낌을 줌)
            near_miss_prizes = [p for p in self.PRIZES if p.value < 500]
            prize = random.choice(near_miss_prizes)
        
        # 애니메이션 타입 결정
        animation_type = 'normal'
        if prize.id == 'jackpot':
            animation_type = 'jackpot'
        elif is_near_miss:
            animation_type = 'near_miss'
        
        # 스핀 횟수 차감
        self._record_spin(user_id)
        
        # 경품 지급 (실제론 사용자 인벤토리에 추가)
        self._award_prize(user_id, prize)
        
        # 결과 메시지 생성
        message = f"축하합니다! {prize.name}을(를) 획득했습니다!"
        if is_near_miss and prize.value < 500:
            message = f"아쉽네요! {prize.name}을(를) 획득했습니다. 다음에는 더 좋은 상품을!"
        
        return PrizeRouletteSpinResult(
            success=True,
            prize=prize,
            message=message,
            spins_left=spins_left - 1,
            cooldown_expires=None,
            is_near_miss=is_near_miss,
            animation_type=animation_type
        )

    def _select_random_prize(self) -> Prize:
        """확률에 따른 경품 선택 (기본 확률)"""
        weights = [prize.probability for prize in self.PRIZES]
        selected_prize = random.choices(self.PRIZES, weights=weights, k=1)[0]
        return selected_prize

    def _select_random_prize_from_list(self, prizes: List[Prize]) -> Prize:
        """확률에 따른 경품 선택 (사용자 정의 확률)"""
        weights = [prize.probability for prize in prizes]
        selected_prize = random.choices(prizes, weights=weights, k=1)[0]
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
