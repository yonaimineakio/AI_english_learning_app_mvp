import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.routers.auth import auth as auth_router_module
from app.routers.auth import router as auth_router
from models.database.models import Base, User


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


@pytest.fixture()
def client(db_session, monkeypatch):
    test_app = FastAPI()
    test_app.include_router(auth_router, prefix="/api/v1/auth")

    # Override DB dependency used by auth router module
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    test_app.dependency_overrides[auth_router_module.get_db] = _override_get_db

    # Ensure deterministic base URL in redirects
    monkeypatch.setattr(settings, "FRONTEND_BASE_URL", "http://frontend.local")

    with TestClient(test_app) as c:
        yield c

    test_app.dependency_overrides.clear()


def test_debug_true_login_redirects_to_mock_callback(client, monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", True)

    res = client.get("/api/v1/auth/login", follow_redirects=False)

    assert res.status_code in (302, 307)
    location = res.headers["location"]
    assert location.startswith("http://frontend.local/callback?")
    assert "code=mock_auth_code_" in location
    assert "state=" in location


def test_debug_true_token_exchange_returns_app_jwt_and_user(
    client, db_session, monkeypatch
):
    monkeypatch.setattr(settings, "DEBUG", True)

    res = client.post("/api/v1/auth/token", json={"code": "mock_auth_code_test"})
    assert res.status_code == 200
    data = res.json()

    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    # JWT-ish format: header.payload.signature
    assert data["access_token"].count(".") == 2

    assert data["user"]["email"] == "test@example.com"

    # User persisted in DB
    user = db_session.query(User).filter(User.sub == "mock_user_123").first()
    assert user is not None
    assert user.email == "test@example.com"


def test_debug_false_login_requires_google_oauth_config(client, monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", None)
    monkeypatch.setattr(settings, "GOOGLE_REDIRECT_URI", None)

    res = client.get("/api/v1/auth/login", follow_redirects=False)
    assert res.status_code == 500
    assert "Google OAuth is not configured" in res.text


def test_debug_false_token_rejects_mock_code(client, monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", False)

    res = client.post("/api/v1/auth/token", json={"code": "mock_auth_code_test"})
    assert res.status_code == 400
    assert "Mock auth code is only allowed" in res.text
