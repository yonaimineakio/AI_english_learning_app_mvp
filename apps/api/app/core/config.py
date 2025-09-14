from pydantic_settings import BaseSettings
from typing import Optional, List
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
    
    # Auth0 Configuration
    AUTH0_DOMAIN: str = "your-auth0-domain.auth0.com"
    AUTH0_CLIENT_ID: str = "your-auth0-client-id"
    AUTH0_CLIENT_SECRET: str = "your-auth0-client-secret"
    AUTH0_AUDIENCE: str = "your-auth0-audience"
    AUTH0_ALGORITHM: str = "RS256"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI English Learning App"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com"
    ]
    
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
