from sqlalchemy.orm import Session
from app.models import User, AgeVerificationRecord
from app.schemas import AgeVerificationRequest # AgeVerificationResponse is not directly used here but good to note
from datetime import datetime
from typing import Optional # Added for the commented out method

class AgeVerificationService:
    def __init__(self, db: Session):
        self.db = db

    def record_verification(self, user_id: int, verification_request: AgeVerificationRequest) -> AgeVerificationRecord | None:
        '''
        Records an age verification attempt.
        'verification_data' in AgeVerificationRequest should be handled carefully,
        potentially with encryption if it contains sensitive PII (though encryption logic
        is outside the scope of this immediate step and would be a separate utility).
        For now, it's stored as JSONB.
        '''
        # Potentially check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            # Or raise an exception
            return None

        # For this example, we assume the request directly translates to a record.
        # In a real system, 'is_valid' might be set by an asynchronous process or callback
        # after actual verification (e.g. by a third-party service).
        # Here, we'll just record it as pending or directly valid based on input/logic.        # Simple logic: if method is "document", assume it needs manual review (is_valid=False initially)
        # Otherwise, for "phone", "ipin", assume it's auto-validated (is_valid=True) for this example.
        is_valid_initial = verification_request.verification_method not in ["document"]

        # Build verification data based on available fields
        verification_data = {}
        if verification_request.document_type:
            verification_data["document_type"] = verification_request.document_type
        if verification_request.phone_number:
            verification_data["phone_number"] = verification_request.phone_number

        db_record = AgeVerificationRecord(
            user_id=user_id,
            verification_method=verification_request.verification_method,
            verified_at=datetime.utcnow(), # Or this could be None until actually verified
            verification_data=verification_data, # Stored as JSON
            is_valid=is_valid_initial # Example: default to True, or set based on method
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def get_verification_status(self, user_id: int) -> AgeVerificationRecord | None:
        '''
        Retrieves the latest valid age verification record for a user.
        '''
        return self.db.query(AgeVerificationRecord)\
            .filter(AgeVerificationRecord.user_id == user_id, AgeVerificationRecord.is_valid == True)\
            .order_by(AgeVerificationRecord.verified_at.desc())\
            .first()

    def is_user_age_verified(self, user_id: int) -> bool:
        '''
        Checks if a user has a valid age verification record.
        '''
        return self.get_verification_status(user_id) is not None

    # Potentially, a method to update verification status if an async process is involved
    # def update_verification_status(self, record_id: int, is_valid: bool, verification_data_update: Optional[dict] = None) -> AgeVerificationRecord | None:
    #     record = self.db.query(AgeVerificationRecord).filter(AgeVerificationRecord.id == record_id).first()
    #     if record:
    #         record.is_valid = is_valid
    #         record.verified_at = datetime.utcnow() # Update timestamp
    #         if verification_data_update:
    #             # For JSONB, direct update might not work like this, may need to merge dicts
    #             # record.verification_data.update(verification_data_update)
    #             # A safer way for JSONB might be:
    #             if record.verification_data is None:
    #                 record.verification_data = verification_data_update
    #             elif isinstance(record.verification_data, dict) and isinstance(verification_data_update, dict):
    #                 record.verification_data = {**record.verification_data, **verification_data_update}
    #             else:
    #                 # Handle other types or raise error if types are incompatible
    #                 record.verification_data = verification_data_update # Fallback or error
    #             # Mark as modified if necessary, though SQLAlchemy usually detects changes to mutable types
    #             # from sqlalchemy.orm.attributes import flag_modified
    #             # flag_modified(record, "verification_data")
    #         self.db.commit()
    #         self.db.refresh(record)
    #     return record
