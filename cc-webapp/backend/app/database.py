"""SQLAlchemy engine and session configuration."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Base class for all models
Base = declarative_base()

# Update this to use PostgreSQL by default
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./dev.db"  # 테스트를 위해 dev.db 사용
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

def get_db():
    db = SessionLocal()
    print(f"Using DB: {engine.url}")
    try:
        yield db
    finally:
        db.close()
