from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class ActivityStats(BaseModel):
    """사용자 활동 통계"""
    total_login_days: int
    recent_login_days: Optional[int] = None
    games_played_today: int
    games_played_week: Optional[int] = None
    current_streak: int
    estimated_play_time_minutes: Optional[int] = None
    total_actions: Optional[int] = None
    level_or_rank: Optional[str] = None


class SegmentInfo(BaseModel):
    """사용자 세그먼트 정보"""
    rfm_group: str
    ltv_score: float
    risk_profile: str


class MissionInfo(BaseModel):
    """미션 정보"""
    mission_id: str
    title: str
    progress: int
    target: int
    reward: str
    expires_at: str


class RecentItem(BaseModel):
    """최근 획득 아이템"""
    name: str
    rarity: str
    acquired_at: str


class InventorySummary(BaseModel):
    """인벤토리 요약"""
    total_items: int
    rare_items: int
    recent_acquisitions: List[RecentItem]


class UserProfilePrivate(BaseModel):
    """본인 프로필 (상세 정보)"""
    user_id: int
    nickname: str
    site_id: str
    phone_number: str
    vip_tier: str
    created_at: datetime
    cyber_tokens: int
    regular_coins: int
    premium_gems: int
    battlepass_level: int
    total_spent: float
    activity_stats: ActivityStats
    segment_info: Optional[SegmentInfo] = None
    missions_info: List[MissionInfo]
    inventory_summary: InventorySummary


class UserProfilePublic(BaseModel):
    """타인 프로필 (제한적 정보)"""
    user_id: int
    nickname: str
    vip_tier: str
    created_at: datetime
    activity_stats: ActivityStats  # 제한된 통계만


class UserProfileResponse(BaseModel):
    """프로필 조회 응답"""
    is_own_profile: bool
    profile_type: Literal["PRIVATE", "PUBLIC"]
    data: Dict[str, Any]  # UserProfilePrivate 또는 UserProfilePublic
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 프로필 수정을 위한 스키마들
class UserProfileUpdateRequest(BaseModel):
    """프로필 수정 요청"""
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    # 기타 수정 가능한 필드들...


class UserProfileUpdateResponse(BaseModel):
    """프로필 수정 응답"""
    success: bool
    message: str
    updated_fields: List[str]
