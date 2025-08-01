"""
게임 세션 및 통계 리포지토리
- 게임 세션 CRUD
- 게임 통계 조회 및 업데이트
- 일일 게임 제한 관리
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import uuid

from ..models.game_session import GameSession, GameStats, DailyGameLimit

class GameSessionRepository:
    """게임 세션 및 통계 관리 리포지토리"""
    
    @staticmethod
    def create_game_session(db: Session, user_id: int, game_type: str, tokens_spent: int = 0):
        """새 게임 세션 생성"""
        session = GameSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            game_type=game_type,
            tokens_spent=tokens_spent,
            started_at=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def update_game_session(db: Session, session_id: str, result: str, tokens_won: int = 0):
        """게임 세션 업데이트 (결과 및 종료)"""
        session = db.query(GameSession).filter(GameSession.session_id == session_id).first()
        if session:
            session.result = result
            session.tokens_won = tokens_won
            session.ended_at = datetime.utcnow()
            
            # 세션 지속 시간 계산 (초 단위)
            if session.started_at:
                delta = session.ended_at - session.started_at
                session.duration_seconds = delta.total_seconds()
                
            db.commit()
            db.refresh(session)
            
            # 사용자 통계 업데이트
            GameSessionRepository.update_user_stats(
                db, session.user_id, session.game_type, 
                session.result, session.tokens_spent, session.tokens_won
            )
            
            return session
        return None
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: int, limit: int = 50):
        """사용자의 최근 게임 세션 조회"""
        return db.query(GameSession).filter(
            GameSession.user_id == user_id
        ).order_by(GameSession.started_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_or_create_user_stats(db: Session, user_id: int):
        """사용자 게임 통계 조회 (없으면 생성)"""
        stats = db.query(GameStats).filter(GameStats.user_id == user_id).first()
        if not stats:
            stats = GameStats(user_id=user_id)
            db.add(stats)
            db.commit()
            db.refresh(stats)
        return stats
    
    @staticmethod
    def update_user_stats(db: Session, user_id: int, game_type: str, result: str, tokens_spent: int, tokens_won: int):
        """사용자 게임 통계 업데이트"""
        stats = GameSessionRepository.get_or_create_user_stats(db, user_id)
        
        # 전체 통계 업데이트
        stats.total_games_played = stats.total_games_played + 1
        stats.total_tokens_spent = stats.total_tokens_spent + tokens_spent
        stats.total_tokens_won = stats.total_tokens_won + tokens_won
        stats.profit_loss = stats.total_tokens_won - stats.total_tokens_spent
        
        # 승/패 업데이트
        is_win = result in ["win", "jackpot", "bonus"]
        if is_win:
            stats.total_wins = stats.total_wins + 1
            stats.current_win_streak = stats.current_win_streak + 1
            
            # SQL 표현식에서는 직접 비교 대신 case when 구문을 사용해야 하지만
            # 여기서는 Python 변수로 가져와 비교 후 다시 할당하는 방식으로 처리
            if db.query(GameStats.current_win_streak).filter(GameStats.id == stats.id).scalar() > db.query(GameStats.longest_win_streak).filter(GameStats.id == stats.id).scalar():
                stats.longest_win_streak = stats.current_win_streak
        else:
            stats.total_losses = stats.total_losses + 1
            stats.current_win_streak = 0
        
        # 승률 계산
        total_games = db.query(GameStats.total_games_played).filter(GameStats.id == stats.id).scalar()
        total_wins = db.query(GameStats.total_wins).filter(GameStats.id == stats.id).scalar()
        if total_games > 0:
            stats.win_rate = (total_wins / total_games) * 100
            
        # 게임별 통계 업데이트
        if game_type == "slot":
            stats.slot_plays = stats.slot_plays + 1
            if is_win:
                stats.slot_wins = stats.slot_wins + 1
        elif game_type == "prize_roulette":
            stats.roulette_spins = stats.roulette_spins + 1
            if is_win:
                stats.roulette_wins = stats.roulette_wins + 1
        elif game_type == "gacha":
            stats.gacha_pulls = stats.gacha_pulls + 1
            if result == "rare":
                stats.gacha_rare_items = stats.gacha_rare_items + 1
        elif game_type == "rock_paper_scissors":
            stats.rps_plays = stats.rps_plays + 1
            if is_win:
                stats.rps_wins = stats.rps_wins + 1
                
        # 선호 게임 업데이트 (SQL에서 직접 계산하는 것이 좋지만 여기서는 간단히 구현)
        # 실제 구현에서는 서브쿼리나 case when 구문을 활용해야 함
        game_plays = db.query(
            GameStats.slot_plays, 
            GameStats.roulette_spins, 
            GameStats.gacha_pulls, 
            GameStats.rps_plays
        ).filter(GameStats.id == stats.id).first()
        
        if game_plays:
            game_dict = {
                "slot": game_plays[0] or 0,
                "prize_roulette": game_plays[1] or 0,
                "gacha": game_plays[2] or 0,
                "rock_paper_scissors": game_plays[3] or 0
            }
            favorite = max(game_dict.items(), key=lambda x: x[1])
            stats.favorite_game = favorite[0]
        
        # 최근 플레이 정보 업데이트
        stats.last_played_at = datetime.utcnow()
        stats.last_game_type = game_type
        
        db.commit()
        db.refresh(stats)
        return stats
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int):
        """사용자 게임 통계 조회"""
        return GameSessionRepository.get_or_create_user_stats(db, user_id)
    
    @staticmethod
    def check_daily_limit(db: Session, user_id: int, game_type: str):
        """일일 게임 제한 확인"""
        today = datetime.utcnow().date()
        
        # 오늘의 제한 기록 조회
        limit_record = db.query(DailyGameLimit).filter(
            DailyGameLimit.user_id == user_id,
            DailyGameLimit.game_type == game_type,
            func.date(DailyGameLimit.date) == today
        ).first()
        
        # 없으면 새 기록 생성
        if not limit_record:
            limit_record = DailyGameLimit(
                user_id=user_id,
                game_type=game_type,
                date=today,
                plays_used=0
            )
            db.add(limit_record)
            db.commit()
            db.refresh(limit_record)
        
        # 제한 확인 (사용량 < 최대량)
        can_play = limit_record.plays_used < limit_record.max_plays
        
        # 쿨다운 확인
        cooldown_active = False
        if limit_record.cooldown_expires_at and limit_record.cooldown_expires_at > datetime.utcnow():
            cooldown_active = True
            
        return {
            "can_play": can_play and not cooldown_active,
            "plays_used": limit_record.plays_used,
            "max_plays": limit_record.max_plays,
            "plays_left": max(0, limit_record.max_plays - limit_record.plays_used),
            "cooldown_active": cooldown_active,
            "cooldown_expires_at": limit_record.cooldown_expires_at
        }
    
    @staticmethod
    def use_daily_play(db: Session, user_id: int, game_type: str, cooldown_minutes: int = 0):
        """일일 게임 사용량 증가 및 쿨다운 설정"""
        today = datetime.utcnow().date()
        
        limit_record = db.query(DailyGameLimit).filter(
            DailyGameLimit.user_id == user_id,
            DailyGameLimit.game_type == game_type,
            func.date(DailyGameLimit.date) == today
        ).first()
        
        if not limit_record:
            limit_record = DailyGameLimit(
                user_id=user_id,
                game_type=game_type,
                date=today,
                plays_used=0
            )
            db.add(limit_record)
        
        # 사용량 증가
        limit_record.plays_used = limit_record.plays_used + 1
        limit_record.last_played_at = datetime.utcnow()
        
        # 쿨다운 설정 (있는 경우)
        if cooldown_minutes > 0:
            limit_record.cooldown_expires_at = datetime.utcnow() + timedelta(minutes=cooldown_minutes)
        
        db.commit()
        db.refresh(limit_record)
        return limit_record
