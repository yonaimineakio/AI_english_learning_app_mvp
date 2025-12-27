from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Auth / OAuth Configuration
    AUTH_USE_MOCK: bool = False
    GOOGLE_CLIENT_ID: str = "85372847730-vogng3qs66idtuqeaasvmmoghm9nj9k8.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = "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"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    FRONTEND_BASE_URL: str = "http://localhost:3000"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI English Learning App"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",        # iOS Simulator
        "http://172.20.10.10:8000",  # Flutter app (Mac IP)
        "http://192.168.11.7:8000",  # Flutter app (previous Mac IP)
    ]
    
    # AI Service
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    OPENAI_CHAT_COMPLETIONS_URL: Optional[str] = None

    GROQ_API_KEY: Optional[str] = None
    GROQ_CHAT_COMPLETIONS_URL: Optional[str] = None
    GROQ_MODEL_NAME: str = "openai/gpt-oss-120b"
    AI_PROVIDER_DEFAULT: str = "mock"

    # Google Cloud Speech-to-Text
    GOOGLE_CLOUD_PROJECT_ID: str = "ai-english-learning-452516"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_SPEECH_API_ENDPOINT: str = "https://speech.googleapis.com/v1/speech:recognize"
    # Google Cloud Text-to-Speech
    GOOGLE_TTS_LANGUAGE: str = "en-US"
    GOOGLE_TTS_VOICE: Optional[str] = None
    GOOGLE_TTS_SPEAKING_RATE: float = 1.0
    
    # Timezone
    TIMEZONE: str = "Asia/Tokyo"
    
    # Debug
    DEBUG: bool = True
    
    class Config:
        # .envファイルのパスを絶対パスで指定
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = True
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
