from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.services.review.review_service import ReviewService
from models.database.models import User
from models.schemas.schemas import ReviewNextResponse, ReviewItem, ReviewCompleteRequest

router = APIRouter()


@router.get("/next", response_model=ReviewNextResponse)
def get_next_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    items = service.get_due_items(current_user.id)
    total = service.count_due_items(current_user.id)
    return ReviewNextResponse(review_items=items, total_count=total)


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

