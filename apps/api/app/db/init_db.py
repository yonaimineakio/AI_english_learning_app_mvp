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


def _ensure_expanded_scenarios(db: Session) -> None:
    """日常会話・旅行カテゴリの拡張シナリオ (id=22〜61) を追加する。

    既存DBでも安全に実行できるよう、存在チェックしてからINSERTする。
    """
    expanded_scenarios = [
        # --- 日常会話 (daily) ---
        (22, "Explain Symptoms at Hospital", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Describe your symptoms to a doctor in detail."),
        (23, "Buy Medicine at Pharmacy", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Ask for appropriate medicine by explaining your symptoms."),
        (24, "Dentist Appointment", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Explain dental issues and make an appointment."),
        (25, "Ask Staff at Supermarket", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Ask about product locations and alternatives."),
        (26, "Try on Clothes", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Ask to try on clothes and request different sizes."),
        (27, "Order Haircut at Salon", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Explain your desired hairstyle to a stylist."),
        (28, "Mobile Phone Contract", ScenarioCategory.DAILY.value, DifficultyLevel.ADVANCED.value,
         "Compare plans and discuss contract terms."),
        (29, "Electronics Store Consultation", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Ask about product differences and recommendations."),
        (30, "Online Order Inquiry", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Check delivery status and request returns."),
        (31, "Apartment Hunting", ScenarioCategory.DAILY.value, DifficultyLevel.ADVANCED.value,
         "Explain your requirements and schedule viewings."),
        (32, "Moving Company Quote", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Get a quote by explaining your moving needs."),
        (33, "Call Repair Service", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Explain the problem and schedule a repair visit."),
        (34, "Greet New Neighbors", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Introduce yourself after moving in."),
        (35, "Send Package at Post Office", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Send a package and ask about delivery options."),
        (36, "Open Bank Account", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Discuss account types and required documents."),
        (37, "Find Books at Library", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Ask the librarian for help finding books."),
        (38, "Invite Friend to Dinner", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Invite a friend and suggest a restaurant."),
        (39, "Small Talk at Party", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Meet new people and find common topics."),
        (40, "Sign Up for Trial Lesson", ScenarioCategory.DAILY.value, DifficultyLevel.BEGINNER.value,
         "Ask about classes and sign up for a trial."),
        (41, "Join a Gym", ScenarioCategory.DAILY.value, DifficultyLevel.INTERMEDIATE.value,
         "Compare membership plans and sign up."),
        # --- 旅行 (travel) ---
        (42, "Request to Flight Attendant", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Ask for drinks, blankets, or seat changes."),
        (43, "Confirm Connecting Flight", ScenarioCategory.TRAVEL.value, DifficultyLevel.INTERMEDIATE.value,
         "Check connection gates and delay procedures."),
        (44, "Lost Luggage", ScenarioCategory.TRAVEL.value, DifficultyLevel.ADVANCED.value,
         "Report missing luggage and negotiate compensation."),
        (45, "Change Flight at Airport", ScenarioCategory.TRAVEL.value, DifficultyLevel.ADVANCED.value,
         "Request flight changes and discuss fees."),
        (46, "Rent a Car", ScenarioCategory.TRAVEL.value, DifficultyLevel.INTERMEDIATE.value,
         "Choose a car, insurance, and return options."),
        (47, "Buy Train/Bus Ticket", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Purchase tickets and confirm platform."),
        (48, "Hotel Room Problem", ScenarioCategory.TRAVEL.value, DifficultyLevel.INTERMEDIATE.value,
         "Report issues and request room change."),
        (49, "Order Room Service", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Order food by phone and specify preferences."),
        (50, "Request Late Checkout", ScenarioCategory.TRAVEL.value, DifficultyLevel.INTERMEDIATE.value,
         "Negotiate late checkout and ask about fees."),
        (51, "Contact Airbnb Host", ScenarioCategory.TRAVEL.value, DifficultyLevel.INTERMEDIATE.value,
         "Ask about check-in and amenities."),
        (52, "Tourist Information Center", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Get recommendations and directions."),
        (53, "Book Local Tour", ScenarioCategory.TRAVEL.value, DifficultyLevel.INTERMEDIATE.value,
         "Confirm tour details and cancellation policy."),
        (54, "Museum Questions", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Ask about tickets and audio guides."),
        (55, "Ask for Photo", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Politely ask someone to take your photo."),
        (56, "Ask Locals for Tips", ScenarioCategory.TRAVEL.value, DifficultyLevel.INTERMEDIATE.value,
         "Get restaurant and sightseeing recommendations."),
        (57, "Ask for Directions When Lost", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Ask for directions and confirm landmarks."),
        (58, "Visit Hospital Abroad", ScenarioCategory.TRAVEL.value, DifficultyLevel.ADVANCED.value,
         "Explain symptoms and show insurance documents."),
        (59, "Lost Passport", ScenarioCategory.TRAVEL.value, DifficultyLevel.ADVANCED.value,
         "Report loss and arrange replacement."),
        (60, "Currency Exchange", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Exchange money and confirm rates."),
        (61, "Souvenir Shopping", ScenarioCategory.TRAVEL.value, DifficultyLevel.BEGINNER.value,
         "Ask about souvenirs and gift wrapping."),
    ]

    created_count = 0
    for scenario_id, name, category, difficulty, description in expanded_scenarios:
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
        print(f"✅ Expanded scenarios (22-61) created: {created_count}")
    else:
        print("ℹ️  Expanded scenarios already exist, no changes")


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
        _ensure_expanded_scenarios(db)
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
