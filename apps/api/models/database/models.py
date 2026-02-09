from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Enum,
    Date,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class ScenarioCategory(PyEnum):
    TRAVEL = "travel"
    BUSINESS = "business"
    DAILY = "daily"


class DifficultyLevel(PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SessionMode(PyEnum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    CUSTOM = "custom"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    sub = Column(
        String(255), unique=True, index=True, nullable=False
    )  # OAuth provider sub
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Placement test / personalized learning fields
    placement_level = Column(
        Enum(DifficultyLevel, values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
    )
    placement_score = Column(Integer, nullable=True)
    placement_completed_at = Column(DateTime(timezone=True), nullable=True)

    # Streak fields
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)

    # Points fields
    total_points = Column(Integer, default=0)

    # Subscription / plan fields
    # NOTE: In MVP we gate features using this flag.
    # Later, this should be synced from RevenueCat (webhook/API) instead of manual updates.
    is_pro = Column(Boolean, default=False, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user")
    review_items = relationship("ReviewItem", back_populates="user")
    saved_phrases = relationship("SavedPhrase", back_populates="user")
    shadowing_progress = relationship("UserShadowingProgress", back_populates="user", cascade="all, delete-orphan")
    custom_scenarios = relationship("CustomScenario", back_populates="user", cascade="all, delete-orphan")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(
        Enum(ScenarioCategory, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    difficulty = Column(
        Enum(DifficultyLevel, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="scenario")
    shadowing_sentences = relationship("ShadowingSentence", back_populates="scenario", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=True)  # 通常シナリオ用
    custom_scenario_id = Column(Integer, ForeignKey("custom_scenarios.id", ondelete="SET NULL"), nullable=True)  # カスタムシナリオ用
    round_target = Column(Integer, nullable=False)  # 4-12 rounds
    completed_rounds = Column(Integer, default=0)
    difficulty = Column(
        Enum(DifficultyLevel, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    mode = Column(
        Enum(SessionMode, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    extension_count = Column(Integer, default=0)  # 延長回数（最大2回）
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    scenario = relationship("Scenario", back_populates="sessions")
    custom_scenario = relationship("CustomScenario", back_populates="sessions")
    session_rounds = relationship(
        "SessionRound", back_populates="session", cascade="all, delete-orphan"
    )
    saved_phrases = relationship("SavedPhrase", back_populates="session")


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
    __table_args__ = {"extend_existing": True}


class ReviewItem(Base):
    __tablename__ = "review_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    phrase = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    source_session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    source_round_index = Column(Integer, nullable=True)
    selection_reason = Column(String(255), nullable=True)
    selection_score = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="review_items")
    source_session = relationship("Session")

    __table_args__ = (
        Index("ix_review_items_user_session", "user_id", "source_session_id"),
    )


class SavedPhrase(Base):
    """ユーザーが手動で保存した改善フレーズ"""

    __tablename__ = "saved_phrases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    phrase = Column(Text, nullable=False)  # improved_sentence
    explanation = Column(Text, nullable=False)  # feedback_short
    original_input = Column(Text, nullable=True)  # ユーザーの元発話
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    round_index = Column(Integer, nullable=True)
    converted_to_review_id = Column(
        Integer, ForeignKey("review_items.id"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="saved_phrases")
    session = relationship("Session", back_populates="saved_phrases")
    converted_review = relationship("ReviewItem")


class ShadowingSentence(Base):
    """シナリオごとのシャドーイング文"""

    __tablename__ = "shadowing_sentences"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False)
    key_phrase = Column(String(255), nullable=False)
    sentence_en = Column(Text, nullable=False)
    sentence_ja = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)
    difficulty = Column(
        Enum(DifficultyLevel, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    audio_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    scenario = relationship("Scenario", back_populates="shadowing_sentences")
    user_progress = relationship("UserShadowingProgress", back_populates="shadowing_sentence", cascade="all, delete-orphan")

    # Unique constraint
    __table_args__ = (
        {"extend_existing": True},
    )


class UserShadowingProgress(Base):
    """ユーザーのシャドーイング進捗"""

    __tablename__ = "user_shadowing_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shadowing_sentence_id = Column(Integer, ForeignKey("shadowing_sentences.id", ondelete="CASCADE"), nullable=False)
    attempt_count = Column(Integer, default=0, nullable=False)
    best_score = Column(Integer, nullable=True)
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="shadowing_progress")
    shadowing_sentence = relationship("ShadowingSentence", back_populates="user_progress")


class CustomScenario(Base):
    """ユーザーが作成したオリジナルシナリオ"""

    __tablename__ = "custom_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    user_role = Column(Text, nullable=False)  # ユーザーの役割
    ai_role = Column(Text, nullable=False)  # AIの役割
    difficulty = Column(String(20), default="intermediate", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="custom_scenarios")
    sessions = relationship("Session", back_populates="custom_scenario")
