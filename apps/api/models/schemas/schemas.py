from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
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
    placement_level: Optional[DifficultyLevel] = None
    placement_score: Optional[int] = None
    placement_completed_at: Optional[datetime] = None


# Scenario schemas
class ScenarioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Literal["travel", "business", "daily"]
    difficulty: Literal["beginner", "intermediate", "advanced"]
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
    difficulty: Literal["beginner", "intermediate", "advanced"]
    mode: Literal["quick", "standard", "deep", "custom"]


class SessionCreate(SessionBase):
    model_config = ConfigDict(use_enum_values=True)


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


class ReviewCompleteRequest(BaseModel):
    result: Literal["correct", "incorrect"]


# Review Question schemas (for speaking/listening practice)
class ReviewQuestion(BaseModel):
    """復習用の問題（スピーキング/リスニング）"""
    question_type: Literal["speaking", "listening"]
    prompt: str
    hint: Optional[str] = None
    # スピーキング用: ユーザーが読み上げるターゲット文
    target_sentence: Optional[str] = None
    # リスニング用: TTS読み上げテキスト
    audio_text: Optional[str] = None
    # リスニング用: 単語パズル（正解順の単語リスト）
    puzzle_words: Optional[List[str]] = None


class ReviewQuestionsResponse(BaseModel):
    """復習アイテムに対する問題一式"""
    review_item_id: int
    phrase: str
    explanation: str
    speaking: ReviewQuestion
    listening: ReviewQuestion


class WordMatch(BaseModel):
    """単語の一致情報"""
    word: str
    matched: bool
    index: int


class ReviewEvaluateRequest(BaseModel):
    """復習の評価リクエスト"""
    question_type: Literal["speaking", "listening"]
    # スピーキング用: 音声認識結果
    user_transcription: Optional[str] = None
    # リスニング用: ユーザーが並べた単語リスト
    user_answer: Optional[List[str]] = None


class ReviewEvaluateResponse(BaseModel):
    """復習の評価結果レスポンス"""
    review_item_id: int
    question_type: str
    score: int = Field(..., ge=0, le=100)  # 0-100点
    is_correct: bool  # 正解かどうか
    is_completed: bool  # 復習アイテムが完了したか
    next_due_at: Optional[datetime] = None
    # スピーキング用: 単語ごとの一致情報
    matching_words: Optional[List[WordMatch]] = None
    # 正解文（フィードバック用）
    correct_answer: Optional[str] = None


# Placement Test evaluation schemas
class PlacementSpeakingEvaluateRequest(BaseModel):
    """Placementテスト - Speaking評価リクエスト"""
    question_id: int
    user_transcription: str  # 音声認識結果


class PlacementSpeakingEvaluateResponse(BaseModel):
    """Placementテスト - Speaking評価レスポンス"""
    question_id: int
    target_sentence: str
    user_transcription: str
    score: int = Field(..., ge=0, le=100)
    matching_words: List[WordMatch]
    feedback: str


class PlacementListeningEvaluateRequest(BaseModel):
    """Placementテスト - Listening評価リクエスト"""
    question_id: int
    user_answer: List[str]  # ユーザーが並べた単語リスト


class PlacementListeningEvaluateResponse(BaseModel):
    """Placementテスト - Listening評価レスポンス"""
    question_id: int
    correct_sentence: str
    user_answer: str
    is_correct: bool
    score: int = Field(..., ge=0, le=100)


# API Response schemas
class SessionStartResponse(BaseModel):
    session_id: int
    scenario: Scenario
    round_target: int
    difficulty: Literal["beginner", "intermediate", "advanced"]
    mode: Literal["quick", "standard", "deep", "custom"]
    # セッション開始時に表示するシナリオ別の初期AIメッセージ（任意）
    initial_ai_message: Optional[str] = None


class SessionStatusResponse(BaseModel):
    session_id: int
    scenario_id: int
    round_target: int
    completed_rounds: int
    difficulty: Literal["beginner", "intermediate", "advanced"]
    mode: Literal["quick", "standard", "deep", "custom"]
    is_active: bool
    difficulty_label: Optional[str] = None
    mode_label: Optional[str] = None
    extension_offered: bool = False
    scenario_name: Optional[str] = None
    can_extend: bool = False
    # セッション開始時に表示するシナリオ別の初期AIメッセージ（任意）
    initial_ai_message: Optional[str] = None


class ConversationAiReply(BaseModel):
    message: str
    feedback_short: str
    improved_sentence: str
    tags: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None
    scores: Optional[Dict[str, Optional[int]]] = None


class TurnResponse(BaseModel):
    round_index: int
    ai_reply: ConversationAiReply | str
    feedback_short: str
    improved_sentence: str
    tags: Optional[List[str]] = None
    response_time_ms: Optional[int] = None
    provider: Optional[str] = None
    session_status: Optional[SessionStatusResponse] = None
    should_end_session: Optional[bool] = False
    # 学習ゴール達成率（達成率判定機能用）
    goals_total: Optional[int] = None
    goals_achieved: Optional[int] = None
    goals_status: Optional[List[int]] = None


class SessionEndResponse(BaseModel):
    session_id: int
    completed_rounds: int
    top_phrases: List[Dict[str, Any]]  # Top 3 phrases for review
    next_review_at: Optional[datetime] = None
    scenario_name: Optional[str] = None
    difficulty: Literal["beginner", "intermediate", "advanced"]
    mode: Literal["quick", "standard", "deep", "custom"]
    # セッション全体の学習ゴール達成率
    goals_total: Optional[int] = None
    goals_achieved: Optional[int] = None
    goals_status: Optional[List[int]] = None


class ReviewNextResponse(BaseModel):
    review_items: List[ReviewItem]
    total_count: int


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# Update forward references
SessionWithDetails.model_rebuild()
