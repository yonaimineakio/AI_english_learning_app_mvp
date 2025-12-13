from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime, timedelta
import pytz
import logging

from models.database.models import User, Session as SessionModel
from models.schemas.schemas import UserStatsResponse

logger = logging.getLogger(__name__)


class StreakService:
    """ストリーク（連続学習日数）管理サービス"""

    def __init__(self, db: Session):
        self.db = db

    def update_streak(self, user_id: int, activity_date: date) -> None:
        """
        ストリークを更新する
        
        Args:
            user_id: ユーザーID
            activity_date: 学習日（JST基準のdateオブジェクト）
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User {user_id} not found for streak update")
            return

        last_activity_date = user.last_activity_date

        if last_activity_date is None:
            # 初回学習
            user.current_streak = 1
            user.longest_streak = 1
            user.last_activity_date = activity_date
            logger.info(f"First learning session for user {user_id}, streak set to 1")
        elif last_activity_date == activity_date:
            # 既に今日学習済み → 変更なし
            logger.debug(f"User {user_id} already learned today, no streak update")
            return
        elif last_activity_date == activity_date - timedelta(days=1):
            # 昨日学習 → 連続継続
            user.current_streak += 1
            user.last_activity_date = activity_date
            # 最長記録を更新
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
            logger.info(
                f"User {user_id} streak continued: {user.current_streak} days"
            )
        else:
            # 2日以上空いている → リセット
            user.current_streak = 1
            user.last_activity_date = activity_date
            logger.info(
                f"User {user_id} streak reset to 1 (last activity: {last_activity_date})"
            )

        self.db.commit()
        self.db.refresh(user)

    def get_user_stats(self, user_id: int) -> UserStatsResponse:
        """
        ユーザー統計情報を取得する
        
        Args:
            user_id: ユーザーID
            
        Returns:
            UserStatsResponse: ユーザー統計情報
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # セッション数の集計
        total_sessions = (
            self.db.query(SessionModel)
            .filter(
                SessionModel.user_id == user_id,
                SessionModel.ended_at.is_not(None),
            )
            .count()
        )

        # ラウンド数の集計
        total_rounds_result = (
            self.db.query(func.sum(SessionModel.completed_rounds))
            .filter(
                SessionModel.user_id == user_id,
                SessionModel.ended_at.is_not(None),
            )
            .scalar()
        )
        total_rounds = int(total_rounds_result) if total_rounds_result else 0

        return UserStatsResponse(
            current_streak=user.current_streak or 0,
            longest_streak=user.longest_streak or 0,
            last_activity_date=user.last_activity_date,
            total_sessions=total_sessions,
            total_rounds=total_rounds,
        )

