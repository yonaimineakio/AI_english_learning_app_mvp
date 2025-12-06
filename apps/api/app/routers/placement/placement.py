from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.services.placement.word_matcher import WordMatcher
from models.database.models import User
from models.schemas.schemas import DifficultyLevel

router = APIRouter(tags=["placement"])


class PlacementQuestionSchema:
    """静的に管理するレベル判定テストの質問定義."""

    def __init__(
        self,
        id: int,
        qtype: str,
        prompt: str,
        scenario_hint: str,
        expected_text: Optional[str] = None,
        word_options: Optional[List[str]] = None,
        distractor_words: Optional[List[str]] = None,
    ) -> None:
        self.id = id
        self.type = qtype  # "listening" | "speaking"
        self.prompt = prompt
        self.scenario_hint = scenario_hint
        # For Speaking: the expected sentence to match
        self.expected_text = expected_text
        # For Listening: words to arrange (correct order)
        self.word_options = word_options or []
        # For Listening: additional wrong words
        self.distractor_words = distractor_words or []


QUESTIONS: List[PlacementQuestionSchema] = [
    # 旅行系（listening/speaking）
    PlacementQuestionSchema(
        id=1,
        qtype="listening",
        prompt="I'm about to board my flight to New York.",
        scenario_hint="空港チェックイン・搭乗前",
        expected_text="I'm about to board my flight to New York.",
        word_options=["I'm", "about", "to", "board", "my", "flight", "to", "New York."],
        distractor_words=["going", "take", "plane", "leaving"],
    ),
    PlacementQuestionSchema(
        id=2,
        qtype="speaking",
        prompt="I need to drop off my baggage.",
        scenario_hint="空港チェックイン・荷物預け",
        expected_text="I need to drop off my baggage.",
    ),
    PlacementQuestionSchema(
        id=3,
        qtype="listening",
        prompt="We're supposed to check in two hours before departure.",
        scenario_hint="空港・ルールの説明",
        expected_text="We're supposed to check in two hours before departure.",
        word_options=["We're", "supposed", "to", "check", "in", "two", "hours", "before", "departure."],
        distractor_words=["must", "arrive", "need", "early"],
    ),
    PlacementQuestionSchema(
        id=4,
        qtype="speaking",
        prompt="I'd love to spend a week at a beach resort.",
        scenario_hint="最高のバケーション",
        expected_text="I'd love to spend a week at a beach resort.",
    ),
    PlacementQuestionSchema(
        id=5,
        qtype="speaking",
        prompt="I recommend visiting Kyoto during spring.",
        scenario_hint="日本を案内する",
        expected_text="I recommend visiting Kyoto during spring.",
    ),
    # 日常会話系
    PlacementQuestionSchema(
        id=6,
        qtype="speaking",
        prompt="I need to report a lost wallet.",
        scenario_hint="財布を無くして警察に相談",
        expected_text="I need to report a lost wallet.",
    ),
    PlacementQuestionSchema(
        id=7,
        qtype="listening",
        prompt="I'd like to ask about a problem with my order.",
        scenario_hint="カスタマーサービスに相談",
        expected_text="I'd like to ask about a problem with my order.",
        word_options=["I'd", "like", "to", "ask", "about", "a", "problem", "with", "my", "order."],
        distractor_words=["want", "question", "issue", "have"],
    ),
    PlacementQuestionSchema(
        id=8,
        qtype="speaking",
        prompt="I feel like trying the seasonal drink.",
        scenario_hint="おしゃれカフェで店員と雑談",
        expected_text="I feel like trying the seasonal drink.",
    ),
    PlacementQuestionSchema(
        id=9,
        qtype="listening",
        prompt="I'm looking for two tickets for tonight's show.",
        scenario_hint="ショーチケットを入手",
        expected_text="I'm looking for two tickets for tonight's show.",
        word_options=["I'm", "looking", "for", "two", "tickets", "for", "tonight's", "show."],
        distractor_words=["want", "need", "buy", "purchase"],
    ),
    PlacementQuestionSchema(
        id=10,
        qtype="speaking",
        prompt="It's such a beautiful day today, isn't it?",
        scenario_hint="公園で雑談",
        expected_text="It's such a beautiful day today, isn't it?",
    ),
    # ビジネス系
    PlacementQuestionSchema(
        id=11,
        qtype="speaking",
        prompt="Something urgent came up, so I need to reschedule our meeting.",
        scenario_hint="ミーティングをリスケする",
        expected_text="Something urgent came up, so I need to reschedule our meeting.",
    ),
    PlacementQuestionSchema(
        id=12,
        qtype="speaking",
        prompt="Are you available for a 30-minute meeting next week?",
        scenario_hint="ミーティングを立てる",
        expected_text="Are you available for a 30-minute meeting next week?",
    ),
    PlacementQuestionSchema(
        id=13,
        qtype="listening",
        prompt="Let's move on to the next agenda item.",
        scenario_hint="会議を進行する",
        expected_text="Let's move on to the next agenda item.",
        word_options=["Let's", "move", "on", "to", "the", "next", "agenda", "item."],
        distractor_words=["proceed", "continue", "topic", "point"],
    ),
    PlacementQuestionSchema(
        id=14,
        qtype="speaking",
        prompt="I'm willing to offer a discount if the contract is extended.",
        scenario_hint="契約条件の交渉",
        expected_text="I'm willing to offer a discount if the contract is extended.",
    ),
    PlacementQuestionSchema(
        id=15,
        qtype="speaking",
        prompt="I'd like to share the key findings from our survey.",
        scenario_hint="顧客満足度の調査結果をプレゼン",
        expected_text="I'd like to share the key findings from our survey.",
    ),
    # レベル境界を測るための少し難しめの質問
    PlacementQuestionSchema(
        id=16,
        qtype="listening",
        prompt="We've been trying to catch up with the schedule.",
        scenario_hint="プロジェクトの遅延を謝罪する",
        expected_text="We've been trying to catch up with the schedule.",
        word_options=["We've", "been", "trying", "to", "catch", "up", "with", "the", "schedule."],
        distractor_words=["working", "hard", "meet", "deadline"],
    ),
    PlacementQuestionSchema(
        id=17,
        qtype="speaking",
        prompt="I apologize for the delay and will ensure it doesn't happen again.",
        scenario_hint="プロジェクトの遅延を謝罪する",
        expected_text="I apologize for the delay and will ensure it doesn't happen again.",
    ),
    PlacementQuestionSchema(
        id=18,
        qtype="listening",
        prompt="I'm not feeling well today and need to take the day off.",
        scenario_hint="体調不良で休む",
        expected_text="I'm not feeling well today and need to take the day off.",
        word_options=["I'm", "not", "feeling", "well", "today", "and", "need", "to", "take", "the", "day", "off."],
        distractor_words=["sick", "unwell", "leave", "rest"],
    ),
    PlacementQuestionSchema(
        id=19,
        qtype="speaking",
        prompt="I'm about to call in sick and hand over my tasks.",
        scenario_hint="体調不良で休む・引き継ぎ",
        expected_text="I'm about to call in sick and hand over my tasks.",
    ),
    PlacementQuestionSchema(
        id=20,
        qtype="speaking",
        prompt="I'd like to bring up a new topic for discussion.",
        scenario_hint="ビジネスミーティング全般",
        expected_text="I'd like to bring up a new topic for discussion.",
    ),
]


