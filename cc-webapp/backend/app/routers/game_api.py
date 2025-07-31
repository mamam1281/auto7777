"""
모든 게임 및 프로필 통합 API 라우터
- PrizeRoulette, 슬롯, 가챠, 배틀패스, 업적, 리더보드, 프로필 통계 등
- 20250729-가이드006.md의 모든 핵심 엔드포인트 포함
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.database import get_db
from app.core.auth import get_current_active_user
from app.schemas.game_schemas import (
    RouletteInfoResponse, RouletteSpinResponse, GameStats, ProfileGameStats,
    GameLeaderboard, Achievement, GameSession
)
from app import models
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/games", tags=["games"])

# 1. 게임 통계 조회 API
@router.get("/stats/{user_id}", response_model=GameStats)
def get_game_stats(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 게임 통계 조회 (슬롯/룰렛/가챠 등)
    - 총 스핀/라운드, 코인/젬/아이템/잭팟/보너스 획득, 스트릭 등
    """
    # 슬롯/룰렛/가챠 등 모든 게임 로그 집계
    total_spins = db.query(models.GameLog).filter(models.GameLog.user_id == user_id).count()
    total_coins_won = db.query(models.UserReward).filter(models.UserReward.user_id == user_id, models.UserReward.reward_type == "COINS").count()
    total_gems_won = db.query(models.UserReward).filter(models.UserReward.user_id == user_id, models.UserReward.reward_type == "GEMS").count()
    special_items_won = db.query(models.UserReward).filter(models.UserReward.user_id == user_id, models.UserReward.reward_type == "SPECIAL").count()
    jackpots_won = db.query(models.GameLog).filter(models.GameLog.user_id == user_id, models.GameLog.result == "jackpot").count()
    bonus_spins_won = db.query(models.UserReward).filter(models.UserReward.user_id == user_id, models.UserReward.reward_type == "BONUS").count()
    best_streak = db.query(models.UserStreak.win_streak).filter(models.UserStreak.user_id == user_id).scalar() or 0
    current_streak = db.query(models.UserStreak.win_streak).filter(models.UserStreak.user_id == user_id).scalar() or 0
    last_spin_date = db.query(models.GameLog.created_at).filter(models.GameLog.user_id == user_id).order_by(models.GameLog.created_at.desc()).first()
    return GameStats(
        user_id=user_id,
        total_spins=total_spins,
        total_coins_won=total_coins_won,
        total_gems_won=total_gems_won,
        special_items_won=special_items_won,
        jackpots_won=jackpots_won,
        bonus_spins_won=bonus_spins_won,
        best_streak=best_streak,
        current_streak=current_streak,
        last_spin_date=last_spin_date[0] if last_spin_date else None
    )

# 2. 실시간 게임 세션 API
@router.get("/session/{user_id}/current", response_model=GameSession)
def get_current_game_session(user_id: int, db: Session = Depends(get_db)):
    """
    현재 진행중인 게임 세션 정보 조회
    """
    session = db.query(models.UserSession).filter(models.UserSession.user_id == user_id, models.UserSession.is_active == True).order_by(models.UserSession.login_at.desc()).first()
    if session:
        return GameSession(
            session_id=session.session_id,
            user_id=session.user_id,
            game_type="roulette",  # 실제 게임 타입 필요시 session에 추가
            start_time=session.login_at,
            status="active"
        )
    else:
        return GameSession(session_id="", user_id=user_id, game_type="", start_time=None, status="inactive")

@router.post("/session/start", response_model=GameSession)
def start_game_session(game_data: dict, db: Session = Depends(get_db)):
    """
    게임 세션 시작
    """
    import uuid
    session_id = str(uuid.uuid4())
    user_id = game_data.get("user_id", 1)
    game_type = game_data.get("game_type", "roulette")
    new_session = models.UserSession(
        user_id=user_id,
        session_id=session_id,
        login_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=2),
        is_active=True
    )
    db.add(new_session)
    db.commit()
    return GameSession(session_id=session_id, user_id=user_id, game_type=game_type, start_time=new_session.login_at, status="active")

