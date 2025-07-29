"""Application configuration module.

This module defines configuration settings for the Casino Club application.
It follows the Pydantic BaseSettings pattern for type-safe configuration
management with support for environment variables.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Info
    app_name: str = "Casino Club API"
    app_description: str = "API for interactive mini-games and token-based reward system"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    
    # Security
    jwt_secret: str = "dev_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7
    
    # Database
    database_url: str = "postgresql://cc_user:cc_password@postgres:5432/cc_webapp_db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    redis_expire_time: int = 3600  # 1 hour default
    
    # Kafka (optional)
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_enabled: bool = False
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ]
    
    # API Documentation
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    enable_prometheus: bool = True
    metrics_endpoint: str = "/metrics"
    
    # Scheduler
    disable_scheduler: bool = False
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Email (optional)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Push Notifications (optional)
    firebase_credentials_path: Optional[str] = None
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v:
            raise ValueError("Database URL is required")
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance.
    
    This function can be used as a FastAPI dependency
    to inject settings into endpoint handlers.
    
    Returns:
        Settings: Application settings instance
    """
    return settings


# Database connection string fallback logic
def get_database_url() -> str:
    """Get database connection URL with fallback logic.
    
    Returns:
        str: Database connection URL
    """
    try:
        # Try primary database URL
        return settings.database_url
    except Exception:
        # Fallback to SQLite for development/testing
        fallback_url = "sqlite:///./fallback.db"
        print(f"Warning: Using fallback database: {fallback_url}")
        return fallback_url


# Environment-specific configurations
def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment.lower() in ("development", "dev", "local")


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment.lower() in ("production", "prod")


def is_testing() -> bool:
    """Check if running in testing environment."""
    return settings.environment.lower() in ("testing", "test")
