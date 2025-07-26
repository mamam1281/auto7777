from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, UserActivity, Reward
from passlib.context import CryptContext

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_data():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Clear existing data
    db.query(Reward).delete()
    db.query(UserActivity).delete()
    db.query(User).delete()
    
    # Create test users
    users = [
        User(
            site_id="admin1",
            nickname="Admin User",
            phone_number="1234567890",
            password_hash=pwd_context.hash("admin123"),
            invite_code="ADMIN1",
            cyber_token_balance=10000,
            rank="ADMIN"
        ),
        User(
            site_id="user1",
            nickname="Regular User",
            phone_number="0987654321",
            password_hash=pwd_context.hash("user123"),
            invite_code="USER01",
            cyber_token_balance=500,
            rank="STANDARD"
        ),
        User(
            site_id="vip1",
            nickname="VIP User",
            phone_number="5555555555",
            password_hash=pwd_context.hash("vip123"),
            invite_code="VIP001",
            cyber_token_balance=2000,
            rank="PREMIUM"
        ),
    ]
    
    db.add_all(users)
    db.commit()
    
    # Refresh to get IDs
    for user in users:
        db.refresh(user)
    
    # Add some activities
    activities = [
        UserActivity(
            user_id=users[1].id,
            activity_type="LOGIN",
            details="User logged in"
        ),
        UserActivity(
            user_id=users[1].id,
            activity_type="GAME_PLAYED",
            details="Played Slot Machine"
        ),
        UserActivity(
            user_id=users[2].id,
            activity_type="PURCHASE",
            details="Purchased 1000 tokens"
        ),
    ]
    
    db.add_all(activities)
    db.commit()
    
    # Add some rewards
    rewards = [
        Reward(
            user_id=users[1].id,
            reward_type="BONUS",
            amount=100,
            reason="Welcome bonus",
            admin_id=users[0].id
        ),
        Reward(
            user_id=users[2].id,
            reward_type="VIP",
            amount=500,
            reason="VIP status reward",
            admin_id=users[0].id
        ),
    ]
    
    db.add_all(rewards)
    db.commit()
    
    db.close()
    
    print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data()
