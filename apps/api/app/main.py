from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.routers.auth import router as auth_router
from app.routers.sessions import router as sessions_router
from app.routers.reviews import router as reviews_router
from app.routers.audio import router as audio_router
from app.routers.placement import router as placement_router
from app.routers.rankings import router as rankings_router
from app.routers.saved_phrases import router as saved_phrases_router
from app.services.ai import initialize_providers

# ロギング設定を初期化
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI English Learning App API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# リクエストロギングミドルウェア
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth")
app.include_router(sessions_router, prefix=f"{settings.API_V1_STR}/sessions", tags=["sessions"])
app.include_router(reviews_router, prefix=f"{settings.API_V1_STR}/reviews", tags=["reviews"])
app.include_router(audio_router, prefix=f"{settings.API_V1_STR}/audio", tags=["audio"])
app.include_router(placement_router, prefix=f"{settings.API_V1_STR}/placement")
app.include_router(rankings_router, prefix=f"{settings.API_V1_STR}", tags=["rankings"])
app.include_router(saved_phrases_router, prefix=f"{settings.API_V1_STR}/saved-phrases", tags=["saved-phrases"])


@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up", extra={"environment": settings.ENVIRONMENT})
    initialize_providers()
    logger.info("AI providers initialized")


@app.get("/")
async def root():
    return {
        "message": "AI English Learning App API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-english-learning-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