def _get_question_by_id(question_id: int) -> Optional[PlacementQuestionSchema]:
    """Get a question by its ID."""
    for q in QUESTIONS:
        if q.id == question_id:
            return q
    return None


def _score_answers(answers: List[dict]) -> int:
    """新しい評価システムでのスコア計算."""
    score = 0
    for a in answers:
        # Check for new evaluation results
        speaking_score = a.get("speaking_score")
        listening_correct = a.get("listening_correct")
        self_score = a.get("self_score")

        if speaking_score is not None:
            # Speaking: score is 0-100, convert to 0-5 scale
            score += int(speaking_score / 20)  # 100 -> 5, 80 -> 4, etc.
        elif listening_correct is not None:
            # Listening: correct = 5, incorrect = 0
            score += 5 if listening_correct else 0
        elif isinstance(self_score, int) and 0 <= self_score <= 5:
            # Legacy self-evaluation
            score += self_score
    return score


def _decide_level(score: int) -> DifficultyLevel:
    """合計スコアからレベルを決定."""
    if score <= 40:
        return DifficultyLevel.BEGINNER
    if score <= 70:
        return DifficultyLevel.INTERMEDIATE
    return DifficultyLevel.ADVANCED


# ============ Pydantic Schemas ============


class WordMatchResult(BaseModel):
    """Word match result for a single word."""

    word: str
    matched: bool
    position: int


