"""Application configuration module.

This module defines configuration settings for the Casino Club application.
It follows the Pydantic BaseSettings pattern for type-safe configuration
management with support for environment variables.

🔗 Integrated from: /app/core/config.py + /cc-webapp/backend/app/config.py
📅 Last updated: 2025-08-02
"""

import os
import json
from typing import List, Optional, Tuple
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Info
    app_name: str = "🎰 Casino-Club F2P API"
    app_description: str = "Interactive mini-games and token-based reward system with behavioral addiction triggers"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Legacy compatibility (from /app/core/config.py)
    APP_ENV: str = "development"
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Enhanced Security Settings
    jwt_secret: str = "dev_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60  # Extended from 30 to 60 minutes
    jwt_refresh_expire_days: int = 7
    
    # Legacy Database Support (from /app/core/config.py)
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "cc_webapp_db"
    DB_USER: str = "cc_user"
    DB_PASSWORD: str = "cc_password"
    
    @property
    def DATABASE_URL(self) -> str:
        """Legacy DATABASE_URL property for backward compatibility."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Enhanced Database Settings
    database_url: str = "postgresql://cc_user:cc_password@postgres:5432/cc_webapp_db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Redis Settings
    REDIS_HOST: str = "redis"  # Legacy compatibility
    REDIS_PORT: int = 6379      # Legacy compatibility
    redis_url: str = "redis://redis:6379/0"
    redis_expire_time: int = 3600  # 1 hour default
    
    # Kafka (optional)
    kafka_bootstrap_servers: str = "kafka:9093"
    kafka_enabled: bool = True
    
    # 🎰 Gacha System Settings (from /app/core/config.py)
    GACHA_RARITY_TABLE: Optional[str] = None
    
    def get_gacha_rarity_table(self) -> List[Tuple[str, float]]:
        """
        Parses the GACHA_RARITY_TABLE from a JSON string in env vars.
        Enhanced with dopamine-triggering probabilities.
        """
        default_table = [
            ("Legendary", 0.002),     # 0.2% - Ultra rare for maximum dopamine
            ("Epic", 0.025),          # 2.5% - Rare enough to feel special
            ("Rare", 0.15),           # 15% - Good rewards to maintain engagement
            ("Common", 0.65),         # 65% - Base rewards
            ("Near_Miss_Epic", 0.08), # 8% - Behavioral trigger
            ("Near_Miss_Legendary", 0.093), # 9.3% - Behavioral trigger
        ]
        if self.GACHA_RARITY_TABLE:
            try:
                data = json.loads(self.GACHA_RARITY_TABLE)
                return [(str(name), float(prob)) for name, prob in data]
            except (json.JSONDecodeError, TypeError):
                return default_table
        return default_table
    
    # Kafka (optional)
    kafka_bootstrap_servers: str = "kafka:9093"
    kafka_enabled: bool = True
    
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
