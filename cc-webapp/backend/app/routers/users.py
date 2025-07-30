from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models import Mission, UserMissionProgress, Avatar, UserProfileImage
from app.routers.auth import get_user_from_token

router = APIRouter()

# Response 모델 정의
class MissionProgressInfo(BaseModel):
    """미션 진행 정보"""
    mission_id: int
    title: str
    description: Optional[str] = None
    mission_type: str
    current_progress: int
    target_value: int
    progress_percentage: float
    reward_type: str
    reward_amount: int
    reward_description: Optional[str] = None
    is_completed: bool
    is_claimed: bool
    is_daily: bool
    is_weekly: bool

class ProfileImageInfo(BaseModel):
    """프로필 이미지 정보"""
    image_url: Optional[str] = None
    image_type: str = "default"  # avatar, custom, default
    avatar_name: Optional[str] = None
    avatar_category: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    site_id: str
    nickname: str
    cyber_token_balance: int
    rank: str
    created_at: str
    last_login_at: Optional[str] = None
    login_count: int
    
    # 통계 정보 (본인일 때만)
    phone_number: Optional[str] = None
    invite_code: Optional[str] = None
    failed_login_attempts: Optional[int] = None
    
    # 새로운 정보들
    active_missions: List[MissionProgressInfo] = []
    profile_image: Optional[ProfileImageInfo] = None
    
    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    """사용자 활동 통계"""
    total_actions: int = 0
    total_rewards: int = 0
    total_spent: int = 0
    play_time_minutes: int = 0
    last_activity: Optional[str] = None

@router.get("/users/{user_id}/profile", response_model=UserProfileResponse, tags=["Users"])
async def get_user_profile(
    user_id: str,  # "me" 또는 실제 사용자 ID
    current_user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """
    사용자 프로필 조회 API
    
    - user_id가 "me"인 경우: 현재 로그인한 사용자의 프로필
    - user_id가 숫자인 경우: 해당 사용자의 프로필
    
    권한 기반 정보 필터링:
    - 본인: 모든 정보 조회 가능 (민감 정보 포함)
    - 타인: 공개 정보만 조회 가능 (닉네임, 등급 등)
    - 관리자: 모든 사용자 정보 조회 가능
    """
    
    try:
        # 현재 사용자 객체 가져오기
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # "me"인 경우 현재 사용자로 설정
        if user_id == "me":
            target_user = current_user
            is_self = True
        else:
            # 숫자 ID인 경우 해당 사용자 조회
            try:
                target_user_id = int(user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="올바르지 않은 사용자 ID 형식입니다"
                )
                
            target_user = db.query(User).filter(User.id == target_user_id).first()
            if not target_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다"
                )
            is_self = current_user.id == target_user_id
        
        # 권한 확인
        is_admin = current_user.rank == "ADMIN"
        
        # 응답 데이터 구성
        profile_data = {
            "id": target_user.id,
            "site_id": target_user.site_id,
            "nickname": target_user.nickname,
            "cyber_token_balance": target_user.cyber_token_balance,
            "rank": target_user.rank,
            "created_at": target_user.created_at.isoformat() if target_user.created_at else None,
            "last_login_at": target_user.last_login_at.isoformat() if target_user.last_login_at else None,
            "login_count": target_user.login_count,
            "active_missions": [],
            "profile_image": None
        }
        
        # 미션 정보 추가 (본인이거나 관리자일 때만)
        if is_self or is_admin:
            # 진행 중인 미션들 조회
            mission_progress = db.query(UserMissionProgress).join(Mission).filter(
                UserMissionProgress.user_id == target_user.id,
                UserMissionProgress.is_completed == False,
                Mission.is_active == True
            ).order_by(Mission.priority.desc(), Mission.created_at.asc()).limit(10).all()
            
            active_missions = []
            for progress in mission_progress:
                mission = progress.mission
                progress_percentage = (progress.current_progress / mission.target_value * 100) if mission.target_value > 0 else 0
                active_missions.append({
                    "mission_id": mission.id,
                    "title": mission.title,
                    "description": mission.description,
                    "mission_type": mission.mission_type,
                    "current_progress": progress.current_progress,
                    "target_value": mission.target_value,
                    "progress_percentage": min(100, progress_percentage),
                    "reward_type": mission.reward_type,
                    "reward_amount": mission.reward_amount,
                    "reward_description": mission.reward_description,
                    "is_completed": progress.is_completed,
                    "is_claimed": progress.is_claimed,
                    "is_daily": mission.is_daily,
                    "is_weekly": mission.is_weekly
                })
            
            profile_data["active_missions"] = active_missions
        
        # 프로필 이미지 정보 추가
        profile_image = db.query(UserProfileImage).filter(
            UserProfileImage.user_id == target_user.id,
            UserProfileImage.is_active == True
        ).first()
        
        if profile_image:
            image_info = {
                "image_type": profile_image.image_type,
                "image_url": None,
                "avatar_name": None,
                "avatar_category": None
            }
            
            if profile_image.custom_image_url:
                image_info["image_url"] = profile_image.custom_image_url
                image_info["image_type"] = "custom"
            elif profile_image.avatar_id:
                avatar = db.query(Avatar).filter(Avatar.id == profile_image.avatar_id).first()
                if avatar:
                    image_info["image_url"] = avatar.image_url
                    image_info["avatar_name"] = avatar.name
                    image_info["avatar_category"] = avatar.category
                    image_info["image_type"] = "avatar"
            
            profile_data["profile_image"] = image_info
        else:
            # 기본 프로필 이미지
            profile_data["profile_image"] = {
                "image_type": "default",
                "image_url": "/static/images/default_avatar.png",
                "avatar_name": "기본 아바타",
                "avatar_category": "basic"
            }
        
        # 민감 정보는 본인이거나 관리자일 때만 포함
        if is_self or is_admin:
            profile_data.update({
                "phone_number": target_user.phone_number,
                "invite_code": target_user.invite_code,
                "failed_login_attempts": target_user.failed_login_attempts
            })
        
        return profile_data
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Profile API error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 조회 중 오류 발생: {str(e)}"
        )

