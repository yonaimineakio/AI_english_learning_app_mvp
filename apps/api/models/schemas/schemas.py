from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, date
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

    id: str  # UUID
    sub: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    placement_level: Optional[DifficultyLevel] = None
    placement_score: Optional[int] = None
    placement_completed_at: Optional[datetime] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    last_activity_date: Optional[date] = None
    is_pro: Optional[bool] = None


class UserStatsResponse(BaseModel):
    """ユーザー統計情報レスポンス"""

    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None
    total_sessions: int
    total_rounds: int


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


# CustomScenario schemas (オリジナルシナリオ)
class CustomScenarioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    user_role: str = Field(..., min_length=1)  # ユーザーの役割
    ai_role: str = Field(..., min_length=1)  # AIの役割


class CustomScenarioCreate(CustomScenarioBase):
    pass


class CustomScenario(CustomScenarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str  # UUID
    goals: Optional[List[str]] = None  # AI生成ゴール（NULLならデフォルト）
    difficulty: str = "intermediate"
    is_active: bool = True
    created_at: datetime


class CustomScenarioListResponse(BaseModel):
    """オリジナルシナリオ一覧レスポンス"""
    custom_scenarios: List[CustomScenario]
    total_count: int


class CustomScenarioLimitResponse(BaseModel):
    """オリジナルシナリオ作成制限レスポンス"""
    daily_limit: int  # 1日の制限数
    created_today: int  # 本日作成済み数
    remaining: int  # 残り作成可能数
    is_pro: bool


# Session schemas
class SessionBase(BaseModel):
    scenario_id: Optional[int] = None  # 通常シナリオ用（どちらか必須）
    custom_scenario_id: Optional[int] = None  # カスタムシナリオ用（どちらか必須）
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
    user_id: str  # UUID
    scenario_id: Optional[int] = None
    custom_scenario_id: Optional[int] = None
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
    user_id: str  # UUID


class ReviewItemUpdate(BaseModel):
    phrase: Optional[str] = None
    explanation: Optional[str] = None
    due_at: Optional[datetime] = None
    is_completed: Optional[bool] = None


class ReviewItem(ReviewItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str  # UUID
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


# Rankings schemas
class UserPointsResponse(BaseModel):
    """ユーザーのポイントサマリ"""

    total_points: int
    points_this_week: int
    points_today: int


class RankingEntry(BaseModel):
    """ランキング1行分"""

    rank: int
    user_id: str  # UUID
    user_name: str
    total_points: int
    current_streak: int


class RankingsResponse(BaseModel):
    """ランキング一覧レスポンス"""

    rankings: List[RankingEntry]
    total_users: int


class MyRankingResponse(BaseModel):
    """自分のランキング情報"""

    rank: int
    total_points: int
    points_to_next_rank: Optional[int] = None
    total_users: int


# API Response schemas
class SessionStartResponse(BaseModel):
    session_id: int
    scenario: Optional[Scenario] = None  # 通常シナリオ
    custom_scenario: Optional[CustomScenario] = None  # カスタムシナリオ
    round_target: int
    difficulty: Literal["beginner", "intermediate", "advanced"]
    mode: Literal["quick", "standard", "deep", "custom"]
    # セッション開始時に表示するシナリオ別の初期AIメッセージ（任意）
    initial_ai_message: Optional[str] = None
    # 各ゴールのラベル（テキスト）
    goals_labels: Optional[List[str]] = None


class SessionStatusResponse(BaseModel):
    session_id: int
    scenario_id: Optional[int] = None  # 通常シナリオ
    custom_scenario_id: Optional[int] = None  # カスタムシナリオ
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
    is_custom_scenario: bool = False  # カスタムシナリオかどうか
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
    # 終了提案の理由（UIで文言や再表示制御に使う）
    # - user_intent: ユーザーが終了意図を示した
    # - goals_completed: 学習ゴール達成
    # - round_limit: ラウンド上限に到達（+3延長提示）
    end_prompt_reason: Optional[
        Literal["user_intent", "goals_completed", "round_limit"]
    ] = None
    # 学習ゴール達成率（達成率判定機能用）
    goals_total: Optional[int] = None
    goals_achieved: Optional[int] = None
    goals_status: Optional[List[int]] = None
    goals_labels: Optional[List[str]] = None  # 各ゴールのラベル（テキスト）


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
    goals_labels: Optional[List[str]] = None  # 各ゴールのラベル（テキスト）


class ReviewNextResponse(BaseModel):
    review_items: List[ReviewItem]
    total_count: int


# SavedPhrase schemas
class SavedPhraseBase(BaseModel):
    phrase: str
    explanation: str
    original_input: Optional[str] = None


class SavedPhraseCreate(SavedPhraseBase):
    session_id: Optional[int] = None
    round_index: Optional[int] = None


class SavedPhrase(SavedPhraseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str  # UUID
    session_id: Optional[int] = None
    round_index: Optional[int] = None
    scenario_id: Optional[int] = None
    scenario_name: Optional[str] = None
    converted_to_review_id: Optional[int] = None
    created_at: datetime


class SavedPhrasesListResponse(BaseModel):
    saved_phrases: List[SavedPhrase]
    total_count: int


class ConvertToReviewResponse(BaseModel):
    saved_phrase_id: int
    review_item: ReviewItem


# ReviewStats schemas
class ReviewStatsResponse(BaseModel):
    """復習統計情報"""

    total_items: int
    completed_items: int
    completion_rate: float  # 0.0 - 100.0


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# Shadowing schemas
class ShadowingUserProgress(BaseModel):
    """ユーザーのシャドーイング文ごとの進捗"""
    attempt_count: int = 0
    best_score: Optional[int] = None
    is_completed: bool = False
    last_practiced_at: Optional[datetime] = None


class ShadowingSentenceBase(BaseModel):
    """シャドーイング文の基本情報"""
    key_phrase: str
    sentence_en: str
    sentence_ja: str
    order_index: int
    difficulty: Literal["beginner", "intermediate", "advanced"]
    audio_url: Optional[str] = None


class ShadowingSentence(ShadowingSentenceBase):
    """シャドーイング文（進捗付き）"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    user_progress: Optional[ShadowingUserProgress] = None
    instant_translation_progress: Optional[ShadowingUserProgress] = None


class ScenarioShadowingResponse(BaseModel):
    """シナリオのシャドーイング文一覧レスポンス"""
    scenario_id: int
    scenario_name: str
    sentences: List[ShadowingSentence]
    total_sentences: int
    completed_count: int


class ShadowingAttemptRequest(BaseModel):
    """シャドーイング練習結果の記録リクエスト"""
    score: int = Field(..., ge=0, le=100)


class ShadowingAttemptResponse(BaseModel):
    """シャドーイング練習結果のレスポンス"""
    shadowing_sentence_id: int
    attempt_count: int
    best_score: int
    is_completed: bool
    is_new_best: bool


class ShadowingWordMatch(BaseModel):
    """単語の一致結果（シャドーイング用）"""
    word: str
    matched: bool
    index: int


class ShadowingSpeakRequest(BaseModel):
    """シャドーイング発話評価リクエスト"""
    user_transcription: str = Field(..., min_length=1, max_length=1000)


class ShadowingSpeakResponse(BaseModel):
    """シャドーイング発話評価レスポンス"""
    shadowing_sentence_id: int
    score: int
    attempt_count: int
    best_score: int
    is_completed: bool
    is_new_best: bool
    target_sentence: str
    matching_words: List[ShadowingWordMatch]


class InstantTranslateSpeakResponse(BaseModel):
    """瞬間英作発話評価レスポンス"""
    shadowing_sentence_id: int
    score: int
    attempt_count: int
    best_score: int
    is_completed: bool
    is_new_best: bool
    target_sentence: str
    matching_words: List[ShadowingWordMatch]


class ScenarioProgressSummary(BaseModel):
    """シナリオごとの進捗サマリー"""
    scenario_id: int
    scenario_name: str
    category: str
    difficulty: str
    total_sentences: int
    completed_sentences: int
    progress_percent: int
    last_practiced_at: Optional[datetime] = None


class ShadowingProgressResponse(BaseModel):
    """シャドーイング全体進捗レスポンス（ホーム画面用）"""
    total_scenarios: int
    practiced_scenarios: int
    total_sentences: int
    completed_sentences: int
    today_practice_count: int
    recent_scenarios: List[ScenarioProgressSummary]


# Update forward references
SessionWithDetails.model_rebuild()
