"SQLAlchemy engine and session configuration."
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Base class for all models
Base = declarative_base()

# Update this to use auth.db for authentication
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./auth.db"  # 새로 생성한 auth.db 사용
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    # Attempt initial connection to validate URL during tests
    with engine.connect():
        pass
except Exception:
    # Fallback to local SQLite file if primary DB is unreachable
    fallback_url = "sqlite:///./fallback.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_url():
    """현재 데이터베이스 URL 반환"""
    return DATABASE_URL

def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()