class SpeakingEvaluationRequest(BaseModel):
    """Request body for Speaking evaluation."""

    question_id: int = Field(..., description="ID of the question being evaluated")
    user_transcript: str = Field(..., description="STT result from user's speech")


class SpeakingEvaluationResponse(BaseModel):
    """Response body for Speaking evaluation."""

    word_matches: List[WordMatchResult]
    score: float = Field(..., ge=0, le=100)
    matched_count: int
    total_count: int
    expected_text: str


class ListeningEvaluationRequest(BaseModel):
    """Request body for Listening evaluation."""

    question_id: int = Field(..., description="ID of the question being evaluated")
    user_answer: str = Field(..., description="User's rearranged word answer")


class ListeningEvaluationResponse(BaseModel):
    """Response body for Listening evaluation."""

    correct: bool
    expected: str


# ============ API Endpoints ============


@router.get("/questions")
async def get_placement_questions(
    current_user: User = Depends(get_current_user),
) -> dict:
    """レベル判定テスト用の全20問を返す."""
    return {
        "questions": [
            {
                "id": q.id,
                "type": q.type,
                "prompt": q.prompt,
                "scenario_hint": q.scenario_hint,
                "expected_text": q.expected_text,
                "word_options": q.word_options,
                "distractor_words": q.distractor_words,
            }
            for q in QUESTIONS
        ]
    }


@router.post("/evaluate-speaking", response_model=SpeakingEvaluationResponse)
async def evaluate_speaking(
    payload: SpeakingEvaluationRequest,
    current_user: User = Depends(get_current_user),
) -> SpeakingEvaluationResponse:
    """Speaking問題の評価: STT結果と問題文を部分一致で比較."""
    question = _get_question_by_id(payload.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {payload.question_id} not found",
        )

    if question.type != "speaking":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {payload.question_id} is not a speaking question",
        )

    if not question.expected_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {payload.question_id} has no expected text",
        )

    result = WordMatcher.evaluate_speaking(
        expected_text=question.expected_text,
        user_transcript=payload.user_transcript,
    )

    return SpeakingEvaluationResponse(
        word_matches=[
            WordMatchResult(
                word=m.word,
                matched=m.matched,
                position=m.position,
            )
            for m in result.word_matches
        ],
        score=result.score,
        matched_count=result.matched_count,
        total_count=result.total_count,
        expected_text=question.expected_text,
    )


@router.post("/evaluate-listening", response_model=ListeningEvaluationResponse)
async def evaluate_listening(
    payload: ListeningEvaluationRequest,
    current_user: User = Depends(get_current_user),
) -> ListeningEvaluationResponse:
    """Listening問題の評価: 並び替え結果を完全一致で比較."""
    question = _get_question_by_id(payload.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {payload.question_id} not found",
        )

    if question.type != "listening":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {payload.question_id} is not a listening question",
        )

    if not question.expected_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {payload.question_id} has no expected text",
        )

    is_correct, expected = WordMatcher.evaluate_listening(
        expected_text=question.expected_text,
        user_answer=payload.user_answer,
    )

    return ListeningEvaluationResponse(
        correct=is_correct,
        expected=expected,
    )


@router.post("/submit")
async def submit_placement_answers(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """レベル判定テストの回答を受け取り、スコアとレベルを決定して保存する。"""
    answers: Optional[List[dict]] = payload.get("answers")
    if not answers or not isinstance(answers, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="answers must be a non-empty list",
        )

    score = _score_answers(answers)
    max_score = 5 * len(QUESTIONS)
    level = _decide_level(score)

    # ユーザーに結果を保存
    user: User = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.placement_level = level
    user.placement_score = score
    user.placement_completed_at = datetime.now(timezone.utc)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "score": score,
        "max_score": max_score,
        "placement_level": level.value,
        "placement_completed_at": user.placement_completed_at.isoformat(),
    }
