"""
カスタムシナリオ（オリジナルシナリオ）機能のAPIテスト

conftest.py で CLOUD_SQL_USE_CONNECTOR=false が設定されているため、
Cloud SQL Connector は使用されません。
"""

import pytest
from datetime import datetime, date
from zoneinfo import ZoneInfo
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.routers.custom_scenarios import router as custom_scenarios_router
from app.core.deps import get_db, get_current_user
from models.database.models import (
    Base,
    User,
    CustomScenario,
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
    """テスト用ユーザー（無料プラン）を作成"""
    user = User(
        id="test-user-id",
        sub="test-sub",
        name="Test User",
        email="test@example.com",
        is_pro=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def pro_user(db_session):
    """テスト用Proユーザーを作成"""
    user = User(
        id="pro-user-id",
        sub="pro-sub",
        name="Pro User",
        email="pro@example.com",
        is_pro=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def test_custom_scenario(db_session, test_user):
    """テスト用カスタムシナリオを作成"""
    scenario = CustomScenario(
        user_id=test_user.id,
        name="カフェで注文",
        description="カフェでコーヒーを注文する",
        user_role="カフェの客",
        ai_role="カフェの店員",
        difficulty="intermediate",
        is_active=True,
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario


@pytest.fixture()
def client(db_session, test_user):
    """テストクライアントを作成（無料ユーザー）"""
    test_app = FastAPI()
    test_app.include_router(custom_scenarios_router, prefix="/api/v1/custom-scenarios")

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


@pytest.fixture()
def pro_client(db_session, pro_user):
    """テストクライアントを作成（Proユーザー）"""
    test_app = FastAPI()
    test_app.include_router(custom_scenarios_router, prefix="/api/v1/custom-scenarios")

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    def _override_get_current_user():
        return pro_user

    test_app.dependency_overrides[get_db] = _override_get_db
    test_app.dependency_overrides[get_current_user] = _override_get_current_user

    with TestClient(test_app) as c:
        yield c

    test_app.dependency_overrides.clear()


class TestGetCustomScenarioLimit:
    """GET /custom-scenarios/limit のテスト"""

    def test_free_user_limit(self, client):
        """無料ユーザーの制限情報を取得"""
        res = client.get("/api/v1/custom-scenarios/limit")

        assert res.status_code == 200
        data = res.json()

        assert data["daily_limit"] == 1
        assert data["created_today"] == 0
        assert data["remaining"] == 1
        assert data["is_pro"] is False

    def test_pro_user_limit(self, pro_client):
        """Proユーザーの制限情報を取得"""
        res = pro_client.get("/api/v1/custom-scenarios/limit")

        assert res.status_code == 200
        data = res.json()

        assert data["daily_limit"] == 5
        assert data["created_today"] == 0
        assert data["remaining"] == 5
        assert data["is_pro"] is True


class TestCreateCustomScenario:
    """POST /custom-scenarios のテスト"""

    def test_create_custom_scenario_success(self, client):
        """カスタムシナリオを正常に作成できる"""
        payload = {
            "name": "レストランで注文",
            "description": "レストランで食事を注文する",
            "user_role": "お客さん",
            "ai_role": "ウェイター",
        }

        res = client.post("/api/v1/custom-scenarios", json=payload)

        assert res.status_code == 201
        data = res.json()

        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert data["user_role"] == payload["user_role"]
        assert data["ai_role"] == payload["ai_role"]
        assert data["difficulty"] == "intermediate"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_custom_scenario_validation_error(self, client):
        """必須フィールドが欠けている場合はバリデーションエラー"""
        payload = {
            "name": "テスト",
            # description, user_role, ai_role が欠けている
        }

        res = client.post("/api/v1/custom-scenarios", json=payload)

        assert res.status_code == 422

    def test_create_custom_scenario_free_user_daily_limit(self, client, db_session, test_user):
        """無料ユーザーは1日1個までしか作成できない"""
        # 既存のシナリオを作成（本日作成）
        existing = CustomScenario(
            user_id=test_user.id,
            name="既存シナリオ",
            description="既存の説明",
            user_role="既存の役割",
            ai_role="既存のAI役割",
            difficulty="intermediate",
            is_active=True,
        )
        db_session.add(existing)
        db_session.commit()

        # 2つ目を作成しようとする
        payload = {
            "name": "新しいシナリオ",
            "description": "新しい説明",
            "user_role": "新しい役割",
            "ai_role": "新しいAI役割",
        }

        res = client.post("/api/v1/custom-scenarios", json=payload)

        assert res.status_code == 429
        assert "1日" in res.json()["detail"]


class TestListCustomScenarios:
    """GET /custom-scenarios のテスト"""

    def test_list_empty(self, client):
        """カスタムシナリオがない場合は空リストを返す"""
        res = client.get("/api/v1/custom-scenarios")

        assert res.status_code == 200
        data = res.json()

        assert data["custom_scenarios"] == []
        assert data["total_count"] == 0

    def test_list_with_scenarios(self, client, test_custom_scenario):
        """カスタムシナリオ一覧を取得"""
        res = client.get("/api/v1/custom-scenarios")

        assert res.status_code == 200
        data = res.json()

        assert len(data["custom_scenarios"]) == 1
        assert data["total_count"] == 1
        assert data["custom_scenarios"][0]["name"] == test_custom_scenario.name

    def test_list_only_own_scenarios(self, client, db_session, test_user):
        """自分のシナリオのみ取得できる"""
        # 他のユーザーのシナリオを作成
        other_user = User(
            id="other-user-id",
            sub="other-sub",
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        db_session.commit()

        other_scenario = CustomScenario(
            user_id=other_user.id,
            name="他人のシナリオ",
            description="他人の説明",
            user_role="他人の役割",
            ai_role="他人のAI役割",
        )
        db_session.add(other_scenario)

        # 自分のシナリオを作成
        own_scenario = CustomScenario(
            user_id=test_user.id,
            name="自分のシナリオ",
            description="自分の説明",
            user_role="自分の役割",
            ai_role="自分のAI役割",
        )
        db_session.add(own_scenario)
        db_session.commit()

        res = client.get("/api/v1/custom-scenarios")

        assert res.status_code == 200
        data = res.json()

        assert len(data["custom_scenarios"]) == 1
        assert data["custom_scenarios"][0]["name"] == "自分のシナリオ"


class TestGetCustomScenario:
    """GET /custom-scenarios/{id} のテスト"""

    def test_get_scenario_success(self, client, test_custom_scenario):
        """カスタムシナリオを正常に取得できる"""
        res = client.get(f"/api/v1/custom-scenarios/{test_custom_scenario.id}")

        assert res.status_code == 200
        data = res.json()

        assert data["id"] == test_custom_scenario.id
        assert data["name"] == test_custom_scenario.name

    def test_get_scenario_not_found(self, client):
        """存在しないシナリオは404を返す"""
        res = client.get("/api/v1/custom-scenarios/9999")

        assert res.status_code == 404

    def test_get_other_users_scenario_not_found(self, client, db_session):
        """他のユーザーのシナリオは取得できない"""
        # 他のユーザーのシナリオを作成
        other_user = User(
            id="other-user-id",
            sub="other-sub",
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        db_session.commit()

        other_scenario = CustomScenario(
            user_id=other_user.id,
            name="他人のシナリオ",
            description="他人の説明",
            user_role="他人の役割",
            ai_role="他人のAI役割",
        )
        db_session.add(other_scenario)
        db_session.commit()

        res = client.get(f"/api/v1/custom-scenarios/{other_scenario.id}")

        assert res.status_code == 404


class TestDeleteCustomScenario:
    """DELETE /custom-scenarios/{id} のテスト"""

    def test_delete_scenario_success(self, client, db_session, test_custom_scenario):
        """カスタムシナリオを正常に削除できる（論理削除）"""
        res = client.delete(f"/api/v1/custom-scenarios/{test_custom_scenario.id}")

        assert res.status_code == 204

        # 論理削除されたことを確認
        db_session.refresh(test_custom_scenario)
        assert test_custom_scenario.is_active is False

    def test_delete_scenario_not_found(self, client):
        """存在しないシナリオの削除は404を返す"""
        res = client.delete("/api/v1/custom-scenarios/9999")

        assert res.status_code == 404

    def test_deleted_scenario_not_in_list(self, client, db_session, test_custom_scenario):
        """削除されたシナリオは一覧に表示されない"""
        # シナリオを削除
        client.delete(f"/api/v1/custom-scenarios/{test_custom_scenario.id}")

        # 一覧を取得
        res = client.get("/api/v1/custom-scenarios")

        assert res.status_code == 200
        data = res.json()

        assert data["total_count"] == 0
        assert data["custom_scenarios"] == []


class TestProUserDailyLimit:
    """Proユーザーの日次制限テスト"""

    def test_pro_user_can_create_multiple(self, pro_client, db_session, pro_user):
        """Proユーザーは複数のシナリオを作成できる"""
        # 5つまで作成できるはず
        for i in range(5):
            payload = {
                "name": f"シナリオ{i+1}",
                "description": f"説明{i+1}",
                "user_role": f"役割{i+1}",
                "ai_role": f"AI役割{i+1}",
            }
            res = pro_client.post("/api/v1/custom-scenarios", json=payload)
            assert res.status_code == 201

        # 6つ目は作成できない
        payload = {
            "name": "シナリオ6",
            "description": "説明6",
            "user_role": "役割6",
            "ai_role": "AI役割6",
        }
        res = pro_client.post("/api/v1/custom-scenarios", json=payload)
        assert res.status_code == 429
