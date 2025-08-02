import os
from pydantic_settings import BaseSettings
from typing import List, Tuple, Optional
import json

class Settings(BaseSettings):
    # Core settings
    APP_ENV: str = "development"
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # Gacha Settings
    GACHA_RARITY_TABLE: Optional[str] = None

    def get_gacha_rarity_table(self) -> List[Tuple[str, float]]:
        """
        Parses the GACHA_RARITY_TABLE from a JSON string in env vars.
        """
        default_table = [
            ("Legendary", 0.002),
            ("Epic", 0.025),
            ("Rare", 0.15),
            ("Common", 0.65),
            ("Near_Miss_Epic", 0.08),
            ("Near_Miss_Legendary", 0.093),
        ]
        if self.GACHA_RARITY_TABLE:
            try:
                data = json.loads(self.GACHA_RARITY_TABLE)
                return [(str(name), float(prob)) for name, prob in data]
            except (json.JSONDecodeError, TypeError):
                return default_table
        return default_table

    class Config:
        env_file = ".env.development"
        env_file_encoding = 'utf-8'
        # Pydantic-settings uses case_sensitive=False by default,
        # which means it will match env vars regardless of case.
        case_sensitive = False

settings = Settings()