@router.get("/users/{user_id}/stats", response_model=UserStatsResponse, tags=["Users"])
async def get_user_stats(
    user_id: str,  # "me" 또는 실제 사용자 ID
    current_user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """
    사용자 활동 통계 조회
    
    - user_id가 "me"인 경우: 현재 로그인한 사용자의 통계
    - user_id가 숫자인 경우: 해당 사용자의 통계
    
    권한: 본인이거나 관리자만 조회 가능
    """
    
    # 현재 사용자 객체 가져오기
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # "me"인 경우 현재 사용자로 설정
    if user_id == "me":
        target_user = current_user
        is_self = True
    else:
        # 숫자 ID인 경우 해당 사용자 조회
        try:
            target_user_id = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="올바르지 않은 사용자 ID 형식입니다"
            )
            
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        is_self = current_user.id == target_user_id
    
    # 권한 확인 (본인이거나 관리자만)
    is_admin = current_user.rank == "ADMIN"
    
    if not (is_self or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 통계를 볼 권한이 없습니다"
        )
    
    # 통계 계산 (실제 구현에서는 user_actions, user_rewards 테이블 조인)
    try:
        # TODO: 실제 통계 쿼리 구현
        # from app.models.user_action import UserAction
        # from app.models.user_reward import UserReward
        
        stats = {
            "total_actions": 0,  # db.query(UserAction).filter(UserAction.user_id == target_user.id).count()
            "total_rewards": 0,  # db.query(UserReward).filter(UserReward.user_id == target_user.id).count()
            "total_spent": 0,    # 실제 구매 내역에서 계산
            "play_time_minutes": 0,  # 세션 시간 합계
            "last_activity": target_user.last_login_at.isoformat() if target_user.last_login_at else None
        }
        
        return stats
    except Exception as e:
        # 통계 계산 중 오류 시 기본값 반환
        return UserStatsResponse()


