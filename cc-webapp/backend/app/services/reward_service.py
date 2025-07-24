from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # Import SQLAlchemyError

from app import models


class RewardService:
    def __init__(self, db: Session):
        self.db = db

    def grant_content_unlock(
        self,
        user_id: int,
        content_id: int,
        stage_name: str,
        source_description: str,
        awarded_at: datetime = None,
    ) -> models.UserReward:
        if awarded_at is None:
            awarded_at = datetime.now(timezone.utc)

        reward_value = f"{content_id}_{stage_name}"

        db_user_reward = models.UserReward(
            user_id=user_id,
            reward_type="CONTENT_UNLOCK",
            reward_value=reward_value,
            source_description=source_description,
            awarded_at=awarded_at,
        )
        try:
            self.db.add(db_user_reward)
            self.db.commit()
            self.db.refresh(db_user_reward)
            return db_user_reward
        except SQLAlchemyError as e:
            self.db.rollback()
            # Optionally log the error e
            # logging.error(f"Database error in grant_content_unlock: {e}")
            raise e
