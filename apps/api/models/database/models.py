from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class ScenarioCategory(str, enum.Enum):
    TRAVEL = "travel"
    BUSINESS = "business"
    DAILY = "daily"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SessionMode(str, enum.Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    CUSTOM = "custom"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    sub = Column(String(255), unique=True, index=True, nullable=False)  # Auth0 sub
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="user")
    review_items = relationship("ReviewItem", back_populates="user")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(ScenarioCategory), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="scenario")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    round_target = Column(Integer, nullable=False)  # 4-12 rounds
    completed_rounds = Column(Integer, default=0)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    mode = Column(SQLEnum(SessionMode), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    scenario = relationship("Scenario", back_populates="sessions")
    session_rounds = relationship("SessionRound", back_populates="session", cascade="all, delete-orphan")


class SessionRound(Base):
    __tablename__ = "session_rounds"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    round_index = Column(Integer, nullable=False)  # 1-based index
    user_input = Column(Text, nullable=False)
    ai_reply = Column(Text, nullable=False)
    feedback_short = Column(String(120), nullable=False)  # Max 120 characters
    improved_sentence = Column(Text, nullable=False)  # Single sentence
    tags = Column(JSON, nullable=True)  # Array of strings
    score_pronunciation = Column(Integer, nullable=True)  # 0-100
    score_grammar = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="session_rounds")

    # Unique constraint
    __table_args__ = (
        {"extend_existing": True}
    )


class ReviewItem(Base):
    __tablename__ = "review_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phrase = Column(Text, nullable=False)  # The phrase to review
    explanation = Column(Text, nullable=False)  # Explanation of the phrase
    due_at = Column(DateTime(timezone=True), nullable=False)  # When to show this review
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="review_items")
