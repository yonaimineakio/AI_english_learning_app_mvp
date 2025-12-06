"""Point service for managing user points."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy.orm import Session

from models.database.models import User, PointHistory


class PointReason(str, Enum):
    """Reasons for point changes."""

    SESSION_COMPLETE = "session_complete"
    ROUND_COMPLETE = "round_complete"
    REVIEW_CORRECT = "review_correct"
    STREAK_BONUS = "streak_bonus"


# Point values for each reason
POINT_VALUES = {
    PointReason.SESSION_COMPLETE: 10,
    PointReason.ROUND_COMPLETE: 2,
    PointReason.REVIEW_CORRECT: 5,
    PointReason.STREAK_BONUS: 5,
}


@dataclass
class PointTransaction:
    """A point transaction record."""

    id: int
    points: int
    reason: str
    created_at: datetime


class PointService:
    """Service for managing user points."""

    def __init__(self, db: Session):
        self.db = db

    def add_points(
        self,
        user: User,
        reason: PointReason,
        multiplier: int = 1,
    ) -> int:
        """Add points to a user.

        Args:
            user: The user to add points to
            reason: The reason for the points
            multiplier: Multiplier for the base point value (e.g., for round count)

        Returns:
            The number of points added
        """
        base_points = POINT_VALUES.get(reason, 0)
        points = base_points * multiplier

        if points <= 0:
            return 0

        # Create history record
        history = PointHistory(
            user_id=user.id,
            points=points,
            reason=reason.value,
        )
        self.db.add(history)

        # Update user total
        user.total_points = (user.total_points or 0) + points
        self.db.add(user)

        self.db.commit()
        self.db.refresh(user)

        return points

    def award_session_points(
        self,
        user: User,
        completed_rounds: int,
        streak_days: int = 0,
    ) -> int:
        """Award points for completing a session.

        Args:
            user: The user to award points to
            completed_rounds: Number of rounds completed
            streak_days: Current streak (for bonus)

        Returns:
            Total points awarded
        """
        total_points = 0

        # Session completion bonus
        session_points = self.add_points(user, PointReason.SESSION_COMPLETE)
        total_points += session_points

        # Points per round
        if completed_rounds > 0:
            round_points = self.add_points(
                user,
                PointReason.ROUND_COMPLETE,
                multiplier=completed_rounds,
            )
            total_points += round_points

        # Streak bonus (only if streak > 1)
        if streak_days > 1:
            streak_points = self.add_points(user, PointReason.STREAK_BONUS)
            total_points += streak_points

        return total_points

    def award_review_points(self, user: User) -> int:
        """Award points for correct review answer.

        Args:
            user: The user to award points to

        Returns:
            Points awarded
        """
        return self.add_points(user, PointReason.REVIEW_CORRECT)

    def get_history(
        self,
        user_id: int,
        limit: int = 20,
    ) -> List[PointTransaction]:
        """Get point history for a user.

        Args:
            user_id: The user ID
            limit: Maximum number of records to return

        Returns:
            List of point transactions
        """
        records = (
            self.db.query(PointHistory)
            .filter(PointHistory.user_id == user_id)
            .order_by(PointHistory.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            PointTransaction(
                id=r.id,
                points=r.points,
                reason=r.reason,
                created_at=r.created_at,
            )
            for r in records
        ]
