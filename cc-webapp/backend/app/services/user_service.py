from sqlalchemy.orm import Session
from app import models

class UserService:
    """Utility service for common user lookups."""

    def __init__(self, db: Session = None, repository=None) -> None:
        self.db = db
        self.repository = repository

    def get_user_or_error(self, user_id: int) -> models.User:
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("존재하지 않는 사용자")
        return user

    def get_user_or_none(self, user_id: int) -> models.User | None:
        """Return user if exists, otherwise None."""
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_or_create_segment(self, user_id: int) -> models.UserSegment:
        """Fetch user's segment or create a default one if missing."""
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

    # --- 테스트 요구 메서드 구현 ---
    def get_user(self, user_id):
        if self.repository:
            return self.repository.get_user(user_id)
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def create_user(self, nickname, rank, site_id=None, email=None):
        """Create a new user with validation for required fields.
        
        Args:
            nickname: User's nickname
            rank: User's rank (STANDARD, PREMIUM, VIP)
            site_id: Required site ID for user
            email: Optional email address
            
        Returns:
            Created user object
        
        Raises:
            ValueError: If rank is invalid or required fields are missing
        """
        # Validate rank
        if rank not in ["STANDARD", "PREMIUM", "VIP"]:
            raise ValueError("Invalid rank")
            
        # Validate required fields
        if site_id is None:
            raise ValueError("site_id is required")
            
        if self.repository:
            return self.repository.create_user(nickname, rank, site_id=site_id, email=email)
            
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

    def update_user_rank(self, user_id, rank):
        if rank not in ["STANDARD", "PREMIUM", "VIP"]:
            raise ValueError("Invalid rank")
        if self.repository:
            return self.repository.update_user_rank(user_id, rank)
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.rank = rank
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id):
        if self.repository:
            return self.repository.delete_user(user_id)
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
