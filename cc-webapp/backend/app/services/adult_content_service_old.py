"""Service for handling adult content access and unlocking."""

from typing import List, Optional, Dict, Tuple, Union
from enum import Enum, auto
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..schemas import (
    AdultContentGalleryItem,
    AdultContentDetail,
    ContentStageInfo,
    ContentUnlockRequestNew,
    ContentUnlockResponse,
    ContentPreviewResponse,
    UnlockHistoryItem,
    AccessUpgradeRequest,
    AccessUpgradeResponse,
    AdultContentStageBase
)
from ..models import User, AdultContent, VIPAccessLog, UserSegment, AgeVerificationRecord

logger = logging.getLogger(__name__)

class StageIndex(int, Enum):
    TEASER = 1
    BASIC = 2
    PREMIUM = 3
    VIP = 4
    PARTIAL = 5
    FULL = 6

class ContentStageEnum(str, Enum):
    TEASER = "Teaser"
    BASIC = "Basic"
    PREMIUM = "Premium"
    VIP = "VIP"
    PARTIAL = "Partial"  # For partially unlocked content
    FULL = "Full"       # For fully unlocked content

# Stage details configuration
STAGE_DETAILS = {
    ContentStageEnum.TEASER: {"cost": 0, "description": "Free preview", "index": StageIndex.TEASER, "order": StageIndex.TEASER},
    ContentStageEnum.BASIC: {"cost": 100, "description": "Basic access", "index": StageIndex.BASIC, "order": StageIndex.BASIC},
    ContentStageEnum.PREMIUM: {"cost": 500, "description": "Premium content", "index": StageIndex.PREMIUM, "order": StageIndex.PREMIUM},
    ContentStageEnum.VIP: {"cost": 1000, "description": "VIP exclusive content", "index": StageIndex.VIP, "order": StageIndex.VIP},
    ContentStageEnum.PARTIAL: {"cost": 50, "description": "Partial access", "index": StageIndex.PARTIAL, "order": StageIndex.PARTIAL},
    ContentStageEnum.FULL: {"cost": 2000, "description": "Full lifetime access", "index": StageIndex.FULL, "order": StageIndex.FULL}
}

# User segment access order configuration
USER_SEGMENT_ACCESS_ORDER = {
    "FREE": 1,    # Can access TEASER
    "BASIC": 2,   # Can access TEASER, BASIC
    "PREMIUM": 3, # Can access TEASER, BASIC, PREMIUM
    "VIP": 4,     # Can access all content levels
    "FULL": 5,    # Can access absolutely everything
    "Low": 1,     # Alias for FREE
    "Medium": 3,  # Alias for PREMIUM
    "High": 4,    # Alias for VIP
    "Whale": 5    # Alias for FULL
}

