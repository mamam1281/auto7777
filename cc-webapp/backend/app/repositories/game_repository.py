"""Game state repository with PostgreSQL persistence."""

import logging
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import models

logger = logging.getLogger(__name__)

# In-memory fallbacks
_streak_cache: dict[int, int] = {}
_gacha_count_cache: dict[int, int] = {}
_gacha_history_cache: dict[int, List[str]] = {}


class GameRepository:
    """Data access layer for game state using DB."""

    def get_streak(self, user_id: int) -> int:
        """Return the current win streak for the user."""
        return _streak_cache.get(user_id, 0)

    def set_streak(self, user_id: int, value: int) -> None:
        """Persist the user's streak value."""
        _streak_cache[user_id] = value

    def get_gacha_count(self, user_id: int) -> int:
        """Get how many gacha pulls the user has performed."""
        return _gacha_count_cache.get(user_id, 0)

    def set_gacha_count(self, user_id: int, value: int) -> None:
        """Set the user's gacha pull count."""
        _gacha_count_cache[user_id] = value

    def get_gacha_history(self, user_id: int) -> List[str]:
        """Return last 10 gacha results for the user."""
        return _gacha_history_cache.get(user_id, [])

    def set_gacha_history(self, user_id: int, history: List[str]) -> None:
        """Save recent gacha history for the user."""
        _gacha_history_cache[user_id] = history

    def get_user_segment(self, db: Session, user_id: int) -> str:
        """Fetch the user's segment label from the database."""
        try:
            seg = (
                db.query(models.UserSegment)
                .filter(models.UserSegment.user_id == user_id)
                .first()
            )
            return "Low" if seg is None or seg.rfm_group is None else str(seg.rfm_group)
        except SQLAlchemyError as exc:
            logger.error("Error fetching user segment: %s", exc)
            db.rollback()
            return "Low"

    def record_action(self, db: Session, user_id: int, action_type: str, value: float) -> models.UserAction:
        """Record a user action in the database."""
        action = models.UserAction(user_id=user_id, action_type=action_type, value=value)
        try:
            db.add(action)
            db.commit()
            db.refresh(action)
            return action
        except SQLAlchemyError as exc:
            logger.error("Failed to record action: %s", exc)
            db.rollback()
            raise
