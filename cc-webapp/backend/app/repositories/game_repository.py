import logging
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import redis

from .. import models
from ..config import get_settings

logger = logging.getLogger(__name__)

# Settings 인스턴스 가져오기
settings = get_settings()

class GameRepository:
    """Data access layer for game state using DB and Redis."""

    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Could not connect to Redis: {e}")
            self.redis_client = None

    def _get_redis_key(self, user_id: int, key_type: str) -> str:
        return f"user:{user_id}:{key_type}"

    def get_streak(self, user_id: int) -> int:
        if not self.redis_client: return 0
        key = self._get_redis_key(user_id, "streak")
        value = self.redis_client.get(key)
        return int(value) if value else 0

    def set_streak(self, user_id: int, value: int) -> None:
        if not self.redis_client: return
        key = self._get_redis_key(user_id, "streak")
        self.redis_client.set(key, value)

    def get_gacha_count(self, user_id: int) -> int:
        if not self.redis_client: return 0
        key = self._get_redis_key(user_id, "gacha_count")
        value = self.redis_client.get(key)
        return int(value) if value else 0

    def set_gacha_count(self, user_id: int, value: int) -> None:
        if not self.redis_client: return
        key = self._get_redis_key(user_id, "gacha_count")
        self.redis_client.set(key, value)

    def get_gacha_history(self, user_id: int) -> List[str]:
        if not self.redis_client: return []
        key = self._get_redis_key(user_id, "gacha_history")
        return self.redis_client.lrange(key, 0, -1)

    def set_gacha_history(self, user_id: int, history: List[str]) -> None:
        if not self.redis_client: return
        key = self._get_redis_key(user_id, "gacha_history")
        self.redis_client.delete(key) # Delete old history
        if history:
            self.redis_client.rpush(key, *history)
        self.redis_client.ltrim(key, 0, 9) # Keep only the last 10

    def get_user_segment(self, db: Session, user_id: int) -> str:
        # This logic should be in RFMService, but keeping here for now to avoid breaking dependencies
        user_segment = db.query(models.UserSegment).filter(models.UserSegment.user_id == user_id).first()
        return user_segment.rfm_group if user_segment else "Low-Value"

    def record_action(self, db: Session, user_id: int, action_type: str, action_data: str) -> models.UserAction:
        action = models.UserAction(user_id=user_id, action_type=action_type, action_data=action_data)
        db.add(action)
        db.commit()
        db.refresh(action)
        return action

    def count_daily_actions(self, db: Session, user_id: int, action_type: str) -> int:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return db.query(models.UserAction).filter(
            models.UserAction.user_id == user_id,
            models.UserAction.action_type == action_type,
            models.UserAction.created_at >= today_start
        ).count()
