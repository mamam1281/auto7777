"""
Test configuration for pytest.
Sets up fixtures and configurations for testing.
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_client import CollectorRegistry, REGISTRY
from unittest.mock import patch
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["DISABLE_SCHEDULER"] = "1"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment configuration."""
    # Clear prometheus registry for tests
    try:
        # Clear existing metrics
        collectors = list(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            try:
                REGISTRY.unregister(collector)
            except KeyError:
                pass
    except Exception:
        pass


@pytest.fixture
def test_app():
    """Create a test app instance without prometheus instrumentation."""
    with patch('app.main.Instrumentator', None):
        from app.main import app
        yield app


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a SQLAlchemy engine for testing"""
    from app.database import Base
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(test_db_engine):
    """Create a session for each test"""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def client(test_app):
    """Create a test client."""
    with TestClient(test_app) as c:
        yield c


@pytest.fixture(autouse=True)
def clear_prometheus_registry():
    """Clear prometheus registry before each test."""
    # Store original registry state
    original_collectors = list(REGISTRY._collector_to_names.keys())
    
    yield
    
    # Clean up after test
    try:
        collectors = list(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            if collector not in original_collectors:
                try:
                    REGISTRY.unregister(collector)
                except (KeyError, ValueError):
                    pass
    except Exception:
        pass
