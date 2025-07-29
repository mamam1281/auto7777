import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import threading
import time

# Adjust import path if needed
import sys
sys.path.append(r'cc-webapp/backend/app')
from models import User, UserSegment, UserAction, Base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ccdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

# 1. ACID Transaction Test
def test_transaction_atomicity(db_session):
    user = User(nickname="acid_test", email="acid@test.com")
    db_session.add(user)
    db_session.commit()
    try:
        db_session.begin()
        user.nickname = "fail_update"
        db_session.add(user)
        raise Exception("Simulated failure")
        db_session.commit()
    except Exception:
        db_session.rollback()
    refreshed = db_session.query(User).filter_by(email="acid@test.com").first()
    assert refreshed.nickname == "acid_test"

# 2. Concurrency Test

def concurrent_update(session_factory, user_id, new_nickname):
    session = session_factory()
    user = session.query(User).get(user_id)
    user.nickname = new_nickname
    session.commit()
    session.close()

def test_concurrent_updates(db_session):
    user = User(nickname="concurrent", email="concurrent@test.com")
    db_session.add(user)
    db_session.commit()
    user_id = user.id
    threads = []
    for i in range(5):
        t = threading.Thread(target=concurrent_update, args=(SessionLocal, user_id, f"nick_{i}"))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    refreshed = db_session.query(User).get(user_id)
    assert refreshed.nickname.startswith("nick_")

# 3. FK Integrity Test

def test_fk_constraint(db_session):
    user = User(nickname="fk_test", email="fk@test.com")
    db_session.add(user)
    db_session.commit()
    segment = UserSegment(user_id=user.id, rfm_group="test", ltv_score=0, risk_profile="low")
    db_session.add(segment)
    db_session.commit()
    db_session.delete(user)
    db_session.commit()
    seg = db_session.query(UserSegment).filter_by(user_id=user.id).first()
    assert seg is None or seg.user_id != user.id

# 4. CRUD & Edge Case Test

def test_crud_and_edge_cases(db_session):
    # Create
    user = User(nickname="crud_test", email="crud@test.com")
    db_session.add(user)
    db_session.commit()
    # Read
    fetched = db_session.query(User).filter_by(email="crud@test.com").first()
    assert fetched is not None
    # Update
    fetched.nickname = "crud_updated"
    db_session.commit()
    updated = db_session.query(User).filter_by(email="crud@test.com").first()
    assert updated.nickname == "crud_updated"
    # Delete
    db_session.delete(updated)
    db_session.commit()
    deleted = db_session.query(User).filter_by(email="crud@test.com").first()
    assert deleted is None
    # Edge: FK violation
    with pytest.raises(Exception):
        seg = UserSegment(user_id=999999, rfm_group="fail", ltv_score=0, risk_profile="fail")
        db_session.add(seg)
        db_session.commit()
