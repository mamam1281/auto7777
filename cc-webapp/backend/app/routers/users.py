from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_user_from_token

router = APIRouter()

# Response 모델 정의
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
            "login_count": target_user.login_count
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
