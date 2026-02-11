"""evaluate_and_update の完了判定ロジックをテストする。

完了条件: Speaking 100 点 AND Listening 100 点
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database.models import Base, ReviewItem, User
from app.services.review.review_service import ReviewService


@pytest.fixture()
def db_session():
    """テスト用のインメモリ SQLite セッションを作成する。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture()
def user(db_session):
    """テスト用ユーザーを作成する。"""
    u = User(
        id="test-user-001",
        sub="test-sub-001",
        name="Test User",
        email="test@example.com",
    )
    db_session.add(u)
    db_session.commit()
    return u


@pytest.fixture()
def review_item(db_session, user):
    """テスト用の復習アイテムを作成する。"""
    item = ReviewItem(
        user_id=user.id,
        phrase="I would like to check in.",
        explanation="ホテルチェックイン時の表現",
        due_at=datetime.utcnow() - timedelta(hours=1),
        is_completed=False,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


class TestEvaluateAndUpdate:
    """evaluate_and_update の完了判定テスト"""

    def test_both_100_marks_completed(self, db_session, user, review_item):
        """Speaking 100 + Listening 100 → 完了"""
        service = ReviewService(db_session)

        # Speaking 評価（DB 変更なし）
        item, is_completed, next_due = service.evaluate_and_update(
            user_id=user.id,
            item_id=review_item.id,
            question_type="speaking",
            score=100,
            is_correct=True,
        )
        assert not is_completed
        assert item.is_completed is False

        # Listening 評価（両方 100 → 完了）
        item, is_completed, next_due = service.evaluate_and_update(
            user_id=user.id,
            item_id=review_item.id,
            question_type="listening",
            score=100,
            is_correct=True,
            speaking_score=100,
        )
        assert is_completed is True
        assert item.is_completed is True
        assert item.completed_at is not None
        assert next_due is None

    def test_speaking_100_listening_partial_reschedules(
        self, db_session, user, review_item
    ):
        """Speaking 100 + Listening < 100 → リスケジュール"""
        service = ReviewService(db_session)

        item, is_completed, next_due = service.evaluate_and_update(
            user_id=user.id,
            item_id=review_item.id,
            question_type="listening",
            score=60,
            is_correct=False,
            speaking_score=100,
        )
        assert is_completed is False
        assert item.is_completed is False
        assert next_due is not None
        assert item.completed_at is None

    def test_speaking_partial_listening_100_reschedules(
        self, db_session, user, review_item
    ):
        """Speaking < 100 + Listening 100 → リスケジュール"""
        service = ReviewService(db_session)

        item, is_completed, next_due = service.evaluate_and_update(
            user_id=user.id,
            item_id=review_item.id,
            question_type="listening",
            score=100,
            is_correct=True,
            speaking_score=80,
        )
        assert is_completed is False
        assert item.is_completed is False
        assert next_due is not None

    def test_both_partial_reschedules(self, db_session, user, review_item):
        """Speaking < 100 + Listening < 100 → リスケジュール"""
        service = ReviewService(db_session)

        item, is_completed, next_due = service.evaluate_and_update(
            user_id=user.id,
            item_id=review_item.id,
            question_type="listening",
            score=70,
            is_correct=False,
            speaking_score=80,
        )
        assert is_completed is False
        assert item.is_completed is False
        assert next_due is not None

    def test_speaking_does_not_modify_db(self, db_session, user, review_item):
        """Speaking 評価時は is_completed / due_at を変更しない"""
        service = ReviewService(db_session)
        original_due = review_item.due_at

        item, is_completed, next_due = service.evaluate_and_update(
            user_id=user.id,
            item_id=review_item.id,
            question_type="speaking",
            score=50,
            is_correct=False,
        )
        assert is_completed is False
        assert item.is_completed is False
        assert item.due_at == original_due
        assert next_due is None

    def test_speaking_score_none_defaults_to_not_complete(
        self, db_session, user, review_item
    ):
        """speaking_score が None の場合、Listening 100 でも完了しない"""
        service = ReviewService(db_session)

        item, is_completed, next_due = service.evaluate_and_update(
            user_id=user.id,
            item_id=review_item.id,
            question_type="listening",
            score=100,
            is_correct=True,
            speaking_score=None,
        )
        assert is_completed is False
        assert item.is_completed is False
        assert next_due is not None


class TestGetDueItemsSortOrder:
    """get_due_items のソート順テスト: 未完了優先 + created_at DESC"""

    def test_incomplete_items_come_first(self, db_session, user):
        """未完了アイテムが完了アイテムより先に表示される"""
        service = ReviewService(db_session)
        now = datetime.utcnow()

        # 完了アイテム（古い）
        completed = ReviewItem(
            user_id=user.id,
            phrase="completed phrase",
            explanation="done",
            due_at=now - timedelta(days=2),
            is_completed=True,
            completed_at=now - timedelta(days=1),
            created_at=now - timedelta(days=3),
        )
        # 未完了アイテム（新しい）
        incomplete = ReviewItem(
            user_id=user.id,
            phrase="incomplete phrase",
            explanation="todo",
            due_at=now - timedelta(hours=1),
            is_completed=False,
            created_at=now - timedelta(days=1),
        )
        db_session.add_all([completed, incomplete])
        db_session.commit()

        items = service.get_due_items(user.id)
        assert len(items) == 2
        assert items[0].is_completed is False
        assert items[1].is_completed is True

    def test_same_status_sorted_by_created_at_desc(self, db_session, user):
        """同じステータス内では created_at の降順"""
        service = ReviewService(db_session)
        now = datetime.utcnow()

        older = ReviewItem(
            user_id=user.id,
            phrase="older",
            explanation="older item",
            due_at=now,
            is_completed=False,
            created_at=now - timedelta(days=5),
        )
        newer = ReviewItem(
            user_id=user.id,
            phrase="newer",
            explanation="newer item",
            due_at=now,
            is_completed=False,
            created_at=now - timedelta(days=1),
        )
        db_session.add_all([older, newer])
        db_session.commit()

        items = service.get_due_items(user.id)
        assert len(items) == 2
        assert items[0].phrase == "newer"
        assert items[1].phrase == "older"
