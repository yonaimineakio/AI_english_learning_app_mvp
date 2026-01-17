from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Tuple
from datetime import datetime, timedelta, timezone
import pytz
import logging

from models.database.models import User, Session as SessionModel, DifficultyLevel

logger = logging.getLogger(__name__)

# ポイント設定
POINTS_PER_ROUND = 10
POINTS_SESSION_COMPLETE_BONUS = 50

# 難易度ボーナス倍率
DIFFICULTY_MULTIPLIERS = {
    "beginner": 1.0,
    "intermediate": 1.2,
    "advanced": 1.5,
}

# ストリークボーナス（連続日数に応じた追加ボーナス率）
STREAK_BONUSES = {
    3: 0.10,  # 3日連続: +10%
    7: 0.20,  # 7日連続: +20%
    14: 0.30,  # 14日連続: +30%
}


class PointService:
    """ポイント計算・付与サービス"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_round_points(
        self,
        difficulty: str,
        current_streak: int,
    ) -> int:
        """
        ラウンド完了時のポイントを計算する

        Args:
            difficulty: 難易度 ("beginner", "intermediate", "advanced")
            current_streak: 現在の連続学習日数

        Returns:
            int: 獲得ポイント
        """
        # 基本ポイント
        base_points = POINTS_PER_ROUND

        # 難易度ボーナス
        multiplier = DIFFICULTY_MULTIPLIERS.get(difficulty.lower(), 1.0)
        points = int(base_points * multiplier)

        # ストリークボーナス（最大の適用可能なボーナスを適用）
        streak_bonus_rate = 0.0
        for streak_days, bonus_rate in sorted(STREAK_BONUSES.items(), reverse=True):
            if current_streak >= streak_days:
                streak_bonus_rate = bonus_rate
                break

        if streak_bonus_rate > 0:
            bonus_points = int(points * streak_bonus_rate)
            points += bonus_points
            logger.debug(
                f"Applied streak bonus: {streak_bonus_rate * 100}% "
                f"(streak: {current_streak} days)"
            )

        return points

    def calculate_session_completion_points(
        self,
        difficulty: str,
        current_streak: int,
    ) -> int:
        """
        セッション完了時のボーナスポイントを計算する

        Args:
            difficulty: 難易度
            current_streak: 現在の連続学習日数

        Returns:
            int: 獲得ポイント
        """
        # 基本ボーナス
        base_bonus = POINTS_SESSION_COMPLETE_BONUS

        # 難易度ボーナス
        multiplier = DIFFICULTY_MULTIPLIERS.get(difficulty.lower(), 1.0)
        points = int(base_bonus * multiplier)

        # ストリークボーナス
        streak_bonus_rate = 0.0
        for streak_days, bonus_rate in sorted(STREAK_BONUSES.items(), reverse=True):
            if current_streak >= streak_days:
                streak_bonus_rate = bonus_rate
                break

        if streak_bonus_rate > 0:
            bonus_points = int(points * streak_bonus_rate)
            points += bonus_points

        return points

    def award_round_points(
        self,
        user_id: int,
        difficulty: str,
    ) -> int:
        """
        ラウンド完了時にポイントを付与する

        Args:
            user_id: ユーザーID
            difficulty: 難易度

        Returns:
            int: 付与されたポイント
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User {user_id} not found for point award")
            return 0

        current_streak = user.current_streak or 0
        points = self.calculate_round_points(difficulty, current_streak)

        user.total_points = (user.total_points or 0) + points
        self.db.commit()
        self.db.refresh(user)

        logger.info(
            f"Awarded {points} points to user {user_id} "
            f"(round completion, difficulty: {difficulty}, streak: {current_streak})"
        )

        return points

    def award_session_completion_points(
        self,
        user_id: int,
        difficulty: str,
    ) -> int:
        """
        セッション完了時にポイントを付与する

        Args:
            user_id: ユーザーID
            difficulty: 難易度

        Returns:
            int: 付与されたポイント
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User {user_id} not found for point award")
            return 0

        current_streak = user.current_streak or 0
        points = self.calculate_session_completion_points(difficulty, current_streak)

        user.total_points = (user.total_points or 0) + points
        self.db.commit()
        self.db.refresh(user)

        logger.info(
            f"Awarded {points} points to user {user_id} "
            f"(session completion, difficulty: {difficulty}, streak: {current_streak})"
        )

        return points

    def get_user_points_summary(self, user_id: int) -> Tuple[int, int, int]:
        """
        ユーザーのポイントサマリーを取得する

        Args:
            user_id: ユーザーID

        Returns:
            Tuple[int, int, int]: (total_points, points_this_week, points_today)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        total_points = user.total_points or 0

        # 今週のポイントを計算（JST基準）
        jst = pytz.timezone("Asia/Tokyo")
        now_jst = datetime.now(jst)
        week_start = (now_jst - timedelta(days=now_jst.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        week_start_utc = week_start.astimezone(timezone.utc)

        # 今日のポイントを計算
        today_start = now_jst.replace(hour=0, minute=0, second=0, microsecond=0)
        today_start_utc = today_start.astimezone(timezone.utc)

        # 今週のセッションからポイントを計算
        # 注: 実際のポイント履歴がないため、セッション完了時刻から推定
        # MVPでは簡易実装として、セッション完了数をベースに推定
        sessions_this_week = (
            self.db.query(SessionModel)
            .filter(
                and_(
                    SessionModel.user_id == user_id,
                    SessionModel.ended_at.is_not(None),
                    SessionModel.ended_at >= week_start_utc,
                )
            )
            .count()
        )

        sessions_today = (
            self.db.query(SessionModel)
            .filter(
                and_(
                    SessionModel.user_id == user_id,
                    SessionModel.ended_at.is_not(None),
                    SessionModel.ended_at >= today_start_utc,
                )
            )
            .count()
        )

        # 簡易計算: セッションあたり平均100ポイントと仮定
        # 実際の実装ではポイント履歴テーブルを作成することを推奨
        points_this_week = sessions_this_week * 100
        points_today = sessions_today * 100

        return total_points, points_this_week, points_today
