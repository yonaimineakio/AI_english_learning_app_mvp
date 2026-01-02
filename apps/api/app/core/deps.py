from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_token
from models.database.models import User
from typing import Optional

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


def _get_or_create_dev_user(db: Session) -> User:
    dev_sub = "dev-user"
    user = db.query(User).filter(User.sub == dev_sub).first()
    if user:
        return user

    user = User(
        sub=dev_sub,
        name="Dev User",
        email="dev@example.com",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token
    token = credentials.credentials

    # まずはアプリ発行トークンを検証
    payload = verify_token(token)
    if payload:
        user_sub = payload.get("sub")
        if not user_sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter(User.sub == user_sub).first()
        if not user:
            # トークンに紐づくユーザーが存在しない場合は401を返す
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found for token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_auth(user: User = Depends(get_current_user)) -> User:
    """Require authentication (used for endpoints that need auth)"""
    return user


def require_pro_user(user: User = Depends(get_current_user)) -> User:
    """Require Pro subscription (MVP: users.is_pro flag)."""
    if not getattr(user, "is_pro", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription is required",
        )
    return user
