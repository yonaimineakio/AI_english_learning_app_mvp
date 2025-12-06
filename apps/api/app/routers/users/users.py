"""Users router for user stats and profile."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.services.streak.streak_service import StreakService
from models.database.models import User, Session as SessionModel, PointHistory

router = APIRouter(tags=["users"])


class StreakInfo(BaseModel):
    """Streak information for a user."""

    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime]
    is_active_today: bool


class UserStats(BaseModel):
    """User statistics."""

    total_sessions: int
    total_rounds: int
    total_points: int
    streak: StreakInfo


class RankingEntry(BaseModel):
    """Ranking entry for a user."""

    rank: int
    user_id: int
    user_name: str
    total_points: int


class RankingResponse(BaseModel):
    """Ranking response."""

    rankings: List[RankingEntry]
    user_rank: Optional[int] = None


@router.get("/stats", response_model=UserStats)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's statistics including streak info."""
    # Check and reset streak if needed
    streak_service = StreakService(db)
    streak_info = streak_service.check_and_reset_streak(current_user)

    # Count total sessions
    total_sessions = db.query(func.count(SessionModel.id)).filter(
        SessionModel.user_id == current_user.id,
        SessionModel.ended_at.isnot(None),
    ).scalar() or 0

    # Count total rounds
    total_rounds = db.query(func.sum(SessionModel.completed_rounds)).filter(
        SessionModel.user_id == current_user.id,
        SessionModel.ended_at.isnot(None),
    ).scalar() or 0

    return UserStats(
        total_sessions=total_sessions,
        total_rounds=total_rounds,
        total_points=current_user.total_points or 0,
        streak=StreakInfo(
            current_streak=streak_info.current_streak,
            longest_streak=streak_info.longest_streak,
            last_activity_date=streak_info.last_activity_date,
            is_active_today=streak_info.is_active_today,
        ),
    )


@router.get("/ranking", response_model=RankingResponse)
def get_ranking(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get top users by points."""
    # Get top users
    top_users = (
        db.query(User)
        .filter(User.total_points > 0)
        .order_by(User.total_points.desc())
        .limit(limit)
        .all()
    )

    rankings = []
    user_rank = None

    for i, user in enumerate(top_users, 1):
        rankings.append(
            RankingEntry(
                rank=i,
                user_id=user.id,
                user_name=user.name,
                total_points=user.total_points or 0,
            )
        )
        if user.id == current_user.id:
            user_rank = i

    # If current user is not in top rankings, find their rank
    if user_rank is None and current_user.total_points and current_user.total_points > 0:
        # Count users with more points
        higher_ranked = db.query(func.count(User.id)).filter(
            User.total_points > current_user.total_points
        ).scalar() or 0
        user_rank = higher_ranked + 1

    return RankingResponse(
        rankings=rankings,
        user_rank=user_rank,
    )
