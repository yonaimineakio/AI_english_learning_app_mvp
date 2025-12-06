from __future__ import annotations

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.services.review.review_service import ReviewService
from app.services.review.problem_generator import ProblemGenerator, ProblemType
from app.services.placement.word_matcher import WordMatcher
from models.database.models import User
from models.schemas.schemas import ReviewNextResponse, ReviewItem, ReviewCompleteRequest

router = APIRouter()


# ============ Pydantic Schemas ============


class WordMatchResult(BaseModel):
    """Word match result for a single word."""

    word: str
    matched: bool
    position: int


class ReviewProblemResponse(BaseModel):
    """Response for next review problem."""

    type: Literal["speaking", "listening", "phrase"]
    review_item_id: int
    phrase: str
    explanation: str
    # For speaking/listening problems
    sentence: Optional[str] = None
    word_options: Optional[List[str]] = None
    distractors: Optional[List[str]] = None
    phrase_highlight: Optional[tuple[int, int]] = None


class ReviewProblemEvaluateRequest(BaseModel):
    """Request to evaluate a review problem."""

    review_item_id: int = Field(..., description="ID of the review item")
    type: Literal["speaking", "listening", "phrase"] = Field(..., description="Type of problem")
    answer: str = Field(..., description="User's answer")


class SpeakingEvaluationResult(BaseModel):
    """Result of speaking evaluation."""

    word_matches: List[WordMatchResult]
    score: float
    matched_count: int
    total_count: int


class ReviewProblemEvaluateResponse(BaseModel):
    """Response for problem evaluation."""

    type: Literal["speaking", "listening", "phrase"]
    is_correct: bool
    # For speaking
    speaking_result: Optional[SpeakingEvaluationResult] = None
    # For listening/phrase
    expected: Optional[str] = None
    # Updated review item
    review_item: ReviewItem


# ============ API Endpoints ============


@router.get("/next", response_model=ReviewNextResponse)
def get_next_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    items = service.get_due_items(current_user.id)
    total = service.count_due_items(current_user.id)
    return ReviewNextResponse(review_items=items, total_count=total)


@router.get("/next-problem", response_model=ReviewProblemResponse)
def get_next_review_problem(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the next review problem (speaking/listening/phrase)."""
    service = ReviewService(db)
    items = service.get_due_items(current_user.id, limit=1)

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No review items available",
        )

    item = items[0]
    problem_type = ProblemGenerator.select_problem_type()

    response = ReviewProblemResponse(
        type=problem_type.value,
        review_item_id=item.id,
        phrase=item.phrase,
        explanation=item.explanation,
    )

    if problem_type == ProblemType.SPEAKING:
        problem = ProblemGenerator.generate_speaking_problem(item.phrase)
        response.sentence = problem.sentence
        response.phrase_highlight = problem.phrase_highlight
    elif problem_type == ProblemType.LISTENING:
        problem = ProblemGenerator.generate_listening_problem(item.phrase)
        response.sentence = problem.sentence
        response.word_options = problem.word_options
        response.distractors = problem.distractors

    return response


@router.post("/evaluate-problem", response_model=ReviewProblemEvaluateResponse)
def evaluate_review_problem(
    payload: ReviewProblemEvaluateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluate a review problem and update the review item."""
    service = ReviewService(db)

    # Get the review item
    items = service.get_due_items(current_user.id, limit=100)
    item = next((i for i in items if i.id == payload.review_item_id), None)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review item not found",
        )

    is_correct = False
    speaking_result = None
    expected = None

    if payload.type == "speaking":
        # Generate the same problem to get the expected sentence
        problem = ProblemGenerator.generate_speaking_problem(item.phrase)
        result = WordMatcher.evaluate_speaking(
            expected_text=problem.sentence,
            user_transcript=payload.answer,
        )
        # Consider 70%+ score as correct
        is_correct = result.score >= 70
        speaking_result = SpeakingEvaluationResult(
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
        )
    elif payload.type == "listening":
        # Generate the same problem to get the expected sentence
        problem = ProblemGenerator.generate_listening_problem(item.phrase)
        is_correct, expected = WordMatcher.evaluate_listening(
            expected_text=problem.sentence,
            user_answer=payload.answer,
        )
    else:  # phrase
        # For phrase review, the answer should contain the phrase
        is_correct = item.phrase.lower() in payload.answer.lower()
        expected = item.phrase

    # Update the review item based on result
    result_str = "correct" if is_correct else "incorrect"
    updated_item, _ = service.complete_review_item(
        current_user.id,
        payload.review_item_id,
        result_str,
    )

    return ReviewProblemEvaluateResponse(
        type=payload.type,
        is_correct=is_correct,
        speaking_result=speaking_result,
        expected=expected,
        review_item=updated_item,
    )


@router.post("/{review_id}/complete", response_model=ReviewItem)
def complete_review(
    review_id: int,
    payload: ReviewCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)

    try:
        item, _ = service.complete_review_item(current_user.id, review_id, payload.result)
        return item
    except ValueError as exc:  # noqa: PERF203 - simple error mapping
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
