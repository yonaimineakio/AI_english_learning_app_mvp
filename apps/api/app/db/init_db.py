import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine
from models.database.models import User, Scenario, ScenarioCategory, DifficultyLevel


def init_db() -> None:
    """Initialize database with tables and initial data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    from app.db.session import SessionLocal
    db = SessionLocal()
    
    try:
        # Check if scenarios already exist
        if db.query(Scenario).first() is None:
            # Create initial scenarios
            scenarios = [
                Scenario(
                    name="Airport Check-in",
                    description="Practice checking in at the airport",
                    category=ScenarioCategory.TRAVEL,
                    difficulty=DifficultyLevel.BEGINNER,
                    is_active=True
                ),
                Scenario(
                    name="Hotel Reservation",
                    description="Make a hotel reservation over the phone",
                    category=ScenarioCategory.TRAVEL,
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    is_active=True
                ),
                Scenario(
                    name="Business Meeting",
                    description="Participate in a business meeting",
                    category=ScenarioCategory.BUSINESS,
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    is_active=True
                ),
                Scenario(
                    name="Job Interview",
                    description="Practice for a job interview",
                    category=ScenarioCategory.BUSINESS,
                    difficulty=DifficultyLevel.ADVANCED,
                    is_active=True
                ),
                Scenario(
                    name="Ordering Food",
                    description="Order food at a restaurant",
                    category=ScenarioCategory.DAILY,
                    difficulty=DifficultyLevel.BEGINNER,
                    is_active=True
                ),
                Scenario(
                    name="Shopping",
                    description="Go shopping and ask for help",
                    category=ScenarioCategory.DAILY,
                    difficulty=DifficultyLevel.BEGINNER,
                    is_active=True
                ),
                Scenario(
                    name="Doctor's Appointment",
                    description="Visit the doctor and describe symptoms",
                    category=ScenarioCategory.DAILY,
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    is_active=True
                ),
                Scenario(
                    name="Banking",
                    description="Handle banking transactions",
                    category=ScenarioCategory.DAILY,
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    is_active=True
                ),
                Scenario(
                    name="Travel Planning",
                    description="Plan a trip and book activities",
                    category=ScenarioCategory.TRAVEL,
                    difficulty=DifficultyLevel.ADVANCED,
                    is_active=True
                ),
                Scenario(
                    name="Client Presentation",
                    description="Present to a client",
                    category=ScenarioCategory.BUSINESS,
                    difficulty=DifficultyLevel.ADVANCED,
                    is_active=True
                )
            ]
            
            for scenario in scenarios:
                db.add(scenario)
            
            db.commit()
            print("✅ Initial scenarios created successfully")
        else:
            print("ℹ️  Scenarios already exist, skipping initialization")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
