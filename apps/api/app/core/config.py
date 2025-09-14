from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI English Learning App"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # AI Service
    OPENAI_API_KEY: Optional[str] = None
    
    # Timezone
    TIMEZONE: str = "Asia/Tokyo"
    
    # Debug
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