class AdultContentService:
    def __init__(
        self, 
        db: Optional[Session] = None, 
        token_service=None, 
        age_verification_service=None,
        reward_service=None
    ):
        self.db = db
        self.token_service = token_service
        self.age_verification_service = age_verification_service
        self.reward_service = reward_service

    def _get_user_segment_max_order(self, user_id: int) -> int:
        """Get maximum content order based on user segment."""
        try:
            if not self.db:
                logger.error("Database session not available")
                return USER_SEGMENT_ACCESS_ORDER["Low"]
                
            # Get user segment from database
            user_segment = self.db.query(UserSegment).filter(
                UserSegment.user_id == user_id
            ).first()
            
            if not user_segment:
                logger.warning(f"No segment found for user {user_id}, defaulting to Low")
                return USER_SEGMENT_ACCESS_ORDER["Low"]            # Extract string value from SQLAlchemy column safely
            rfm_group = getattr(user_segment, 'rfm_group', None)
            name = getattr(user_segment, 'name', None)
            segment_name = rfm_group or name or "Low"
            return USER_SEGMENT_ACCESS_ORDER.get(segment_name, USER_SEGMENT_ACCESS_ORDER["Low"])
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user segment for user {user_id}: {e}")
            return USER_SEGMENT_ACCESS_ORDER["Low"]

    def _get_user_unlocked_stage_order(self, user_id: int, content_id: int) -> int:
        """Get user's current unlock stage order for content."""
        try:
            if not self.db:
                logger.error("Database session not available")
                return StageIndex.TEASER.value
                
            # Get highest unlocked stage from VIP access logs
            highest_access = self.db.query(VIPAccessLog).filter(
                VIPAccessLog.user_id == user_id,
                VIPAccessLog.content_id == content_id
            ).order_by(VIPAccessLog.accessed_at.desc()).first()
            
            if not highest_access:
                return StageIndex.TEASER.value
                
            # Map access_tier to stage order - convert SQLAlchemy column to string
            access_tier = str(highest_access.access_tier) if highest_access.access_tier else "Teaser"
            tier_mapping = {
                "Teaser": StageIndex.TEASER.value,
                "Basic": StageIndex.BASIC.value,
                "Premium": StageIndex.PREMIUM.value,
                "VIP": StageIndex.VIP.value,
                "Partial": StageIndex.PARTIAL.value,
                "Full": StageIndex.FULL.value
            }
            
            return tier_mapping.get(access_tier, StageIndex.TEASER.value)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting unlocked stages for user {user_id}, content {content_id}: {e}")
            return StageIndex.TEASER.value

    def _get_stage_by_index(self, index: int) -> ContentStageEnum:
        """Convert stage index to enum value."""
        for stage, details in STAGE_DETAILS.items():
            if details["index"].value == index:
                return stage
        raise ValueError(f"Invalid stage index: {index}")

    def _get_index_by_stage(self, stage: Union[ContentStageEnum, str]) -> int:
        """Convert stage enum/name to index."""
        if isinstance(stage, str):
            stage = ContentStageEnum(stage)
        return STAGE_DETAILS[stage]["index"].value

    def _is_user_age_verified(self, user_id: int) -> bool:
        """Check if user is age verified."""
        try:
            if self.age_verification_service:
                return self.age_verification_service.is_user_age_verified(user_id)
                
            # Fallback to direct DB check
            if not self.db:
                return False
                
            verification = self.db.query(AgeVerificationRecord).filter(
                AgeVerificationRecord.user_id == user_id,
                AgeVerificationRecord.is_valid == True
            ).first()
            
            return verification is not None
            
        except Exception as e:
            logger.error(f"Error checking age verification for user {user_id}: {e}")
            return False

    async def get_content_details(
        self, 
        content_id: int,
        user_id: int
    ) -> Optional[AdultContentDetail]:
        """Get detailed information about specific content."""
        try:
            if not self.db:
                logger.error("Database session not available")
                return None
                
            # Check age verification first
            if not self._is_user_age_verified(user_id):
                logger.warning(f"Age verification required for user {user_id}")
                return None
                
            # Get content from database
            content = self.db.query(AdultContent).filter(
                AdultContent.id == content_id
            ).first()
            
            if not content:
                logger.warning(f"Content {content_id} not found")
                return None
                
            max_order = self._get_user_segment_max_order(user_id)
            current_stage = self._get_user_unlocked_stage_order(user_id, content_id)

            stages = [
                AdultContentStageBase(
                    stage_name=stage.value,
                    cost=STAGE_DETAILS[stage]["cost"],
                    description=STAGE_DETAILS[stage]["description"],
                    is_unlocked=STAGE_DETAILS[stage]["index"].value <= current_stage
                )
                for stage in ContentStageEnum
                if STAGE_DETAILS[stage]["index"].value <= max_order
            ]

            return AdultContentDetail(
                id=int(content.id),
                title=str(content.name),
                description=str(content.description or "No description available"),
                content_url=str(content.media_url or "https://example.com/content"),
                type=ContentStageEnum.BASIC.value,  # Default type
                unlock_level=int(content.required_segment_level),
                prerequisites=["age_verified"],
                stages=stages,
                user_current_access_level=current_stage
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting content details for content {content_id}: {e}")
            return None

    async def unlock_content_stage(
        self, 
        content_id: int,
        stage_to_unlock: Union[int, str, ContentStageEnum],
        user: User
    ) -> ContentUnlockResponse:
        """Unlock specific content stage."""
        try:
            if not self.db:
                return ContentUnlockResponse(
                    success=False,
                    status="error",
                    message="Database session not available"
                )
                
            # Check age verification
            user_id = int(user.id)
            if not self._is_user_age_verified(user_id):
                return ContentUnlockResponse(
                    success=False,
                    status="error",
                    message="Age verification required"
                )
                
            # Get content
            content = self.db.query(AdultContent).filter(
                AdultContent.id == content_id
            ).first()
            
            if not content:
                return ContentUnlockResponse(
                    success=False,
                    status="error",
                    message="Content not found"
                )
                
            # Parse stage
            if isinstance(stage_to_unlock, (str, ContentStageEnum)):
                stage_index = self._get_index_by_stage(stage_to_unlock)
            else:
                stage_index = stage_to_unlock

            stage = self._get_stage_by_index(stage_index)
            cost = STAGE_DETAILS[stage]["cost"]
            
            # Check if user has enough tokens
            user_balance = int(user.cyber_token_balance)
            if user_balance < cost:
                return ContentUnlockResponse(
                    success=False,
                    status="error",
                    message="Insufficient tokens",
                    tokens_spent=0,
                    remaining_tokens=user_balance
                )
                
            # Check segment access level
            max_order = self._get_user_segment_max_order(user_id)
            if stage_index > max_order:
                return ContentUnlockResponse(
                    success=False,
                    status="error",
                    message="Segment level too low for this content"
                )
                
            # Deduct tokens if cost > 0
            if cost > 0 and self.token_service:
                new_balance = self.token_service.deduct_tokens(user_id, cost)
                if new_balance is None:
                    return ContentUnlockResponse(
                        success=False,
                        status="error",
                        message="Failed to deduct tokens"
                    )
            else:
                new_balance = user_balance - cost
                
            # Create access log
            access_log = VIPAccessLog(
                user_id=user_id,
                content_id=content_id,
                access_tier=stage.value,
                tokens_spent=cost,
                accessed_at=datetime.utcnow()
            )
            
            self.db.add(access_log)
            self.db.commit()
            
            logger.info(f"User {user_id} unlocked stage {stage.value} for content {content_id}")

            return ContentUnlockResponse(
                success=True,
                status="success",
                content_url=str(content.media_url or "https://example.com/content"),
                message="Stage unlocked successfully",
                unlocked_stage=stage_index,
                tokens_spent=cost,
                remaining_tokens=new_balance
            )
            
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid stage unlock request: {e}")
            return ContentUnlockResponse(
                success=False,
                status="error",
                message="Invalid stage to unlock"
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error unlocking content stage: {e}")
            if self.db:
                self.db.rollback()
            return ContentUnlockResponse(
                success=False,
                status="error",
                message="Database error occurred"
            )

    async def upgrade_access_temporarily(
        self,
        request: AccessUpgradeRequest,
        user: User
    ) -> AccessUpgradeResponse:
        """Temporarily upgrade user's access level."""
        try:
            if request.requested_level <= request.current_level:
                return AccessUpgradeResponse(
                    success=False,
                    new_level=request.current_level,
                    status="error",
                    message="Requested level must be higher than current level"
                )

            # Calculate upgrade cost based on level difference
            level_diff = request.requested_level - request.current_level
            base_cost = 500
            upgrade_cost = base_cost * level_diff
            
            # Check tokens
            user_balance = int(user.cyber_token_balance)
            if user_balance < upgrade_cost:
                return AccessUpgradeResponse(
                    success=False,
                    new_level=request.current_level,
                    status="error",
                    message="Insufficient tokens for upgrade"
                )
                
            # Deduct tokens
            user_id = int(user.id)
            if self.token_service:
                new_balance = self.token_service.deduct_tokens(user_id, upgrade_cost)
                if new_balance is None:
                    return AccessUpgradeResponse(
                        success=False,
                        new_level=request.current_level,
                        status="error",
                        message="Failed to deduct tokens"
                    )

            duration = timedelta(days=request.duration_days or 30)
            valid_until = datetime.now() + duration

            # Update user segment temporarily (in real implementation, 
            # you might want a separate temporary_segment table)
            segment_names = ["FREE", "BASIC", "PREMIUM", "VIP", "FULL"]
            new_segment_name = segment_names[min(request.requested_level - 1, len(segment_names) - 1)]
            
            logger.info(f"User {user_id} upgraded access level to {request.requested_level}")

            return AccessUpgradeResponse(
                success=True,
                new_level=request.requested_level,
                status="success",
                message="Access level upgraded successfully",
                new_segment_level=request.requested_level,
                tokens_spent=upgrade_cost,
                valid_until=valid_until
            )
            
        except Exception as e:
            logger.error(f"Error upgrading access for user {user.id}: {e}")
            return AccessUpgradeResponse(
                success=False,
                new_level=request.current_level,
                status="error",
                message="Internal error during upgrade"
            )

    async def get_content_preview(
        self,
        content_id: int,
        user_id: int
    ) -> ContentPreviewResponse:
        """Get preview for content."""
        try:
            if not self.db:
                return ContentPreviewResponse(
                    id=content_id,
                    title="Preview Unavailable",
                    preview_data={"error": "Database not available"},
                    unlock_requirements={"min_level": 1, "tokens": 100},
                    preview_url="",
                    current_stage_accessed=0
                )
                
            # Get content
            content = self.db.query(AdultContent).filter(
                AdultContent.id == content_id
            ).first()
            
            if not content:
                return ContentPreviewResponse(
                    id=content_id,
                    title="Content Not Found",
                    preview_data={"error": "Content not found"},
                    unlock_requirements={"min_level": 1, "tokens": 100},
                    preview_url="",
                    current_stage_accessed=0
                )
                
            current_stage = self._get_user_unlocked_stage_order(user_id, content_id)
            
            return ContentPreviewResponse(
                id=int(content.id),
                title=str(content.name),
                preview_data={
                    "thumbnail": str(content.thumbnail_url or "https://example.com/thumb.jpg"),
                    "description": str(content.description or "")
                },
                unlock_requirements={
                    "min_level": int(content.required_segment_level), 
                    "tokens": STAGE_DETAILS[ContentStageEnum.BASIC]["cost"]
                },
                preview_url=str(content.thumbnail_url or "https://example.com/preview.jpg"),
                current_stage_accessed=current_stage
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting content preview for content {content_id}: {e}")
            return ContentPreviewResponse(
                id=content_id,
                title="Preview Error",
                preview_data={"error": "Database error"},
                unlock_requirements={"min_level": 1, "tokens": 100},
                preview_url="",
                current_stage_accessed=0
            )

    def get_content_access_level(self, user_id: int, content_id: int) -> Optional[ContentStageEnum]:
        """Get user's access level for content based on age verification, segment, and unlocks."""
        try:
            # Check age verification first
            if not self._is_user_age_verified(user_id):
                return None
            
            # Get segment and unlock levels
            segment_order = self._get_user_segment_max_order(user_id)
            unlocked_order = self._get_user_unlocked_stage_order(user_id, content_id)
            
            # Return the higher of the two
            max_order = max(segment_order, unlocked_order)
            return self._get_stage_by_index(max_order)
            
        except Exception as e:
            logger.error(f"Error getting content access level for user {user_id}, content {content_id}: {e}")
            return None

    def get_gallery_for_user(self, user_id: int) -> List[AdultContentGalleryItem]:
        """Get gallery content for user."""
        try:
            if not self.db:
                logger.error("Database session not available")
                return []
                
            # Check age verification
            if not self._is_user_age_verified(user_id):
                logger.warning(f"Age verification required for user {user_id}")
                return []
                
            # Get user's max segment order
            max_order = self._get_user_segment_max_order(user_id)
            
            # Get all content that user can access based on segment
            contents = self.db.query(AdultContent).filter(
                AdultContent.required_segment_level <= max_order
            ).all()
            
            gallery_items = []
            for content in contents:
                current_access = self._get_user_unlocked_stage_order(user_id, int(content.id))
                
                gallery_items.append(AdultContentGalleryItem(
                    id=int(content.id),
                    title=str(content.name),
                    thumbnail_url=str(content.thumbnail_url or "https://example.com/thumb.jpg"),
                    preview_text=str(content.description or "No description"),
                    is_unlocked=current_access >= StageIndex.BASIC.value,
                    unlock_cost=STAGE_DETAILS[ContentStageEnum.BASIC]["cost"],
                    user_access_level=current_access
                ))
                
            return gallery_items
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting gallery for user {user_id}: {e}")
            return []

    def get_user_unlock_history(self, user_id: int) -> List[UnlockHistoryItem]:
        """Get user's unlock history."""
        try:
            if not self.db:
                logger.error("Database session not available")
                return []
                
            # Get access logs with content details
            access_logs = self.db.query(VIPAccessLog, AdultContent).join(
                AdultContent, VIPAccessLog.content_id == AdultContent.id
            ).filter(
                VIPAccessLog.user_id == user_id
            ).order_by(
                VIPAccessLog.accessed_at.desc()
            ).all()
            
            history_items = []
            for log, content in access_logs:
                history_items.append(UnlockHistoryItem(
                    content_id=int(content.id),
                    content_title=str(content.name),
                    stage_unlocked=str(log.access_tier),
                    tokens_spent=int(log.tokens_spent or 0),
                    unlocked_at=log.accessed_at,
                    content_url=str(content.media_url or "")
                ))
                
            return history_items
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting unlock history for user {user_id}: {e}")
            return []
