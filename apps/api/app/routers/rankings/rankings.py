from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import Literal, Optional
from datetime import datetime, timedelta, timezone
import pytz
import logging

from app.core.deps import get_db, get_current_user
from models.database.models import User, Session as SessionModel
from models.schemas.schemas import (
    UserPointsResponse,
    RankingsResponse,
    RankingEntry,
    MyRankingResponse,
)
from app.services.points.point_service import PointService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rankings"])


@router.get("/users/me/points", response_model=UserPointsResponse)
async def get_user_points(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's points summary"""
    try:
        service = PointService(db)
        total_points, points_this_week, points_today = service.get_user_points_summary(
            current_user.id
        )
        return UserPointsResponse(
            total_points=total_points,
            points_this_week=points_this_week,
            points_today=points_today,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get user points: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user points"
        )


@router.get("/rankings", response_model=RankingsResponse)
async def get_rankings(
    limit: int = Query(default=20, ge=1, le=100, description="Number of rankings to return"),
    period: Literal["all_time", "weekly", "monthly"] = Query(
        default="all_time",
        description="Ranking period"
    ),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get rankings (top N users)"""
    try:
        # 期間フィルタの設定
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        now_utc = now_jst.astimezone(timezone.utc)

        if period == "weekly":
            period_start = (now_jst - timedelta(days=now_jst.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).astimezone(timezone.utc)
        elif period == "monthly":
            period_start = now_jst.replace(day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
        else:
            period_start = None

        # ランキングクエリ
        query = db.query(User).filter(User.total_points > 0)

        # 期間フィルタ適用（all_timeの場合は全期間）
        if period_start:
            # 期間内にセッション完了したユーザーのみを対象
            user_ids_with_sessions = (
                db.query(SessionModel.user_id)
                .filter(
                    and_(
                        SessionModel.ended_at.is_not(None),
                        SessionModel.ended_at >= period_start,
                    )
                )
                .distinct()
                .subquery()
            )
            query = query.filter(User.id.in_(db.query(user_ids_with_sessions.c.user_id)))

        # ポイント順でソート
        users = query.order_by(desc(User.total_points)).limit(limit).all()

        rankings = []
        for rank, user in enumerate(users, start=1):
            rankings.append(
                RankingEntry(
                    rank=rank,
                    user_id=user.id,
                    user_name=user.name,
                    total_points=user.total_points or 0,
                    current_streak=user.current_streak or 0,
                )
            )

        # 総ユーザー数（ポイントを持っているユーザー）
        total_users = db.query(User).filter(User.total_points > 0).count()

        return RankingsResponse(
            rankings=rankings,
            total_users=total_users,
        )
    except Exception as e:
        logger.error(f"Failed to get rankings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rankings"
        )


@router.get("/rankings/me", response_model=MyRankingResponse)
async def get_my_ranking(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's ranking"""
    try:
        user_points = current_user.total_points or 0

        # 自分よりポイントが高いユーザー数をカウント
        rank = (
            db.query(func.count(User.id))
            .filter(User.total_points > user_points)
            .scalar()
        ) + 1

        # 総ユーザー数
        total_users = db.query(User).filter(User.total_points > 0).count()

        # 次のランクまでのポイント差を計算
        next_user = (
            db.query(User)
            .filter(User.total_points > user_points)
            .order_by(User.total_points.asc())
            .first()
        )
        points_to_next_rank = None
        if next_user:
            points_to_next_rank = (next_user.total_points or 0) - user_points

        return MyRankingResponse(
            rank=rank,
            total_points=user_points,
            points_to_next_rank=points_to_next_rank,
            total_users=total_users,
        )
    except Exception as e:
        logger.error(f"Failed to get my ranking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get my ranking"
        )

