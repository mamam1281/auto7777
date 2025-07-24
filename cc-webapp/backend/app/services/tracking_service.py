from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import models


class TrackingService:
    def __init__(self, db: Session):
        self.db = db

    def log_site_visit(self, user_id: int, source: str) -> models.SiteVisit:
        """
        Logs a site visit for a user.
        'visit_timestamp' is handled by the model's default.
        """
        db_site_visit = models.SiteVisit(
            user_id=user_id,
            source=source,
            # visit_timestamp is automatically set by the model's default value
        )
        try:
            self.db.add(db_site_visit)
            self.db.commit()
            self.db.refresh(db_site_visit)
            return db_site_visit
        except SQLAlchemyError as e:
            # Log the error, e.g., logging.error(f"Database error in log_site_visit: {e}")
            self.db.rollback()
            # Depending on policy, might raise a custom service exception
            # For now, re-raising the original SQLAlchemyError or a generic one.
            raise # Or transform into a service-specific exception.
