"""
🎰 Casino-Club F2P - 설정 관리 (간소화)
=====================================
환경 변수 기반 애플리케이션 설정
"""

import os
from typing import List, Optional


class Settings:
    """간소화된 설정 클래스"""
    
    def __init__(self):
        # 기본 설정
        self.app_name = "Casino-Club F2P API"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # 보안 설정
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
        self.algorithm = "HS256"
        self.jwt_algorithm = "HS256"
        self.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        
        # 데이터베이스 설정
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
        
        # Kafka 설정 (선택적)
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        
        # 게임 설정
        self.max_daily_rewards = 5


# 전역 설정 인스턴스
settings = Settings()


def get_settings():
    """설정 인스턴스 반환"""
    return settings


def is_development():
    """개발 환경 여부 확인"""
    return settings.environment == "development"
