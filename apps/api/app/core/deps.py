from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth0 import auth0_service
from models.database.models import User
from typing import Optional

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    
    # Extract token
    token = credentials.credentials
    
    # Verify Auth0 token
    payload = await auth0_service.verify_auth0_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user sub (Auth0 user ID)
    user_sub = payload.get("sub")
    if not user_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.sub == user_sub).first()
    if not user:
        # Create new user if not exists
        user_info = await auth0_service.get_user_info(token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not retrieve user information",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new user
        user = User(
            sub=user_sub,
            name=user_info.get("name", ""),
            email=user_info.get("email", "")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


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
