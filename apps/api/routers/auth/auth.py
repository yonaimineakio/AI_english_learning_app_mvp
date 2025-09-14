from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.core.auth0 import auth0_service
from models.database.models import User
from models.schemas.schemas import User as UserSchema
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication"])

security = HTTPBearer()


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/verify")
async def verify_token(
    credentials: HTTPBearer = Depends(security)
):
    """Verify Auth0 token"""
    token = credentials.credentials
    
    # Verify token
    payload = await auth0_service.verify_auth0_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "valid": True,
        "user_id": payload.get("sub"),
        "expires_at": payload.get("exp")
    }


@router.get("/userinfo")
async def get_user_info(
    credentials: HTTPBearer = Depends(security)
):
    """Get user information from Auth0"""
    token = credentials.credentials
    
    user_info = await auth0_service.get_user_info(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not retrieve user information"
        )
    
    return user_info


@router.get("/health")
async def auth_health():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "auth0_domain": auth0_service.domain
    }
