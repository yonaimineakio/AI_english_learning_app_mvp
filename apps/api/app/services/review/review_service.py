from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.database.models import ReviewItem


class ReviewService:
    """復習アイテムの取得・完了処理を担うサービス"""

    def __init__(self, db: Session):
        self.db = db

    def get_due_items(self, user_id: int, limit: int = 10) -> List[ReviewItem]:
        """現在期限切れになっている復習アイテムを取得する"""

        now = datetime.utcnow()
        return (
            self.db.query(ReviewItem)
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.is_completed.is_(False),
                ReviewItem.due_at <= now,
            )
            .order_by(ReviewItem.due_at.asc(), ReviewItem.created_at.asc())
            .limit(limit)
            .all()
        )

    def count_due_items(self, user_id: int) -> int:
        now = datetime.utcnow()
        return (
            self.db.query(func.count(ReviewItem.id))
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.is_completed.is_(False),
                ReviewItem.due_at <= now,
            )
            .scalar()
            or 0
        )

    def get_history(self, user_id: int, limit: int = 20) -> List[ReviewItem]:
        """最近完了した復習アイテム"""

        return (
            self.db.query(ReviewItem)
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.is_completed.is_(True),
                ReviewItem.completed_at.isnot(None),
            )
            .order_by(ReviewItem.completed_at.desc())
            .limit(limit)
            .all()
        )

    def complete_review_item(self, user_id: int, item_id: int, result: str) -> Tuple[ReviewItem, bool]:
        """復習結果を保存する。

        Returns:
            ReviewItem: 更新後のアイテム
            bool: 正解だった場合は True
        """

        item = (
            self.db.query(ReviewItem)
            .filter(ReviewItem.id == item_id, ReviewItem.user_id == user_id)
            .first()
        )

        if not item:
            raise ValueError("Review item not found")

        now = datetime.utcnow()
        normalized = result.lower()
        if normalized not in {"correct", "incorrect"}:
            raise ValueError("Invalid review result")

        if normalized == "correct":
            item.is_completed = True
            item.completed_at = now
        else:
            # 翌日再出題（シンプルな復習間隔）
            item.is_completed = False
            item.due_at = now + timedelta(days=1)
            item.completed_at = None

        self.db.commit()
        self.db.refresh(item)

        return item, normalized == "correct"

