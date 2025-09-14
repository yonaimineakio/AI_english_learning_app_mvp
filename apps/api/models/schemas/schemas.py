from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ScenarioCategory(str, Enum):
    TRAVEL = "travel"
    BUSINESS = "business"
    DAILY = "daily"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SessionMode(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    CUSTOM = "custom"


# User schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., max_length=255)


class UserCreate(UserBase):
    sub: str = Field(..., min_length=1, max_length=255)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sub: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# Scenario schemas
class ScenarioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: ScenarioCategory
    difficulty: DifficultyLevel
    is_active: bool = True


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[ScenarioCategory] = None
    difficulty: Optional[DifficultyLevel] = None
    is_active: Optional[bool] = None


class Scenario(ScenarioBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Session schemas
class SessionBase(BaseModel):
    scenario_id: int
    round_target: int = Field(..., ge=4, le=12)
    difficulty: DifficultyLevel
    mode: SessionMode


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    round_target: Optional[int] = Field(None, ge=4, le=12)
    difficulty: Optional[DifficultyLevel] = None
    mode: Optional[SessionMode] = None


class Session(SessionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    completed_rounds: int = 0
    started_at: datetime
    ended_at: Optional[datetime] = None


class SessionWithDetails(Session):
    scenario: Scenario
    session_rounds: List["SessionRound"] = []


# SessionRound schemas
class SessionRoundBase(BaseModel):
    round_index: int = Field(..., ge=1)
    user_input: str
    ai_reply: str
    feedback_short: str = Field(..., max_length=120)
    improved_sentence: str
    tags: Optional[List[str]] = None
    score_pronunciation: Optional[int] = Field(None, ge=0, le=100)
    score_grammar: Optional[int] = Field(None, ge=0, le=100)


class SessionRoundCreate(SessionRoundBase):
    session_id: int


class SessionRoundUpdate(BaseModel):
    user_input: Optional[str] = None
    ai_reply: Optional[str] = None
    feedback_short: Optional[str] = Field(None, max_length=120)
    improved_sentence: Optional[str] = None
    tags: Optional[List[str]] = None
    score_pronunciation: Optional[int] = Field(None, ge=0, le=100)
    score_grammar: Optional[int] = Field(None, ge=0, le=100)


class SessionRound(SessionRoundBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    created_at: datetime


# ReviewItem schemas
class ReviewItemBase(BaseModel):
    phrase: str
    explanation: str
    due_at: datetime


class ReviewItemCreate(ReviewItemBase):
    user_id: int


class ReviewItemUpdate(BaseModel):
    phrase: Optional[str] = None
    explanation: Optional[str] = None
    due_at: Optional[datetime] = None
    is_completed: Optional[bool] = None


class ReviewItem(ReviewItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    is_completed: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None


# API Response schemas
class SessionStartResponse(BaseModel):
    session_id: int
    scenario: Scenario
    round_target: int
    difficulty: DifficultyLevel
    mode: SessionMode


class TurnResponse(BaseModel):
    round_index: int
    ai_reply: str
    feedback_short: str
    improved_sentence: str
    tags: Optional[List[str]] = None


class SessionEndResponse(BaseModel):
    session_id: int
    completed_rounds: int
    top_phrases: List[Dict[str, Any]]  # Top 3 phrases for review


class ReviewNextResponse(BaseModel):
    review_items: List[ReviewItem]
    total_count: int


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# Update forward references
SessionWithDetails.model_rebuild()