# --- 미션 관련 API ---
@router.get("/users/{user_id}/missions", tags=["Users", "Missions"])
async def get_user_missions(
    user_id: str,
    current_user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """사용자의 미션 목록 조회 (진행 중, 완료, 전체)"""
    
    # 현재 사용자 확인
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
    
    # 타겟 사용자 확인
    if user_id == "me":
        target_user = current_user
        is_self = True
    else:
        try:
            target_user_id = int(user_id)
            target_user = db.query(User).filter(User.id == target_user_id).first()
            if not target_user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
            is_self = current_user.id == target_user_id
        except ValueError:
            raise HTTPException(status_code=400, detail="올바르지 않은 사용자 ID")
    
    # 권한 확인
    is_admin = current_user.rank == "ADMIN"
    if not (is_self or is_admin):
        raise HTTPException(status_code=403, detail="다른 사용자의 미션을 볼 권한이 없습니다")
    
    # 미션 진행 상황 조회
    mission_progress = db.query(UserMissionProgress).join(Mission).filter(
        UserMissionProgress.user_id == target_user.id,
        Mission.is_active == True
    ).order_by(Mission.priority.desc(), Mission.created_at.asc()).all()
    
    missions = []
    for progress in mission_progress:
        mission = progress.mission
        progress_percentage = (progress.current_progress / mission.target_value * 100) if mission.target_value > 0 else 0
        missions.append({
            "mission_id": mission.id,
            "title": mission.title,
            "description": mission.description,
            "mission_type": mission.mission_type,
            "current_progress": progress.current_progress,
            "target_value": mission.target_value,
            "progress_percentage": min(100, progress_percentage),
            "reward_type": mission.reward_type,
            "reward_amount": mission.reward_amount,
            "reward_description": mission.reward_description,
            "is_completed": progress.is_completed,
            "is_claimed": progress.is_claimed,
            "is_daily": mission.is_daily,
            "is_weekly": mission.is_weekly,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            "claimed_at": progress.claimed_at.isoformat() if progress.claimed_at else None
        })
    
    return {"missions": missions, "total_count": len(missions)}


@router.post("/users/{user_id}/missions/{mission_id}/claim", tags=["Users", "Missions"])
async def claim_mission_reward(
    user_id: str,
    mission_id: int,
    current_user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """미션 보상 수령"""
    
    # 현재 사용자 확인
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
    
    # 타겟 사용자 확인
    if user_id == "me":
        target_user = current_user
        is_self = True
    else:
        try:
            target_user_id = int(user_id)
            target_user = db.query(User).filter(User.id == target_user_id).first()
            if not target_user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
            is_self = current_user.id == target_user_id
        except ValueError:
            raise HTTPException(status_code=400, detail="올바르지 않은 사용자 ID")
    
    # 본인만 보상 수령 가능
    if not is_self:
        raise HTTPException(status_code=403, detail="본인의 미션 보상만 수령할 수 있습니다")
    
    # 미션 진행 상황 확인
    progress = db.query(UserMissionProgress).filter(
        UserMissionProgress.user_id == target_user.id,
        UserMissionProgress.mission_id == mission_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    
    if not progress.is_completed:
        raise HTTPException(status_code=400, detail="완료되지 않은 미션입니다")
    
    if progress.is_claimed:
        raise HTTPException(status_code=400, detail="이미 수령한 보상입니다")
    
    # 미션 정보 조회
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="미션 정보를 찾을 수 없습니다")
    
    # 보상 지급
    try:
        if mission.reward_type == "cyber_token":
            target_user.cyber_token_balance += mission.reward_amount
        # TODO: 다른 보상 타입들 구현 (premium_gem, item 등)
        
        # 보상 수령 상태 업데이트
        progress.is_claimed = True
        progress.claimed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"보상을 수령했습니다: {mission.reward_description}",
            "reward_type": mission.reward_type,
            "reward_amount": mission.reward_amount,
            "new_balance": target_user.cyber_token_balance if mission.reward_type == "cyber_token" else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"보상 지급 중 오류 발생: {str(e)}")


# --- 프로필 이미지/아바타 관련 API ---
@router.get("/avatars", tags=["Avatars"])
async def get_available_avatars(
    current_user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """사용 가능한 아바타 목록 조회"""
    
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
    
    # 사용자 등급에 맞는 아바타들 조회
    rank_order = {"STANDARD": 1, "PREMIUM": 2, "VIP": 3, "ADMIN": 4}
    user_rank_level = rank_order.get(current_user.rank, 1)
    
    avatars = db.query(Avatar).filter(
        Avatar.is_active == True,
        Avatar.required_rank.in_([k for k, v in rank_order.items() if v <= user_rank_level])
    ).order_by(Avatar.category, Avatar.sort_order).all()
    
    avatar_list = []
    for avatar in avatars:
        avatar_list.append({
            "id": avatar.id,
            "name": avatar.name,
            "description": avatar.description,
            "image_url": avatar.image_url,
            "thumbnail_url": avatar.thumbnail_url or avatar.image_url,
            "category": avatar.category,
            "unlock_condition": avatar.unlock_condition,
            "required_rank": avatar.required_rank,
            "is_premium": avatar.is_premium
        })
    
    return {"avatars": avatar_list}


@router.post("/users/{user_id}/avatar", tags=["Users", "Avatars"])
async def set_user_avatar(
    user_id: str,
    avatar_id: int,
    current_user_id: int = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """사용자 아바타 설정"""
    
    # 현재 사용자 확인
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
    
    # 타겟 사용자 확인
    if user_id == "me":
        target_user = current_user
        is_self = True
    else:
        try:
            target_user_id = int(user_id)
            target_user = db.query(User).filter(User.id == target_user_id).first()
            if not target_user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
            is_self = current_user.id == target_user_id
        except ValueError:
            raise HTTPException(status_code=400, detail="올바르지 않은 사용자 ID")
    
    # 본인만 아바타 설정 가능
    if not is_self:
        raise HTTPException(status_code=403, detail="본인의 아바타만 설정할 수 있습니다")
    
    # 아바타 확인
    avatar = db.query(Avatar).filter(
        Avatar.id == avatar_id,
        Avatar.is_active == True
    ).first()
    
    if not avatar:
        raise HTTPException(status_code=404, detail="아바타를 찾을 수 없습니다")
    
    # 권한 확인
    rank_order = {"STANDARD": 1, "PREMIUM": 2, "VIP": 3, "ADMIN": 4}
    user_rank_level = rank_order.get(target_user.rank, 1)
    required_rank_level = rank_order.get(avatar.required_rank, 1)
    
    if user_rank_level < required_rank_level:
        raise HTTPException(
            status_code=403, 
            detail=f"이 아바타는 {avatar.required_rank} 등급 이상만 사용할 수 있습니다"
        )
    
    try:
        # 기존 프로필 이미지 설정 조회/생성
        profile_image = db.query(UserProfileImage).filter(
            UserProfileImage.user_id == target_user.id
        ).first()
        
        if profile_image:
            # 기존 설정 업데이트
            profile_image.avatar_id = avatar_id
            profile_image.custom_image_url = None
            profile_image.image_type = "avatar"
            profile_image.updated_at = datetime.utcnow()
        else:
            # 새로운 설정 생성
            profile_image = UserProfileImage(
                user_id=target_user.id,
                avatar_id=avatar_id,
                image_type="avatar"
            )
            db.add(profile_image)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"아바타가 '{avatar.name}'로 변경되었습니다",
            "avatar": {
                "id": avatar.id,
                "name": avatar.name,
                "image_url": avatar.image_url,
                "category": avatar.category
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"아바타 설정 중 오류 발생: {str(e)}")
