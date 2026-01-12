from sqlalchemy.orm import Session

from models.database.models import User
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_app_user_id(self, app_user_id: str) -> User:
        """Get user by app_user_id (UUID string)."""
        user = self.db.query(User).filter(User.id == app_user_id).first()
        if not user:
            logger.warning(f"User with app_user_id {app_user_id} not found")
            return None
        return user
    
    def update_user_subscription(self, user_id: str, is_pro: bool) -> None:
        """Update user subscription status. user_id is UUID string."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with id {user_id} not found")
            return
        user.is_pro = is_pro
        self.db.commit()
        self.db.refresh(user)