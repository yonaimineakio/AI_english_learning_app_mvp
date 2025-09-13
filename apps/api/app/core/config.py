"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI English Learning API"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ai_english_learning"
    DATABASE_URL_SQLITE: str = "sqlite:///./ai_english_learning.db"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Timezone
    TIMEZONE: str = "Asia/Tokyo"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
