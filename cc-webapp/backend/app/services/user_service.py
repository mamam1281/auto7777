from sqlalchemy.orm import Session
from app import models

class UserService:
    """Utility service for common user lookups."""

    def __init__(self, db: Session) -> None:
        self.db = db

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
