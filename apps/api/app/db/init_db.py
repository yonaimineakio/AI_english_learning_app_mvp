import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from sqlalchemy.orm import Session
from app.db.session import engine
from models.database.models import Base, Scenario, ScenarioCategory, DifficultyLevel
from app.db.migrations import upgrade_head


def _create_initial_scenarios(db: Session) -> None:
    """既存の初期シナリオを作成（テーブルが空の場合のみ）"""
    if db.query(Scenario).first() is not None:
        print("ℹ️  Scenarios already exist, skipping initial seed")
        return

    scenarios = [
        Scenario(
            name="Airport Check-in",
            description="Practice checking in at the airport",
            category=ScenarioCategory.TRAVEL.value,
            difficulty=DifficultyLevel.BEGINNER.value,
            is_active=True,
        ),
        Scenario(
            name="Hotel Reservation",
            description="Make a hotel reservation over the phone",
            category=ScenarioCategory.TRAVEL.value,
            difficulty=DifficultyLevel.INTERMEDIATE.value,
            is_active=True,
        ),
        Scenario(
            name="Business Meeting",
            description="Participate in a business meeting",
            category=ScenarioCategory.BUSINESS.value,
            difficulty=DifficultyLevel.INTERMEDIATE.value,
            is_active=True,
        ),
        Scenario(
            name="Job Interview",
            description="Practice for a job interview",
            category=ScenarioCategory.BUSINESS.value,
            difficulty=DifficultyLevel.ADVANCED.value,
            is_active=True,
        ),
        Scenario(
            name="Ordering Food",
            description="Order food at a restaurant",
            category=ScenarioCategory.DAILY.value,
            difficulty=DifficultyLevel.BEGINNER.value,
            is_active=True,
        ),
        Scenario(
            name="Shopping",
            description="Go shopping and ask for help",
            category=ScenarioCategory.DAILY.value,
            difficulty=DifficultyLevel.BEGINNER.value,
            is_active=True,
        ),
        Scenario(
            name="Doctor's Appointment",
            description="Visit the doctor and describe symptoms",
            category=ScenarioCategory.DAILY.value,
            difficulty=DifficultyLevel.INTERMEDIATE.value,
            is_active=True,
        ),
        Scenario(
            name="Banking",
            description="Handle banking transactions",
            category=ScenarioCategory.DAILY.value,
            difficulty=DifficultyLevel.INTERMEDIATE.value,
            is_active=True,
        ),
        Scenario(
            name="Travel Planning",
            description="Plan a trip and book activities",
            category=ScenarioCategory.TRAVEL.value,
            difficulty=DifficultyLevel.ADVANCED.value,
            is_active=True,
        ),
        Scenario(
            name="Client Presentation",
            description="Present to a client",
            category=ScenarioCategory.BUSINESS.value,
            difficulty=DifficultyLevel.ADVANCED.value,
            is_active=True,
        ),
    ]

    for scenario in scenarios:
        db.add(scenario)

    db.commit()
    print("✅ Initial scenarios created successfully")


def _ensure_issue27_additional_scenarios(db: Session) -> None:
    """Issue #27 で追加したシナリオ用のレコードを不足分だけ挿入する。

    既存DBでも安全に実行できるよう、存在チェックしてからINSERTする。
    ここでは id=11〜21 のみを対象とし、既存の 1〜10 は変更しない。
    """
    additional_scenarios = [
        # id, name, category, difficulty, description
        (
            11,
            "Customer Service Inquiry",
            ScenarioCategory.DAILY.value,
            DifficultyLevel.BEGINNER.value,
            "Ask customer service for help with a problem.",
        ),
        (
            12,
            "Cafe Small Talk",
            ScenarioCategory.DAILY.value,
            DifficultyLevel.INTERMEDIATE.value,
            "Chat with a barista at a stylish cafe.",
        ),
        (
            13,
            "Get Show Tickets",
            ScenarioCategory.DAILY.value,
            DifficultyLevel.BEGINNER.value,
            "Buy tickets for a concert or show.",
        ),
        (
            14,
            "Park Small Talk",
            ScenarioCategory.DAILY.value,
            DifficultyLevel.INTERMEDIATE.value,
            "Have a light conversation with someone in a park.",
        ),
        (
            15,
            "Reschedule a Meeting",
            ScenarioCategory.BUSINESS.value,
            DifficultyLevel.BEGINNER.value,
            "Politely ask to reschedule a meeting.",
        ),
        (
            16,
            "Schedule a Meeting",
            ScenarioCategory.BUSINESS.value,
            DifficultyLevel.INTERMEDIATE.value,
            "Set up a new meeting and agree on a time.",
        ),
        (
            17,
            "Run a Meeting",
            ScenarioCategory.BUSINESS.value,
            DifficultyLevel.ADVANCED.value,
            "Facilitate and run a business meeting.",
        ),
        (
            18,
            "Contract Negotiation",
            ScenarioCategory.BUSINESS.value,
            DifficultyLevel.ADVANCED.value,
            "Negotiate contract terms with a partner.",
        ),
        (
            19,
            "Present Customer Survey Results",
            ScenarioCategory.BUSINESS.value,
            DifficultyLevel.ADVANCED.value,
            "Present customer satisfaction survey results.",
        ),
        (
            20,
            "Apologize for Project Delay",
            ScenarioCategory.BUSINESS.value,
            DifficultyLevel.INTERMEDIATE.value,
            "Explain and apologize for a project delay.",
        ),
        (
            21,
            "Call in Sick",
            ScenarioCategory.BUSINESS.value,
            DifficultyLevel.INTERMEDIATE.value,
            "Tell your manager you are sick and need a day off.",
        ),
    ]

    created_count = 0
    for scenario_id, name, category, difficulty, description in additional_scenarios:
        exists = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if exists:
            continue
        scenario = Scenario(
            id=scenario_id,
            name=name,
            description=description,
            category=category,
            difficulty=difficulty,
            is_active=True,
        )
        db.add(scenario)
        created_count += 1

    if created_count:
        db.commit()
        print(f"✅ Issue #27 additional scenarios created: {created_count}")
    else:
        print("ℹ️  Issue #27 additional scenarios already exist, no changes")


def init_db() -> None:
    """Initialize database with tables and initial data"""
    # Always prefer Alembic for schema creation/evolution.
    # `create_all()` does not add missing columns to existing tables.
    upgrade_head()

    # Create database session
    from app.db.session import SessionLocal

    db = SessionLocal()

    try:
        _create_initial_scenarios(db)
        _ensure_issue27_additional_scenarios(db)
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
