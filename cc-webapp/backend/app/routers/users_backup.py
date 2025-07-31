from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from ..auth.simple_auth import get_current_user
from ..database import get_db
from ..models.auth_clean import User
from ..models.game_models import UserAction
from ..models.analytics_models import UserSegment

router = APIRouter()


@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: int = Path(..., description="조회할 사용자 ID"),
    current_user_id: Optional[int] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자 프로필 조회 API
    - 본인 프로필: 상세 정보 모두 공개
    - 타인 프로필: 제한적 정보만 공개 (닉네임, 등급, 일부 통계)
    """
    
    if not current_user_id:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    
    # 조회 대상 사용자 확인
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 본인 프로필인지 확인
    is_own_profile = current_user_id == user_id
    
    # 기본 사용자 정보
    base_info = {
        "user_id": target_user.id,
        "nickname": target_user.nickname,
        "vip_tier": target_user.vip_tier,
        "created_at": target_user.created_at.isoformat()
    }
    
    # 활동 통계 계산 (공통)
    activity_stats = calculate_activity_stats(db, user_id)
    
    if is_own_profile:
        # 📋 본인 프로필: 모든 상세 정보 공개
        user_segment = db.query(UserSegment).filter(UserSegment.user_id == user_id).first()
        
        detailed_info = {
            **base_info,
            "site_id": target_user.site_id,
            "phone_number": target_user.phone_number,
            "cyber_tokens": target_user.cyber_tokens,
            "regular_coins": target_user.regular_coins,
            "premium_gems": target_user.premium_gems,
            "battlepass_level": target_user.battlepass_level,
            "total_spent": target_user.total_spent,
            "activity_stats": activity_stats,
            "segment_info": {
                "rfm_group": user_segment.rfm_group if user_segment else "UNKNOWN",
                "ltv_score": user_segment.ltv_score if user_segment else 0,
                "risk_profile": user_segment.risk_profile if user_segment else "MEDIUM"
            } if user_segment else None,
            "missions_info": get_user_missions(db, user_id),  # 진행 중인 미션
            "inventory_summary": get_inventory_summary(db, user_id)  # 보유 아이템 요약
        }
        
        return {
            "is_own_profile": True,
            "profile_type": "PRIVATE",
            "data": detailed_info
        }
    
    else:
        # 👥 타인 프로필: 제한적 정보만 공개
        limited_info = {
            **base_info,
            "activity_stats": {
                # 일부 통계만 공개 (민감한 정보 제외)
                "total_login_days": activity_stats.get("total_login_days", 0),
                "games_played_today": activity_stats.get("games_played_today", 0),
                "current_streak": activity_stats.get("current_streak", 0),
                "level_or_rank": f"레벨 {target_user.battlepass_level}" if target_user.battlepass_level else "초보자"
            }
        }
        
        return {
            "is_own_profile": False,
            "profile_type": "PUBLIC",
            "data": limited_info
        }


def calculate_activity_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """사용자 활동 통계 계산"""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    # 로그인 횟수 (총/최근 7일)
    total_logins = db.query(func.count(UserAction.id)).filter(
        UserAction.user_id == user_id,
        UserAction.action_type == "LOGIN"
    ).scalar() or 0
    
    recent_logins = db.query(func.count(UserAction.id)).filter(
        UserAction.user_id == user_id,
        UserAction.action_type == "LOGIN",
        func.date(UserAction.created_at) >= week_ago
    ).scalar() or 0
    
    # 게임 플레이 횟수 (오늘/이번 주)
    games_today = db.query(func.count(UserAction.id)).filter(
        UserAction.user_id == user_id,
        UserAction.action_type.in_(["SLOT_SPIN", "GACHA_SPIN"]),
        func.date(UserAction.created_at) == today
    ).scalar() or 0
    
    games_this_week = db.query(func.count(UserAction.id)).filter(
        UserAction.user_id == user_id,
        UserAction.action_type.in_(["SLOT_SPIN", "GACHA_SPIN"]),
        func.date(UserAction.created_at) >= week_ago
    ).scalar() or 0
    
    # 현재 스트릭 계산 (연속 로그인 일수)
    current_streak = calculate_login_streak(db, user_id)
    
    # 총 플레이 시간 추정 (액션 수 기반)
    total_actions = db.query(func.count(UserAction.id)).filter(
        UserAction.user_id == user_id
    ).scalar() or 0
    estimated_play_time = total_actions * 2  # 액션당 평균 2분 추정
    
    return {
        "total_login_days": total_logins,
        "recent_login_days": recent_logins,
        "games_played_today": games_today,
        "games_played_week": games_this_week,
        "current_streak": current_streak,
        "estimated_play_time_minutes": estimated_play_time,
        "total_actions": total_actions
    }


def calculate_login_streak(db: Session, user_id: int) -> int:
    """연속 로그인 일수 계산"""
    today = datetime.utcnow().date()
    current_date = today
    streak = 0
    
    # 최대 30일까지만 확인 (성능상 제한)
    for i in range(30):
        login_exists = db.query(UserAction.id).filter(
            UserAction.user_id == user_id,
            UserAction.action_type == "LOGIN",
            func.date(UserAction.created_at) == current_date
        ).first()
        
        if login_exists:
            streak += 1
            current_date = current_date - timedelta(days=1)
        else:
            break
    
    return streak


def get_user_missions(db: Session, user_id: int) -> list:
    """진행 중인 미션 정보 (구현 예정)"""
    # TODO: 미션 시스템 구현 후 실제 미션 데이터 반환
    return [
        {
            "mission_id": "daily_login",
            "title": "매일 로그인하기",
            "progress": 5,
            "target": 7,
            "reward": "100 사이버 토큰",
            "expires_at": "2025-08-01T00:00:00Z"
        },
        {
            "mission_id": "slot_master",
            "title": "슬롯 10회 플레이",
            "progress": 7,
            "target": 10,
            "reward": "50 프리미엄 젬",
            "expires_at": "2025-08-01T00:00:00Z"
        }
    ]


def get_inventory_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """보유 아이템 요약 (구현 예정)"""
    # TODO: 인벤토리 시스템 구현 후 실제 아이템 데이터 반환
    return {
        "total_items": 12,
        "rare_items": 3,
        "recent_acquisitions": [
            {"name": "황금 코인", "rarity": "SR", "acquired_at": "2025-07-30T12:00:00Z"},
            {"name": "럭키 참", "rarity": "R", "acquired_at": "2025-07-29T15:30:00Z"}
        ]
    }


@router.post("/users")
async def create_user():
    return {"message": "User endpoint stub"}
