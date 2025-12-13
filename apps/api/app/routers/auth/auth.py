from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.deps import get_current_user, get_current_user_optional
from datetime import timedelta

from models.database.models import User
from models.schemas.schemas import User as UserSchema, UserStatsResponse
from typing import Optional
import httpx
from urllib.parse import urlencode
import secrets
import logging

from app.core.security import create_access_token


router = APIRouter(tags=["authentication"])

security = HTTPBearer()

logger = logging.getLogger(__name__)


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics including streak information"""
    from app.services.streak.streak_service import StreakService
    service = StreakService(db)
    return service.get_user_stats(current_user.id)




@router.get("/login")
async def login(
    request: Request,
    client_id: str,
    redirect_uri: Optional[str] = None,
    response_type: str = "code",
    scope: str = "openid profile email"
):
    """Initiate OAuth login flow"""

    if settings.AUTH_USE_MOCK:
        state = secrets.token_urlsafe(32)
        mock_code = f"mock_auth_code_{secrets.token_urlsafe(16)}"
        target_redirect = redirect_uri or f"{settings.FRONTEND_BASE_URL.rstrip('/')}/callback"
        redirect_url = f"{target_redirect}?code={mock_code}&state={state}"
        return RedirectResponse(url=redirect_url)

    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": response_type,
        "scope": scope,
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }

    query_string = urlencode(params)
    redirect_url = f"{authorization_url}?{query_string}"

    return RedirectResponse(url=redirect_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: Optional[str] = None,
):
    """Forward Google callback to frontend callback page"""
    target = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/callback"
    params = {"code": code}
    if state:
        params["state"] = state
    redirect_url = f"{target}?{urlencode(params)}"
    return RedirectResponse(url=redirect_url)


@router.post("/token")
async def exchange_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Exchange authorization code for tokens"""
    body = await request.json()
    code = body.get("code")

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required",
        )

    if settings.AUTH_USE_MOCK or code.startswith("mock_auth_code_"):
        mock_user_data = {
            "sub": "mock_user_123",
            "name": "Test User",
            "email": "test@example.com",
            "picture": "https://via.placeholder.com/150",
        }

        user = db.query(User).filter(User.sub == mock_user_data["sub"]).first()

        if not user:
            user = User(
                sub=mock_user_data["sub"],
                name=mock_user_data["name"],
                email=mock_user_data["email"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token({"sub": user.sub})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "picture": mock_user_data["picture"],
            },
        }

    if code.startswith("mock_auth_code_"):
        return {
            "access_token": f"mock_jwt_token_{secrets.token_urlsafe(32)}",
            "refresh_token": None,
            "token_type": "bearer",
            "expires_in": 3600,
            "id_token": None,
            "user": {
                "id": "mock",
                "name": "Mock User",
                "email": "mock@example.com",
                "picture": "https://via.placeholder.com/150",
            },
        }

    token_endpoint = "https://oauth2.googleapis.com/token"
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_endpoint,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15.0,
        )

    if token_response.status_code != 200:
        logger.error(
            "Google token exchange failed: %s", token_response.text
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange authorization code with Google",
        )

    token_data = token_response.json()
    provider_access_token = token_data.get("access_token")
    if not provider_access_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google token response missing access_token",
        )

    userinfo_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {provider_access_token}"},
            timeout=15.0,
        )

    if userinfo_response.status_code != 200:
        logger.error(
            "Google userinfo fetch failed: %s", userinfo_response.text
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch user info from Google",
        )

    profile = userinfo_response.json()
    sub = profile.get("id")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google user info missing identifier",
        )

    user = db.query(User).filter(User.sub == sub).first()
    if not user:
        user = User(
            sub=sub,
            name=profile.get("name") or profile.get("given_name") or "Google User",
            email=profile.get("email") or "",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token({"sub": user.sub})

    return {
        "access_token": access_token,
        "refresh_token": token_data.get("refresh_token"),
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in"),
        "id_token": token_data.get("id_token"),
        "provider_access_token": provider_access_token,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "picture": profile.get("picture"),
        },
    }


@router.get("/logout")
async def logout(
    request: Request,
    client_id: Optional[str] = None,
    return_to: Optional[str] = None,
):
    """Handle logout by redirecting back to frontend"""

    target = return_to or f"{settings.FRONTEND_BASE_URL.rstrip('/')}/login"

    response = RedirectResponse(url=target)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("session")

    return response


@router.get("/health")
async def auth_health():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "service": "authentication",
    }
