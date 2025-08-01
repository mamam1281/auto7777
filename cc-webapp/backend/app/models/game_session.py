"""
게임 세션 및 통계 관련 데이터베이스 모델
- 게임 세션 기록
- 사용자별 게임 통계
- 게임별 통계
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base

class GameSession(Base):
    """
    게임 세션 기록 모델
    - 사용자별 게임 플레이 히스토리 기록
    - 토큰 획득/소비 기록
    - 게임 결과 기록
    """
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, index=True)
    game_type = Column(String(50), index=True)  # "slot", "prize_roulette", "gacha", "rock_paper_scissors"
    result = Column(String(20), nullable=True)  # "win", "lose", "jackpot", "bonus" 등
    tokens_spent = Column(Integer, default=0)
    tokens_won = Column(Integer, default=0)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    metadata_json = Column(String, nullable=True)  # 추가 메타데이터 (JSON 형식)
    
    # 관계 설정
    # stats = relationship("GameStats", back_populates="sessions")

class GameStats(Base):
    """
    사용자별 게임 통계 모델
    - 전체 게임 통계 (승/패, 승률 등)
    - 게임별 통계
    - 토큰 수익/손실
    - 최장 연승 기록
    """
    __tablename__ = "game_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    
    # 전체 게임 통계
    total_games_played = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # 토큰 관련 통계
    total_tokens_spent = Column(Integer, default=0)
    total_tokens_won = Column(Integer, default=0)
    profit_loss = Column(Integer, default=0)
    
    # 연승 기록
    longest_win_streak = Column(Integer, default=0)
    current_win_streak = Column(Integer, default=0)
    
    # 게임별 통계
    slot_plays = Column(Integer, default=0)
    slot_wins = Column(Integer, default=0)
    roulette_spins = Column(Integer, default=0)
    roulette_wins = Column(Integer, default=0)
    gacha_pulls = Column(Integer, default=0)
    gacha_rare_items = Column(Integer, default=0)
    rps_plays = Column(Integer, default=0)
    rps_wins = Column(Integer, default=0)
    
    # 선호 게임 (가장 많이 플레이한 게임)
    favorite_game = Column(String(50), default="none")
    
    # 최근 플레이 정보
    last_played_at = Column(DateTime, nullable=True)
    last_game_type = Column(String(50), nullable=True)
    
    # 관계 설정
    # sessions = relationship("GameSession", back_populates="stats")
    
    # 통계 업데이트 메서드
    def update_after_game(self, game_type, result, tokens_spent, tokens_won):
        """게임 후 통계 업데이트"""
        # 전체 통계 업데이트
        self.total_games_played += 1
        self.total_tokens_spent += tokens_spent
        self.total_tokens_won += tokens_won
        self.profit_loss = self.total_tokens_won - self.total_tokens_spent
        
        # 승/패 업데이트
        is_win = result in ["win", "jackpot", "bonus"]
        if is_win:
            self.total_wins += 1
            self.current_win_streak += 1
            if self.current_win_streak > self.longest_win_streak:
                self.longest_win_streak = self.current_win_streak
        else:
            self.total_losses += 1
            self.current_win_streak = 0
            
        # 승률 계산
        if self.total_games_played > 0:
            self.win_rate = (self.total_wins / self.total_games_played) * 100
            
        # 게임별 통계 업데이트
        if game_type == "slot":
            self.slot_plays += 1
            if is_win:
                self.slot_wins += 1
        elif game_type == "prize_roulette":
            self.roulette_spins += 1
            if is_win:
                self.roulette_wins += 1
        elif game_type == "gacha":
            self.gacha_pulls += 1
            if result == "rare":
                self.gacha_rare_items += 1
        elif game_type == "rock_paper_scissors":
            self.rps_plays += 1
            if is_win:
                self.rps_wins += 1
                
        # 선호 게임 업데이트
        game_plays = {
            "slot": self.slot_plays,
            "prize_roulette": self.roulette_spins,
            "gacha": self.gacha_pulls,
            "rock_paper_scissors": self.rps_plays
        }
        self.favorite_game = max(game_plays, key=game_plays.get)
        
        # 최근 플레이 정보 업데이트
        self.last_played_at = func.now()
        self.last_game_type = game_type

class DailyGameLimit(Base):
    """
    일일 게임 제한 모델
    - 룰렛 일일 스핀 제한
    - 무료 게임 횟수 제한
    - 보너스 게임 쿨다운
    """
    __tablename__ = "daily_game_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    game_type = Column(String(50), index=True)
    date = Column(DateTime, index=True, default=func.date(func.now()))
    
    # 제한/사용량
    max_plays = Column(Integer, default=3)  # 기본값: 하루 3회
    plays_used = Column(Integer, default=0)
    
    # 쿨다운
    last_played_at = Column(DateTime, nullable=True)
    cooldown_expires_at = Column(DateTime, nullable=True)
    
    # 복합 유니크 제약 (사용자+게임+날짜)
    __table_args__ = (
        # UniqueConstraint('user_id', 'game_type', 'date', name='uix_user_game_date'),
    )
