"""
모든 게임 �??�로???�합 API ?�우??
- PrizeRoulette, ?�롯, 가�? 배�??�스, ?�적, 리더보드, ?�로???�계 ??
- 20250729-가?�드006.md??모든 ?�심 ?�드?�인???�함
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.game_schemas import (
    RouletteInfoResponse, RouletteSpinResponse, GameStats, ProfileGameStats,
    GameLeaderboard, Achievement, GameSession
)
from app import models
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/games", tags=["games"])

# 1. 게임 ?�계 조회 API
@router.get("/stats/{user_id}", response_model=GameStats)
def get_game_stats(user_id: int, db = Depends(get_db)):
    """
    ?�용??게임 ?�계 조회 (?�롯/룰렛/가�???
    - �??��?/?�운?? 코인/???�이????��/보너???�득, ?�트�???
    """
    # UserAction???�용?�여 게임 로그 집계
    total_spins = db.query(models.UserAction).filter(
        models.UserAction.user_id == user_id,
        models.UserAction.action_type.in_(['SLOT_SPIN', 'ROULETTE_SPIN', 'GACHA_SPIN'])
    ).count()
    
    total_coins_won = db.query(models.UserReward).filter(
        models.UserReward.user_id == user_id, 
        models.UserReward.reward.has(reward_type="COINS")
    ).count()
    
    total_gems_won = db.query(models.UserReward).filter(
        models.UserReward.user_id == user_id, 
        models.UserReward.reward.has(reward_type="GEMS")
    ).count()
    
    special_items_won = db.query(models.UserReward).filter(
        models.UserReward.user_id == user_id, 
        models.UserReward.reward.has(reward_type="SPECIAL")
    ).count()
    
    # UserAction???�용?�여 ??�� 카운??
    jackpots_won = db.query(models.UserAction).filter(
        models.UserAction.user_id == user_id,
        models.UserAction.action_data.contains('"result":"jackpot"')
    ).count()
    
    bonus_spins_won = db.query(models.UserReward).filter(
        models.UserReward.user_id == user_id, 
        models.UserReward.reward.has(reward_type="BONUS")
    ).count()
    
    # ?�트�?? ?�단 0?�로 ?�정 (?�중??구현)
    best_streak = 0
    current_streak = 0
    
    # 마�?�??��? ?�짜
    last_action = db.query(models.UserAction).filter(
        models.UserAction.user_id == user_id,
        models.UserAction.action_type.in_(['SLOT_SPIN', 'ROULETTE_SPIN', 'GACHA_SPIN'])
    ).order_by(models.UserAction.created_at.desc()).first()
    
    last_spin_date = last_action.created_at if last_action else None
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

# 2. ?�시�?게임 ?�션 API
@router.get("/session/{user_id}/current", response_model=GameSession)
def get_current_game_session(user_id: int, db = Depends(get_db)):
    """
    ?�재 진행중인 게임 ?�션 ?�보 조회
    """
    session = db.query(models.UserSession).filter(
        models.UserSession.user_id == user_id, 
        models.UserSession.is_active == True
    ).order_by(models.UserSession.login_at.desc()).first()
    
    if session:
        return GameSession(
            session_id=session.session_id,
            user_id=session.user_id,
            game_type="roulette",  # ?�제 게임 ?�???�요??session??추�?
            start_time=session.login_at,
            status="active"
        )
    else:
        return GameSession(session_id="", user_id=user_id, game_type="", start_time=None, status="inactive")

@router.post("/session/start", response_model=GameSession)
def start_game_session(game_data: dict, db = Depends(get_db)):
    """
    게임 ?�션 ?�작
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
def end_game_session(session_data: dict, db = Depends(get_db)):
    """
    게임 ?�션 종료 �?결과 ?�??
    """
    session_id = session_data.get("session_id")
    user_id = session_data.get("user_id")
    session = db.query(models.UserSession).filter(
        models.UserSession.session_id == session_id, 
        models.UserSession.user_id == user_id
    ).first()
    
    if session:
        session.is_active = False
        session.logout_at = datetime.utcnow()
        session.logout_reason = session_data.get("logout_reason", "user_end")
        db.commit()
        return GameSession(session_id=session_id, user_id=user_id, game_type="roulette", start_time=session.login_at, status="completed")
    else:
        return GameSession(session_id=session_id, user_id=user_id, game_type="roulette", start_time=None, status="not_found")

# 3. 보상 �??�적 API
@router.get("/achievements/{user_id}", response_model=List[Achievement])
def get_user_achievements(user_id: int, db = Depends(get_db)):
    """
    ?�용???�적 �?보상 ?�역 조회
    """
    # ?�적 ?�이블이 별도 ?�다�?UserReward?�서 집계
    rewards = db.query(models.UserReward).filter(models.UserReward.user_id == user_id).all()
    achievements = []
    for r in rewards:
        achievements.append(Achievement(
            id=r.id,
            name=f"Reward {r.id}",
            description="Achievement earned",
            badge_icon="?��",
            badge_color="#FFD700",
            achieved_at=r.claimed_at,
            progress=1.0
        ))
    return achievements

# 4. 리더보드 API
@router.get("/leaderboard", response_model=GameLeaderboard)
def get_leaderboard(game_type: str, period: str = "week", limit: int = 10, db = Depends(get_db)):
    """
    게임�?리더보드 조회 (UserAction 기반)
    """
    # UserAction??기반?�로 리더보드 ?�성
    leaderboard_query = db.query(
        models.User.id,
        models.User.nickname
    ).join(models.UserAction, models.User.id == models.UserAction.user_id)
    
    if game_type:
        leaderboard_query = leaderboard_query.filter(
            models.UserAction.action_type.like(f"%{game_type.upper()}%")
        )
    
    # ?�용?�별 ?�션 ?�로 ?�수 계산
    users = leaderboard_query.distinct().limit(limit).all()
    entries = []
    
    for idx, user in enumerate(users):
        action_count = db.query(models.UserAction).filter(
            models.UserAction.user_id == user.id
        ).count()
        
        entries.append({
            "rank": idx + 1,
            "user_id": user.id,
            "nickname": user.nickname,
            "score": action_count,
            "avatar_url": None
        })
    
    return GameLeaderboard(game_type=game_type, period=period, entries=entries, updated_at=datetime.utcnow())

# 5. ?�로??게임 ?�계 API
@router.get("/profile/{user_id}/stats", response_model=ProfileGameStats)
def get_profile_game_stats(user_id: int, db = Depends(get_db)):
    """
    ?�로??게임 ?�계 조회
    """
    # 최근 ?�동/?�적/?�션 ???�합
    recent_activities = []
    actions = db.query(models.UserAction).filter(
        models.UserAction.user_id == user_id
    ).order_by(models.UserAction.created_at.desc()).limit(10).all()
    
    for a in actions:
        recent_activities.append({
            "game_type": a.action_type,
            "total_rounds": 1,
            "total_wins": 1 if "win" in str(a.action_data or "") else 0,
            "total_losses": 1 if "win" not in str(a.action_data or "") else 0,
            "win_rate": 1.0 if "win" in str(a.action_data or "") else 0.0,
            "favorite": False,
            "last_played": a.created_at
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
        current_session=current_session,
        updated_at=datetime.utcnow()
    )
