from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.services.conversation.session_service import SessionService
from models.database.models import (
    Base,
    DifficultyLevel,
    ReviewItem,
    Scenario,
    ScenarioCategory,
    Session as SessionModel,
    SessionMode,
    SessionRound,
    User,
)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_session_data(db, round_count: int = 4):
    user = User(
        id="00000000-0000-0000-0000-000000000001",
        sub="sub-1",
        name="Tester",
        email="tester@example.com",
        is_pro=True,
    )
    db.add(user)

    scenario = Scenario(
        name="Airport Check-in",
        description="test",
        category=ScenarioCategory.TRAVEL,
        difficulty=DifficultyLevel.BEGINNER,
        is_active=True,
    )
    db.add(scenario)
    db.flush()

    session = SessionModel(
        user_id=user.id,
        scenario_id=scenario.id,
        custom_scenario_id=None,
        round_target=5,
        completed_rounds=min(round_count, 3),
        difficulty=DifficultyLevel.BEGINNER,
        mode=SessionMode.STANDARD,
        started_at=datetime.now(timezone.utc),
        ended_at=None,
    )
    db.add(session)
    db.flush()

    base_time = datetime(2026, 2, 1, tzinfo=timezone.utc)
    for i in range(1, round_count + 1):
        db.add(
            SessionRound(
                session_id=session.id,
                round_index=i,
                user_input=f"user-input-{i}",
                ai_reply=f"ai-reply-{i}",
                feedback_short=f"feedback-{i}",
                improved_sentence=f"improved-{i}",
                tags=["conversation"],
                created_at=base_time + timedelta(minutes=i),
            )
        )

    db.commit()
    return user, session


@pytest.mark.asyncio
async def test_end_session_persists_selected_review_items(db_session, monkeypatch):
    user, session = _seed_session_data(db_session)

    async def fake_goal_progress(_self, _session):
        return 0, 0, []

    async def fake_selector(_history):
        return [
            {
                "round_index": 2,
                "phrase": "improved-2",
                "explanation": "feedback-2",
                "reason": "学習価値が高い",
                "score": 91,
            },
            {
                "round_index": 1,
                "phrase": "improved-1",
                "explanation": "feedback-1",
                "reason": "再発しやすいミス",
                "score": 78,
            },
        ]

    monkeypatch.setattr(SessionService, "_calculate_goal_progress", fake_goal_progress)
    monkeypatch.setattr(
        "app.services.conversation.session_service.select_top_review_phrases",
        fake_selector,
    )

    service = SessionService(db_session)
    result = await service.end_session(session.id, user.id)

    stored = (
        db_session.query(ReviewItem)
        .filter(
            ReviewItem.user_id == user.id,
            ReviewItem.source_session_id == session.id,
        )
        .order_by(ReviewItem.id.asc())
        .all()
    )
    assert len(stored) == 2
    assert stored[0].source_round_index == 2
    assert stored[0].selection_reason == "学習価値が高い"
    assert stored[0].selection_score == 91
    assert result.top_phrases[0]["phrase"] == "improved-2"
    assert result.top_phrases[0]["score"] == 91


@pytest.mark.asyncio
async def test_end_session_is_idempotent_uses_stored_selection(db_session, monkeypatch):
    user, session = _seed_session_data(db_session)

    async def fake_goal_progress(_self, _session):
        return 0, 0, []

    async def first_selector(_history):
        return [
            {
                "round_index": 3,
                "phrase": "improved-3",
                "explanation": "feedback-3",
                "reason": "語順の定着",
                "score": 84,
            }
        ]

    monkeypatch.setattr(SessionService, "_calculate_goal_progress", fake_goal_progress)
    monkeypatch.setattr(
        "app.services.conversation.session_service.select_top_review_phrases",
        first_selector,
    )

    service = SessionService(db_session)
    first = await service.end_session(session.id, user.id)

    async def should_not_run(_history):
        raise AssertionError("selector should not be called for already ended session")

    monkeypatch.setattr(
        "app.services.conversation.session_service.select_top_review_phrases",
        should_not_run,
    )
    second = await service.end_session(session.id, user.id)

    assert first.top_phrases == second.top_phrases
    count = (
        db_session.query(ReviewItem)
        .filter(
            ReviewItem.user_id == user.id,
            ReviewItem.source_session_id == session.id,
        )
        .count()
    )
    assert count == 1


@pytest.mark.asyncio
async def test_end_session_falls_back_when_ai_selection_fails(db_session, monkeypatch):
    user, session = _seed_session_data(db_session, round_count=4)

    async def fake_goal_progress(_self, _session):
        return 0, 0, []

    async def failed_selector(_history):
        return None

    monkeypatch.setattr(SessionService, "_calculate_goal_progress", fake_goal_progress)
    monkeypatch.setattr(
        "app.services.conversation.session_service.select_top_review_phrases",
        failed_selector,
    )

    service = SessionService(db_session)
    result = await service.end_session(session.id, user.id)

    assert len(result.top_phrases) == 3
    assert all(item["reason"] == "fallback_latest_rounds" for item in result.top_phrases)

    stored = (
        db_session.query(ReviewItem)
        .filter(
            ReviewItem.user_id == user.id,
            ReviewItem.source_session_id == session.id,
        )
        .all()
    )
    assert len(stored) == 3
