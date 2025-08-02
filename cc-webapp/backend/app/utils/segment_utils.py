from sqlalchemy.orm import Session
import logging
from ..services.rfm_service import RFMService

logger = logging.getLogger(__name__)

def compute_rfm_and_update_segments(db: Session):
    """
    Initializes RFMService and runs the segment update process for all users.
    This function is called by the APScheduler job.
    """
    try:
        rfm_service = RFMService(db=db)
        rfm_service.update_all_user_segments()
    except Exception as e:
        logger.error(f"An error occurred during the RFM update job: {e}", exc_info=True)
        # Depending on desired reliability, you might want to add retry logic here
        # or more specific error handling.
        pass
