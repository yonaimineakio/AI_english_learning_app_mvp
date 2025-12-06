"""Streak tracking service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from models.database.models import User


# Japan timezone offset (UTC+9)
JST_OFFSET = timedelta(hours=9)


def get_jst_date(dt: Optional[datetime] = None) -> datetime:
    """Get the date in Japan timezone (Asia/Tokyo).

    Args:
        dt: Optional datetime. If None, uses current time.

    Returns:
        Date in JST (time set to midnight)
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    jst_dt = dt + JST_OFFSET
    # Return date at midnight JST
    return jst_dt.replace(hour=0, minute=0, second=0, microsecond=0)


@dataclass
class StreakInfo:
    """Streak information for a user."""

    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime]
    is_active_today: bool


class StreakService:
    """Service for managing user streak tracking."""

    def __init__(self, db: Session):
        self.db = db

    def get_streak_info(self, user: User) -> StreakInfo:
        """Get streak information for a user.

        Args:
            user: The user to get streak info for

        Returns:
            StreakInfo with current and longest streak
        """
        today = get_jst_date()
        last_activity = user.last_activity_date

        is_active_today = False
        if last_activity:
            last_activity_jst = get_jst_date(last_activity)
            is_active_today = last_activity_jst.date() == today.date()

        return StreakInfo(
            current_streak=user.current_streak or 0,
            longest_streak=user.longest_streak or 0,
            last_activity_date=user.last_activity_date,
            is_active_today=is_active_today,
        )

    def update_streak(self, user: User) -> StreakInfo:
        """Update streak when user completes a session.

        Call this when a session is completed.

        Args:
            user: The user to update streak for

        Returns:
            Updated StreakInfo
        """
        today = get_jst_date()
        now = datetime.now(timezone.utc)

        current_streak = user.current_streak or 0
        longest_streak = user.longest_streak or 0
        last_activity = user.last_activity_date

        if last_activity is None:
            # First activity ever
            current_streak = 1
        else:
            last_activity_jst = get_jst_date(last_activity)
            days_diff = (today.date() - last_activity_jst.date()).days

            if days_diff == 0:
                # Already active today, no change to streak
                pass
            elif days_diff == 1:
                # Consecutive day - increment streak
                current_streak += 1
            else:
                # Streak broken - reset to 1
                current_streak = 1

        # Update longest streak if current is higher
        if current_streak > longest_streak:
            longest_streak = current_streak

        # Update user record
        user.current_streak = current_streak
        user.longest_streak = longest_streak
        user.last_activity_date = now

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return StreakInfo(
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_activity_date=now,
            is_active_today=True,
        )

    def check_and_reset_streak(self, user: User) -> StreakInfo:
        """Check if streak should be reset due to inactivity.

        Call this when loading user data to check for streak reset.

        Args:
            user: The user to check

        Returns:
            Updated StreakInfo (streak may be reset)
        """
        if user.last_activity_date is None:
            return StreakInfo(
                current_streak=0,
                longest_streak=0,
                last_activity_date=None,
                is_active_today=False,
            )

        today = get_jst_date()
        last_activity_jst = get_jst_date(user.last_activity_date)
        days_diff = (today.date() - last_activity_jst.date()).days

        if days_diff > 1:
            # Streak broken - reset current streak
            user.current_streak = 0
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        is_active_today = days_diff == 0

        return StreakInfo(
            current_streak=user.current_streak or 0,
            longest_streak=user.longest_streak or 0,
            last_activity_date=user.last_activity_date,
            is_active_today=is_active_today,
        )
