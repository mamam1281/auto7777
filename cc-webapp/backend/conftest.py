"""
Test configuration for pytest.
Sets up fixtures and configurations for testing.
"""
import pytest
import os
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry, REGISTRY
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment configuration."""
    os.environ["DISABLE_SCHEDULER"] = "1"
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
