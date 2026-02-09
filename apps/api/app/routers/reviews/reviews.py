from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_pro_user
from app.services.review.review_service import ReviewService
from app.services.review.review_question_service import ReviewQuestionService
from models.database.models import User, ReviewItem as ReviewItemModel
from models.schemas.schemas import (
    ReviewNextResponse,
    ReviewItem,
    ReviewCompleteRequest,
    ReviewQuestion,
    ReviewQuestionsResponse,
    ReviewEvaluateRequest,
    ReviewEvaluateResponse,
    ReviewStatsResponse,
    WordMatch,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# 問題データをセッションに保存するための一時ストレージ（MVPではインメモリ）
# 本番環境ではRedisなどを使用することを推奨
_questions_cache: dict[str, dict] = {}


def _get_cache_key(user_id: int, review_id: int) -> str:
    return f"{user_id}:{review_id}"


@router.get("/next", response_model=ReviewNextResponse)
def get_next_reviews(
    current_user: User = Depends(require_pro_user),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    items = service.get_due_items(current_user.id)
    total = service.count_due_items(current_user.id)
    return ReviewNextResponse(review_items=items, total_count=total)


@router.get("/stats", response_model=ReviewStatsResponse)
def get_review_stats(
    current_user: User = Depends(require_pro_user),
    db: Session = Depends(get_db),
):
    """累計の復習完了率を取得する"""
    service = ReviewService(db)
    stats = service.get_stats(current_user.id)
    return ReviewStatsResponse(
        total_items=stats["total_items"],
        completed_items=stats["completed_items"],
        completion_rate=stats["completion_rate"],
    )


@router.post("/{review_id}/complete", response_model=ReviewItem)
def complete_review(
    review_id: int,
    payload: ReviewCompleteRequest,
    current_user: User = Depends(require_pro_user),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)

    try:
        item, _ = service.complete_review_item(
            current_user.id, review_id, payload.result
        )
        return item
    except ValueError as exc:  # noqa: PERF203 - simple error mapping
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.get("/{review_id}/questions", response_model=ReviewQuestionsResponse)
async def get_review_questions(
    review_id: int,
    current_user: User = Depends(require_pro_user),
    db: Session = Depends(get_db),
):
    """復習アイテムに対するスピーキング・リスニング問題を生成する"""
    # 復習アイテムを取得
    item = (
        db.query(ReviewItemModel)
        .filter(
            ReviewItemModel.id == review_id, ReviewItemModel.user_id == current_user.id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review item not found"
        )

    # 問題を生成
    try:
        async with ReviewQuestionService() as question_service:
            speaking, listening = await question_service.generate_both_questions(
                phrase=item.phrase,
                explanation=item.explanation,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI service timeout"
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate questions",
        ) from exc

    # 評価用にキャッシュに保存
    cache_key = _get_cache_key(current_user.id, review_id)
    _questions_cache[cache_key] = {
        "speaking_target": speaking.target_sentence,
        "listening_words": listening.puzzle_words,
    }

    return ReviewQuestionsResponse(
        review_item_id=item.id,
        phrase=item.phrase,
        explanation=item.explanation,
        speaking=ReviewQuestion(
            question_type=speaking.question_type,
            prompt=speaking.prompt,
            hint=speaking.hint,
            target_sentence=speaking.target_sentence,
            audio_text=speaking.audio_text,
            puzzle_words=None,
        ),
        listening=ReviewQuestion(
            question_type=listening.question_type,
            prompt=listening.prompt,
            hint=listening.hint,
            target_sentence=None,
            audio_text=listening.audio_text,
            puzzle_words=listening.puzzle_words,
        ),
    )


@router.post("/{review_id}/evaluate", response_model=ReviewEvaluateResponse)
def evaluate_review(
    review_id: int,
    payload: ReviewEvaluateRequest,
    current_user: User = Depends(require_pro_user),
    db: Session = Depends(get_db),
):
    """復習の評価を送信する

    スピーキング: 発話内容とターゲット文の単語一致率で評価
    リスニング: 単語パズルの完全一致で評価
    """
    service = ReviewService(db)

    # キャッシュから問題データを取得
    cache_key = _get_cache_key(current_user.id, review_id)
    cached = _questions_cache.get(cache_key)

    if not cached:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questions not found. Please call GET /questions first.",
        )

    try:
        logger.info(f"evaluate_review: {payload}")
        logger.info(f"cached: {cached}")
        logger.info(f"review_id: {review_id}")
        logger.info(f"current_user: {current_user.id}")
        logger.info(f"db: {db}")
        logger.info(f"service: {service}")
        logger.info(f"payload: {payload}")
        logger.info(f"cached: {cached}")
        logger.info(f"review_id: {review_id}")
        if payload.question_type == "speaking":
            # スピーキング評価: 単語一致率
            target_sentence = cached.get("speaking_target", "")
            user_transcription = payload.user_transcription or ""

            eval_result = service.evaluate_speaking(target_sentence, user_transcription)

            # 復習アイテムを更新
            item, is_completed, next_due_at = service.evaluate_and_update(
                user_id=current_user.id,
                item_id=review_id,
                question_type="speaking",
                score=eval_result.score,
                is_correct=eval_result.is_correct,
            )
            logger.info(f"item: {item}")
            logger.info(f"is_completed: {is_completed}")
            logger.info(f"next_due_at: {next_due_at}")
            logger.info(f"eval_result: {eval_result}")
            logger.info(f"eval_result.score: {eval_result.score}")
            logger.info(f"eval_result.is_correct: {eval_result.is_correct}")
            logger.info(f"eval_result.matching_words: {eval_result.matching_words}")
            logger.info(f"eval_result.correct_answer: {eval_result.correct_answer}")

            return ReviewEvaluateResponse(
                review_item_id=item.id,
                question_type="speaking",
                score=eval_result.score,
                is_correct=eval_result.is_correct,
                is_completed=is_completed,
                next_due_at=next_due_at,
                matching_words=[
                    WordMatch(
                        word=m.word,
                        matched=m.matched,
                        index=m.index,
                    )
                    for m in eval_result.matching_words
                ],
                correct_answer=eval_result.correct_answer,
            )

        elif payload.question_type == "listening":
            # リスニング評価: 単語パズル完全一致
            correct_words = cached.get("listening_words", [])
            user_answer = payload.user_answer or []

            eval_result = service.evaluate_listening(correct_words, user_answer)

            # 復習アイテムを更新
            item, is_completed, next_due_at = service.evaluate_and_update(
                user_id=current_user.id,
                item_id=review_id,
                question_type="listening",
                score=eval_result.score,
                is_correct=eval_result.is_correct,
            )

            # キャッシュをクリア（両方の問題が完了）
            _questions_cache.pop(cache_key, None)

            return ReviewEvaluateResponse(
                review_item_id=item.id,
                question_type="listening",
                score=eval_result.score,
                is_correct=eval_result.is_correct,
                is_completed=is_completed,
                next_due_at=next_due_at,
                matching_words=None,
                correct_answer=eval_result.correct_answer,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question type"
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
