"""
シャドーイング機能のAPIテスト
"""

import pytest
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.routers.shadowing import router as shadowing_router
from app.core.deps import get_db, get_current_user
from models.database.models import (
    Base,
    User,
    Scenario,
    ShadowingSentence,
    UserShadowingProgress,
    ScenarioCategory,
    DifficultyLevel,
)


@pytest.fixture()
def db_session():
    """テスト用のインメモリDBセッションを作成"""
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


@pytest.fixture()
def test_user(db_session):
    """テスト用ユーザーを作成"""
    user = User(
        id="test-user-id",
        sub="test-sub",
        name="Test User",
        email="test@example.com",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def test_scenario(db_session):
    """テスト用シナリオを作成"""
    scenario = Scenario(
        id=1,
        name="空港チェックイン",
        description="空港でのチェックイン練習",
        category=ScenarioCategory.TRAVEL.value,
        difficulty=DifficultyLevel.BEGINNER.value,
        is_active=True,
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario


@pytest.fixture()
def test_shadowing_sentences(db_session, test_scenario):
    """テスト用シャドーイング文を作成"""
    sentences = [
        ShadowingSentence(
            id=1,
            scenario_id=test_scenario.id,
            key_phrase="be about to board",
            sentence_en="I'm about to board the flight.",
            sentence_ja="もうすぐ搭乗します。",
            order_index=1,
            difficulty=DifficultyLevel.BEGINNER.value,
        ),
        ShadowingSentence(
            id=2,
            scenario_id=test_scenario.id,
            key_phrase="be about to board",
            sentence_en="We're about to board, please turn off your phone.",
            sentence_ja="まもなく搭乗です、電話の電源をお切りください。",
            order_index=2,
            difficulty=DifficultyLevel.BEGINNER.value,
        ),
        ShadowingSentence(
            id=3,
            scenario_id=test_scenario.id,
            key_phrase="be supposed to check in",
            sentence_en="I'm supposed to check in at counter 5.",
            sentence_ja="5番カウンターでチェックインすることになっています。",
            order_index=3,
            difficulty=DifficultyLevel.BEGINNER.value,
        ),
    ]
    for sentence in sentences:
        db_session.add(sentence)
    db_session.commit()
    return sentences


@pytest.fixture()
def client(db_session, test_user):
    """テストクライアントを作成"""
    test_app = FastAPI()
    test_app.include_router(shadowing_router, prefix="/api/v1/shadowing")

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    def _override_get_current_user():
        return test_user

    test_app.dependency_overrides[get_db] = _override_get_db
    test_app.dependency_overrides[get_current_user] = _override_get_current_user

    with TestClient(test_app) as c:
        yield c

    test_app.dependency_overrides.clear()


class TestGetScenarioShadowing:
    """GET /shadowing/scenarios/{scenario_id} のテスト"""

    def test_get_scenario_shadowing_success(
        self, client, test_scenario, test_shadowing_sentences
    ):
        """シナリオのシャドーイング文を正常に取得できる"""
        res = client.get(f"/api/v1/shadowing/scenarios/{test_scenario.id}")

        assert res.status_code == 200
        data = res.json()

        assert data["scenario_id"] == test_scenario.id
        assert data["scenario_name"] == "空港チェックイン"
        assert data["total_sentences"] == 3
        assert data["completed_count"] == 0
        assert len(data["sentences"]) == 3

        # 順序が正しいことを確認
        assert data["sentences"][0]["order_index"] == 1
        assert data["sentences"][1]["order_index"] == 2
        assert data["sentences"][2]["order_index"] == 3

        # 最初の文の内容を確認
        first_sentence = data["sentences"][0]
        assert first_sentence["key_phrase"] == "be about to board"
        assert first_sentence["sentence_en"] == "I'm about to board the flight."
        assert first_sentence["sentence_ja"] == "もうすぐ搭乗します。"
        assert first_sentence["user_progress"] is None

    def test_get_scenario_shadowing_not_found(self, client):
        """存在しないシナリオの場合は404を返す"""
        res = client.get("/api/v1/shadowing/scenarios/9999")

        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_get_scenario_shadowing_with_progress(
        self, client, db_session, test_user, test_scenario, test_shadowing_sentences
    ):
        """ユーザーの進捗がある場合、進捗情報が含まれる"""
        # 進捗データを作成
        progress = UserShadowingProgress(
            user_id=test_user.id,
            shadowing_sentence_id=test_shadowing_sentences[0].id,
            attempt_count=3,
            best_score=85,
            is_completed=True,
            last_practiced_at=datetime.utcnow(),
        )
        db_session.add(progress)
        db_session.commit()

        res = client.get(f"/api/v1/shadowing/scenarios/{test_scenario.id}")

        assert res.status_code == 200
        data = res.json()

        assert data["completed_count"] == 1

        # 最初の文に進捗がある
        first_sentence = data["sentences"][0]
        assert first_sentence["user_progress"] is not None
        assert first_sentence["user_progress"]["attempt_count"] == 3
        assert first_sentence["user_progress"]["best_score"] == 85
        assert first_sentence["user_progress"]["is_completed"] is True


class TestRecordShadowingAttempt:
    """POST /shadowing/{sentence_id}/attempt のテスト"""

    def test_record_attempt_first_time(
        self, client, test_shadowing_sentences
    ):
        """初回の練習記録が正常に作成される"""
        sentence_id = test_shadowing_sentences[0].id
        res = client.post(
            f"/api/v1/shadowing/{sentence_id}/attempt",
            json={"score": 75},
        )

        assert res.status_code == 200
        data = res.json()

        assert data["shadowing_sentence_id"] == sentence_id
        assert data["attempt_count"] == 1
        assert data["best_score"] == 75
        assert data["is_completed"] is False
        assert data["is_new_best"] is True

    def test_record_attempt_updates_best_score(
        self, client, db_session, test_user, test_shadowing_sentences
    ):
        """より高いスコアでベストスコアが更新される"""
        sentence_id = test_shadowing_sentences[0].id

        # 既存の進捗を作成
        progress = UserShadowingProgress(
            user_id=test_user.id,
            shadowing_sentence_id=sentence_id,
            attempt_count=1,
            best_score=70,
            is_completed=False,
        )
        db_session.add(progress)
        db_session.commit()

        # より高いスコアで記録
        res = client.post(
            f"/api/v1/shadowing/{sentence_id}/attempt",
            json={"score": 85},
        )

        assert res.status_code == 200
        data = res.json()

        assert data["attempt_count"] == 2
        assert data["best_score"] == 85
        assert data["is_new_best"] is True

    def test_record_attempt_no_new_best(
        self, client, db_session, test_user, test_shadowing_sentences
    ):
        """低いスコアではベストスコアは更新されない"""
        sentence_id = test_shadowing_sentences[0].id

        # 既存の進捗を作成
        progress = UserShadowingProgress(
            user_id=test_user.id,
            shadowing_sentence_id=sentence_id,
            attempt_count=1,
            best_score=90,
            is_completed=True,
        )
        db_session.add(progress)
        db_session.commit()

        # より低いスコアで記録
        res = client.post(
            f"/api/v1/shadowing/{sentence_id}/attempt",
            json={"score": 75},
        )

        assert res.status_code == 200
        data = res.json()

        assert data["attempt_count"] == 2
        assert data["best_score"] == 90  # 変更なし
        assert data["is_new_best"] is False

    def test_record_attempt_marks_completed_at_80(
        self, client, test_shadowing_sentences
    ):
        """80点以上で完了とマークされる"""
        sentence_id = test_shadowing_sentences[0].id

        res = client.post(
            f"/api/v1/shadowing/{sentence_id}/attempt",
            json={"score": 80},
        )

        assert res.status_code == 200
        data = res.json()

        assert data["is_completed"] is True

    def test_record_attempt_not_completed_below_80(
        self, client, test_shadowing_sentences
    ):
        """80点未満では完了にならない"""
        sentence_id = test_shadowing_sentences[0].id

        res = client.post(
            f"/api/v1/shadowing/{sentence_id}/attempt",
            json={"score": 79},
        )

        assert res.status_code == 200
        data = res.json()

        assert data["is_completed"] is False

    def test_record_attempt_sentence_not_found(self, client):
        """存在しないシャドーイング文の場合は404を返す"""
        res = client.post(
            "/api/v1/shadowing/9999/attempt",
            json={"score": 80},
        )

        assert res.status_code == 404


class TestGetShadowingProgress:
    """GET /shadowing/progress のテスト"""

    def test_get_progress_empty(self, client, test_scenario, test_shadowing_sentences):
        """練習履歴がない場合の進捗取得"""
        res = client.get("/api/v1/shadowing/progress")

        assert res.status_code == 200
        data = res.json()

        assert data["total_scenarios"] == 1
        assert data["practiced_scenarios"] == 0
        assert data["total_sentences"] == 3
        assert data["completed_sentences"] == 0
        assert data["today_practice_count"] == 0
        assert data["recent_scenarios"] == []

    def test_get_progress_with_practice(
        self, client, db_session, test_user, test_scenario, test_shadowing_sentences
    ):
        """練習履歴がある場合の進捗取得"""
        # 進捗データを作成
        progress1 = UserShadowingProgress(
            user_id=test_user.id,
            shadowing_sentence_id=test_shadowing_sentences[0].id,
            attempt_count=3,
            best_score=85,
            is_completed=True,
            last_practiced_at=datetime.utcnow(),
        )
        progress2 = UserShadowingProgress(
            user_id=test_user.id,
            shadowing_sentence_id=test_shadowing_sentences[1].id,
            attempt_count=1,
            best_score=70,
            is_completed=False,
            last_practiced_at=datetime.utcnow(),
        )
        db_session.add(progress1)
        db_session.add(progress2)
        db_session.commit()

        res = client.get("/api/v1/shadowing/progress")

        assert res.status_code == 200
        data = res.json()

        assert data["total_scenarios"] == 1
        assert data["practiced_scenarios"] == 1
        assert data["total_sentences"] == 3
        assert data["completed_sentences"] == 1
        assert data["today_practice_count"] == 2
        assert len(data["recent_scenarios"]) == 1

        # 最近のシナリオの詳細を確認
        recent = data["recent_scenarios"][0]
        assert recent["scenario_id"] == test_scenario.id
        assert recent["scenario_name"] == "空港チェックイン"
        assert recent["total_sentences"] == 3
        assert recent["completed_sentences"] == 1
        assert recent["progress_percent"] == 33  # 1/3 = 33%


class TestGetAllScenariosWithProgress:
    """GET /shadowing/scenarios のテスト"""

    def test_get_all_scenarios(self, client, test_scenario, test_shadowing_sentences):
        """全シナリオの進捗一覧を取得"""
        res = client.get("/api/v1/shadowing/scenarios")

        assert res.status_code == 200
        data = res.json()

        assert len(data) == 1
        assert data[0]["scenario_id"] == test_scenario.id
        assert data[0]["scenario_name"] == "空港チェックイン"
        assert data[0]["total_sentences"] == 3
        assert data[0]["completed_sentences"] == 0
        assert data[0]["progress_percent"] == 0

    def test_get_scenarios_with_category_filter(
        self, client, db_session, test_scenario, test_shadowing_sentences
    ):
        """カテゴリフィルタで絞り込み"""
        # 別カテゴリのシナリオを追加
        business_scenario = Scenario(
            id=2,
            name="ビジネスミーティング",
            description="会議での会話練習",
            category=ScenarioCategory.BUSINESS.value,
            difficulty=DifficultyLevel.INTERMEDIATE.value,
            is_active=True,
        )
        db_session.add(business_scenario)
        db_session.commit()

        # travelでフィルタ
        res = client.get("/api/v1/shadowing/scenarios?category=travel")

        assert res.status_code == 200
        data = res.json()

        assert len(data) == 1
        assert data[0]["category"] == "travel"

    def test_get_scenarios_with_progress(
        self, client, db_session, test_user, test_scenario, test_shadowing_sentences
    ):
        """進捗がある場合のシナリオ一覧"""
        # 進捗データを作成
        progress = UserShadowingProgress(
            user_id=test_user.id,
            shadowing_sentence_id=test_shadowing_sentences[0].id,
            attempt_count=2,
            best_score=90,
            is_completed=True,
            last_practiced_at=datetime.utcnow(),
        )
        db_session.add(progress)
        db_session.commit()

        res = client.get("/api/v1/shadowing/scenarios")

        assert res.status_code == 200
        data = res.json()

        assert len(data) == 1
        assert data[0]["completed_sentences"] == 1
        assert data[0]["progress_percent"] == 33
        assert data[0]["last_practiced_at"] is not None