@router.post("/session/end", response_model=GameSession)
def end_game_session(session_data: dict, db: Session = Depends(get_db)):
    """
    게임 세션 종료 및 결과 저장
    """
    session_id = session_data.get("session_id")
    user_id = session_data.get("user_id")
    session = db.query(models.UserSession).filter(models.UserSession.session_id == session_id, models.UserSession.user_id == user_id).first()
    if session:
        session.is_active = False
        session.logout_at = datetime.utcnow()
        session.logout_reason = session_data.get("logout_reason", "user_end")
        db.commit()
        return GameSession(session_id=session_id, user_id=user_id, game_type="roulette", start_time=session.login_at, status="completed")
    else:
        return GameSession(session_id=session_id, user_id=user_id, game_type="roulette", start_time=None, status="not_found")

# 3. 보상 및 업적 API
@router.get("/achievements/{user_id}", response_model=List[Achievement])
def get_user_achievements(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 업적 및 보상 내역 조회
    """
    # 업적 테이블이 별도 없다면 UserReward에서 집계
    rewards = db.query(models.UserReward).filter(models.UserReward.user_id == user_id).all()
    achievements = []
    for r in rewards:
        achievements.append(Achievement(
            id=r.id,
            name=r.reward_type,
            description=r.source_description or "",
            badge_icon="🏆",
            badge_color="#FFD700",
            achieved_at=r.awarded_at,
            progress=1.0
        ))
    return achievements

# 4. 리더보드 API
@router.get("/leaderboard", response_model=GameLeaderboard)
def get_leaderboard(game_type: str, period: str = "week", limit: int = 10, db: Session = Depends(get_db)):
    """
    게임별 리더보드 조회
    """
    # 예시: GameLog에서 score 집계 (실제 점수/승수/토큰 등 기준으로 변경)
    from sqlalchemy import func
    leaderboard_query = db.query(
        models.User.id,
        models.User.nickname,
        func.count(models.GameLog.id).label("score")
    ).join(models.GameLog, models.User.id == models.GameLog.user_id)
    if game_type:
        leaderboard_query = leaderboard_query.filter(models.GameLog.game_type == game_type)
    leaderboard_query = leaderboard_query.group_by(models.User.id, models.User.nickname).order_by(func.count(models.GameLog.id).desc()).limit(limit)
    entries = []
    for idx, row in enumerate(leaderboard_query):
        entries.append({
            "rank": idx + 1,
            "user_id": row.id,
            "nickname": row.nickname,
            "score": row.score,
            "avatar_url": None
        })
    return GameLeaderboard(game_type=game_type, period=period, entries=entries, updated_at=datetime.utcnow())

# 5. 프로필 게임 통계 API
@router.get("/profile/{user_id}/stats", response_model=ProfileGameStats)
def get_profile_game_stats(user_id: int, db: Session = Depends(get_db)):
    """
    프로필 게임 통계 조회
    """
    # 최근 활동/업적/세션 등 통합
    recent_activities = []
    actions = db.query(models.UserAction).filter(models.UserAction.user_id == user_id).order_by(models.UserAction.timestamp.desc()).limit(10).all()
    for a in actions:
        recent_activities.append({
            "game_type": a.action_type,
            "total_rounds": 1,
            "total_wins": 1 if a.value > 0 else 0,
            "total_losses": 1 if a.value <= 0 else 0,
            "win_rate": 1.0 if a.value > 0 else 0.0,
            "favorite": False,
            "last_played": a.timestamp
        })
    achievements = get_user_achievements(user_id, db)
    current_session = get_current_game_session(user_id, db)
    return ProfileGameStats(
        user_id=user_id,
        total_games_played=len(actions),
        total_time_played=None,
        favorite_game=None,
        recent_activities=recent_activities,
        achievements=achievements,
        current_session=current_session
    )
