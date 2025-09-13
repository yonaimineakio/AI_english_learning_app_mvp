"""
AI English Learning App API
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title="AI English Learning API",
    description="API for AI-powered English learning application",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}

# Include API routers
# from app.api.v1 import auth, sessions, reviews
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
# app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
