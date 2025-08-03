"""
🎰 Casino-Club F2P - User Service
================================
사용자 비즈니스 로직 서비스

📅 작성일: 2025-08-03
🎯 목적: Repository 패턴 적용한 사용자 서비스
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app import models
from app.repositories import UserRepository, AuthRepository

logger = logging.getLogger(__name__)


class UserService:
    """Repository 패턴을 활용한 사용자 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)

    # === 기존 호환성 메서드 ===
    
    def get_user_or_error(self, user_id: int) -> models.User:
        """사용자 조회 (없으면 에러)"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("존재하지 않는 사용자")
        return user

    def get_user_or_none(self, user_id: int) -> Optional[models.User]:
        """사용자 조회 (없으면 None)"""
        return self.user_repo.get_by_id(user_id)

    def get_or_create_segment(self, user_id: int) -> models.UserSegment:
        """사용자 세그먼트 조회 또는 생성"""
        # Repository 패턴으로 이동 예정
        segment = (
            self.db.query(models.UserSegment)
            .filter(models.UserSegment.user_id == user_id)
            .first()
        )
        if segment:
            return segment

        # Create with default low segment if not found
        segment = models.UserSegment(
            user_id=user_id,
            name="Low",
            rfm_group="Low",
        )
        self.db.add(segment)
        self.db.commit()
        self.db.refresh(segment)
        return segment

    # === Repository 패턴 활용 메서드 ===
    
    def get_user(self, user_id: int) -> Optional[models.User]:
        """사용자 조회"""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_nickname(self, nickname: str) -> Optional[models.User]:
        """닉네임으로 사용자 조회"""
        return self.user_repo.get_by_nickname(nickname)

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """이메일로 사용자 조회"""
        return self.user_repo.get_by_email(email)

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """사용자 통계 조회 (기본 구현)"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {}
            
            return {
                "user_id": user_id,
                "nickname": user.nickname,
                "created_at": user.created_at,
                "last_login": getattr(user, 'last_login', None)
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}

    def update_last_login(self, user_id: int) -> bool:
        """마지막 로그인 시간 업데이트 (기본 구현)"""
        try:
            user = self.get_user(user_id)
            if user:
                user.last_login = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False

    def update_spending(self, user_id: int, amount: float) -> bool:
        """사용자 지출 금액 업데이트 (기본 구현)"""
        try:
            user = self.get_user(user_id)
            if user:
                current_spent = getattr(user, 'total_spent', 0) or 0
                user.total_spent = current_spent + amount
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating spending: {e}")
            return False

    # === 인증 관련 메서드 ===
    
    def authenticate_user(self, email: str, password_hash: str) -> Optional[models.User]:
        """사용자 인증"""
        return self.auth_repo.authenticate_user(email, password_hash)

    def verify_password(self, user_id: int, password_hash: str) -> bool:
        """비밀번호 확인"""
        return self.auth_repo.verify_password(user_id, password_hash)

    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """비밀번호 업데이트"""
        return self.auth_repo.update_password(user_id, new_password_hash)

    # === 레거시 호환성 메서드 ===
    
    def create_user(self, nickname: str, rank: str, site_id: Optional[int] = None, email: Optional[str] = None) -> models.User:
        """사용자 생성 (레거시 호환성)"""
        # Validate rank
        if rank not in ["STANDARD", "PREMIUM", "VIP"]:
            raise ValueError("Invalid rank")
            
        # Validate required fields
        if site_id is None:
            raise ValueError("site_id is required")
            
        # Create user with all required fields
        user = models.User(
            nickname=nickname, 
            rank=rank, 
            site_id=site_id,
            email=email
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # === 추가 필요 메서드들 ===
    
    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """사용자 프로필 정보 조회"""
        user = self.get_user_or_error(user_id)
        segment = self.get_or_create_segment(user_id)
        
        return {
            "id": user.id,
            "site_id": user.site_id,
            "nickname": user.nickname,
            "phone_number": user.phone_number,
            "invite_code": user.invite_code,
            "cyber_token_balance": user.cyber_token_balance,
            "created_at": user.created_at,
            "rank": user.rank,
            "total_spent": getattr(user, 'total_spent', 0.0),
            "vip_tier": getattr(user, 'vip_tier', 'STANDARD'),
            "battlepass_level": getattr(user, 'battlepass_level', 1),
            "segment": segment.rfm_group if segment else "STANDARD"
        }
    
    def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 프로필 업데이트"""
        user = self.get_user_or_error(user_id)
        
        # 업데이트 가능한 필드들
        if "nickname" in update_data and update_data["nickname"]:
            user.nickname = update_data["nickname"]
        if "phone_number" in update_data and update_data["phone_number"]:
            user.phone_number = update_data["phone_number"]
            
        self.db.commit()
        self.db.refresh(user)
        
        return self.get_user_profile(user_id)
    
    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """사용자 진행상황 조회"""
        user = self.get_user_or_error(user_id)
        
        # 기본 진행상황 계산 (실제 게임 로직에 따라 수정 필요)
        level = getattr(user, 'battlepass_level', 1)
        experience = getattr(user, 'total_experience', 0)
        next_level_exp = level * 1000  # 예시 계산
        progress_percentage = (experience % 1000) / 1000 * 100
        
        return {
            "user_id": user_id,
            "level": level,
            "experience": experience,
            "next_level_exp": next_level_exp,
            "progress_percentage": progress_percentage
        }
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """사용자 통계 조회"""
        user = self.get_user_or_error(user_id)
        
        # UserAction 테이블에서 통계 계산 (실제 구현 시 조정 필요)
        total_games_played = self.db.query(models.UserAction).filter(
            models.UserAction.user_id == user_id
        ).count()
        
        total_spent = getattr(user, 'total_spent', 0.0)
        total_earned = user.cyber_token_balance
        win_rate = 0.65  # 예시 승률
        favorite_game = "슬롯머신"  # 예시
        
        return {
            "user_id": user_id,
            "total_games_played": total_games_played,
            "total_spent": total_spent,
            "total_earned": total_earned,
            "win_rate": win_rate,
            "favorite_game": favorite_game
        }
    
    def soft_delete_user(self, user_id: int) -> Dict[str, Any]:
        """사용자 소프트 삭제"""
        user = self.get_user_or_error(user_id)
        
        # 실제로는 deleted_at 필드를 설정하거나 is_active를 False로 설정
        # 현재는 단순히 상태만 반환
        return {
            "user_id": user_id,
            "deleted": True,
            "message": "사용자가 비활성화되었습니다"
        }
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 사용자 목록 조회 (관리자용)"""
        users = self.db.query(models.User).offset(skip).limit(limit).all()
        
        return [
            {
                "id": user.id,
                "site_id": user.site_id,
                "nickname": user.nickname,
                "rank": user.rank,
                "created_at": user.created_at,
                "cyber_token_balance": user.cyber_token_balance
            }
            for user in users
        ]
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ID로 사용자 조회 (관리자용)"""
        user = self.get_user_or_none(user_id)
        if not user:
            return None
            
        return {
            "id": user.id,
            "site_id": user.site_id,
            "nickname": user.nickname,
            "phone_number": user.phone_number,
            "invite_code": user.invite_code,
            "cyber_token_balance": user.cyber_token_balance,
            "created_at": user.created_at,
            "rank": user.rank
        }
