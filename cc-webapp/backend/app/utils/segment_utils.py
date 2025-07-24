# cc-webapp/backend/app/utils/segment_utils.py
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
# Assuming models are defined in ..models
# from ..models import UserAction, UserSegment # Placeholder
# from ..database import SessionLocal # Placeholder for getting a DB session

# Placeholder models for development if actual models are not yet available
# Define these here or assume they are imported
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float #, ForeignKey
# from sqlalchemy.orm import relationship

Base = declarative_base()

class UserAction(Base): # Placeholder
    __tablename__ = "user_actions" # Match your actual table name
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True) # Should ideally be ForeignKey("users.id")
    action_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # Add a 'value' field if needed for Monetary calculation
    value = Column(Float, default=0.0)


class UserSegment(Base): # Placeholder
    __tablename__ = "user_segments" # Match your actual table name
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True) # Should ideally be ForeignKey("users.id")
    rfm_group = Column(String, index=True, nullable=True) # Nullable if user has no actions yet
    risk_profile = Column(String, index=True, nullable=True) # From previous/other logic
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add other fields as per your schema (e.g., streak_count, etc.)


# Define RFM thresholds (these should come from 02_data_personalization_en.md)
# Using placeholder values/logic here as direct doc parsing isn't feasible for the agent.
# These values represent:
# Recency: days since last action (lower is better). 'high' means very recent.
# Frequency: count of actions in last 30 days. 'high' means many actions.
# Monetary: sum of value in last 30 days. 'high' means high total value.

# Example: Score 5 (best) if recency <= 7 days, Score 3 if <= 30 days, else Score 1
RECENCY_THRESHOLDS = {'high': 7, 'mid': 30}
# Example: Score 5 if frequency >= 10 actions, Score 3 if >= 3, else Score 1
FREQUENCY_THRESHOLDS = {'high': 10, 'mid': 3}
# Example: Score 5 if monetary >= 100 units, Score 3 if >= 20, else Score 1
MONETARY_THRESHOLDS = {'high': 100, 'mid': 20}

def get_rfm_score(value, thresholds, higher_is_better=True):
    if higher_is_better:
        if value >= thresholds['high']: return 5
        if value >= thresholds['mid']: return 3
        return 1
    else: # lower is better (like recency)
        if value <= thresholds['high']: return 5 # e.g. days <= 7 is a 5
        if value <= thresholds['mid']: return 3 # e.g. days <= 30 is a 3
        return 1

def compute_rfm_and_update_segments(db: Session):
    print(f"[{datetime.utcnow()}] Starting RFM computation and segment update...")
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Query for Recency, Frequency, Monetary based on actions in the last 30 days
    rfm_data = db.query(
        UserAction.user_id,
        func.max(UserAction.timestamp).label("last_action_date"),
        func.count(UserAction.id).label("frequency"),
        func.sum(UserAction.value).label("monetary_value")
    ).filter(UserAction.timestamp >= thirty_days_ago).group_by(UserAction.user_id).all()

    if not rfm_data:
        print(f"[{datetime.utcnow()}] No user actions in the last 30 days to process for RFM.")
        return

    updated_count = 0
    created_count = 0

    for row in rfm_data:
        user_id, last_action_date, frequency, monetary_value = row
        monetary_value = monetary_value or 0.0 # Ensure monetary_value is not None

        recency_days = (datetime.utcnow() - last_action_date).days if last_action_date else 999 # Handle potential None

        r_score = get_rfm_score(recency_days, RECENCY_THRESHOLDS, higher_is_better=False)
        f_score = get_rfm_score(frequency, FREQUENCY_THRESHOLDS)
        m_score = get_rfm_score(monetary_value, MONETARY_THRESHOLDS)

        # Simplified RFM group assignment based on typical segmentation.
        # This should be replaced/refined by rules from 02_data_personalization_en.md.
        # Current logic:
        # Whale: All scores are high (>=4 based on example thresholds, let's use score 5 for very top)
        # Medium: Average or mixed scores
        # Low: All scores are low

        # Using a common approach for RFM naming:
        # Whale: R=5, F=5, M=5 (Best Customers)
        # Champions: R=5, F=4-5, M=4-5
        # Loyal Customers: F=4-5 (regardless of R, M for simplicity here, or R=3-5, M=3-5)
        # Potential Loyalists: R=3-5, F=1-3, M=1-3 (Recent, but not frequent)
        # Big Spenders: M=4-5 (regardless of R, F for simplicity here)
        # At Risk: R=1-2, F=1-2 (Low Recency, Low Frequency)
        # Hibernating: R=1-2, F=1-2 (similar to At Risk)
        # Lost: R=1, F=1 (Lowest scores)

        # Simplified to Whale, Medium, Low as per example in prompt for now
        if r_score >= 4 and f_score >= 4 and m_score >= 4 : # Example: Top tier scores
            rfm_group = "Whale"
        elif r_score >= 3 and f_score >= 3 : # Example: Mid tier (good recency and frequency)
            rfm_group = "Medium"
        else:
            rfm_group = "Low"

        # Alternative simplified logic from prompt:
        # if r_score >= 4 and f_score >= 4 and m_score >= 4: rfm_group = "Whale"
        # elif (r_score + f_score + m_score) / 3 >= 2.5: rfm_group = "Medium" # Avg score >= 2.5
        # else: rfm_group = "Low"


        # Update or Create UserSegment
        user_segment = db.query(UserSegment).filter(UserSegment.user_id == user_id).first()
        current_time = datetime.utcnow()
        if user_segment:
            user_segment.rfm_group = rfm_group
            user_segment.name = rfm_group
            user_segment.recency_score = r_score
            user_segment.frequency_score = f_score
            user_segment.monetary_score = m_score
            user_segment.last_updated = current_time
            updated_count += 1
        else:
            user_segment = UserSegment(
                user_id=user_id,
                rfm_group=rfm_group,
                name=rfm_group,
                recency_score=r_score,
                frequency_score=f_score,
                monetary_score=m_score,
                # risk_profile will be set by another process or if logic is added here
                last_updated=current_time,
            )
            db.add(user_segment)
            created_count += 1

        # print(f"User {user_id}: R={recency_days}d (Score {r_score}), F={frequency} (Score {f_score}), M={monetary_value} (Score {m_score}) -> RFM Group: {rfm_group}")

    try:
        db.commit()
        print(f"[{datetime.utcnow()}] User segments updated: {updated_count} updated, {created_count} created.")
    except Exception as e:
        db.rollback()
        print(f"[{datetime.utcnow()}] Error updating user segments: {e}")

# Example usage (for testing, not part of the final scheduler call directly)
# if __name__ == "__main__":
#     # This requires database.py to be setup and accessible
#     # from ..database import SessionLocal, engine
#     # from ..models import Base as ActualBase # Import Base from actual models.py
#     # ActualBase.metadata.create_all(bind=engine) # Create tables if not exist (for testing)
#
#     # db = SessionLocal()
#     # try:
#     #     # Add some dummy UserAction data for testing
#     #     # Example:
#     #     # db.add(UserAction(user_id=1, action_type="login", value=0, timestamp=datetime.utcnow() - timedelta(days=np.random.randint(1,60))))
#     #     # for i in range(50): # Add 50 random actions for user 1
#     #     #    db.add(UserAction(user_id=1, action_type="event", value=np.random.uniform(5,20), timestamp=datetime.utcnow() - timedelta(days=np.random.randint(1,60))))
#     #     # db.commit()
#     #     compute_rfm_and_update_segments(db)
#     # finally:
#     #     db.close()
#     pass
