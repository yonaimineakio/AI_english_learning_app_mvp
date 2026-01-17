from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user, get_db, require_pro_user
from models.database.models import (
    User,
    SavedPhrase as SavedPhraseModel,
    ReviewItem as ReviewItemModel,
    Session as SessionModel,
    Scenario as ScenarioModel,
)
from models.schemas.schemas import (
    SavedPhrase,
    SavedPhraseCreate,
    SavedPhrasesListResponse,
    ConvertToReviewResponse,
    ReviewItem,
)

router = APIRouter()


@router.post("", response_model=SavedPhrase, status_code=status.HTTP_201_CREATED)
def create_saved_phrase(
    payload: SavedPhraseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """改善フレーズを保存する"""
    # 重複チェック（同じセッション・ラウンドの組み合わせで既に保存済みか）
    if payload.session_id and payload.round_index:
        existing = (
            db.query(SavedPhraseModel)
            .filter(
                SavedPhraseModel.user_id == current_user.id,
                SavedPhraseModel.session_id == payload.session_id,
                SavedPhraseModel.round_index == payload.round_index,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This phrase is already saved",
            )

    saved_phrase = SavedPhraseModel(
        user_id=current_user.id,
        phrase=payload.phrase,
        explanation=payload.explanation,
        original_input=payload.original_input,
        session_id=payload.session_id,
        round_index=payload.round_index,
    )

    db.add(saved_phrase)
    db.commit()
    db.refresh(saved_phrase)

    scenario_id = None
    scenario_name = None
    if saved_phrase.session_id:
        row = (
            db.query(SessionModel.scenario_id, ScenarioModel.name)
            .join(ScenarioModel, ScenarioModel.id == SessionModel.scenario_id)
            .filter(SessionModel.id == saved_phrase.session_id)
            .first()
        )
        if row:
            scenario_id = row[0]
            scenario_name = row[1]

    # Return as dict so extra fields are included in the response schema.
    return {
        "id": saved_phrase.id,
        "user_id": saved_phrase.user_id,
        "phrase": saved_phrase.phrase,
        "explanation": saved_phrase.explanation,
        "original_input": saved_phrase.original_input,
        "session_id": saved_phrase.session_id,
        "round_index": saved_phrase.round_index,
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "converted_to_review_id": saved_phrase.converted_to_review_id,
        "created_at": saved_phrase.created_at,
    }


@router.get("", response_model=SavedPhrasesListResponse)
def list_saved_phrases(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存した表現一覧を取得する"""
    query = (
        db.query(
            SavedPhraseModel,
            ScenarioModel.id.label("scenario_id"),
            ScenarioModel.name.label("scenario_name"),
        )
        .outerjoin(SessionModel, SessionModel.id == SavedPhraseModel.session_id)
        .outerjoin(ScenarioModel, ScenarioModel.id == SessionModel.scenario_id)
        .filter(SavedPhraseModel.user_id == current_user.id)
        .order_by(SavedPhraseModel.created_at.desc())
    )

    total_count = query.count()
    rows = query.offset(offset).limit(limit).all()
    saved_phrases = []
    for sp, scenario_id, scenario_name in rows:
        saved_phrases.append(
            {
                "id": sp.id,
                "user_id": sp.user_id,
                "phrase": sp.phrase,
                "explanation": sp.explanation,
                "original_input": sp.original_input,
                "session_id": sp.session_id,
                "round_index": sp.round_index,
                "scenario_id": scenario_id,
                "scenario_name": scenario_name,
                "converted_to_review_id": sp.converted_to_review_id,
                "created_at": sp.created_at,
            }
        )

    return SavedPhrasesListResponse(
        saved_phrases=saved_phrases,
        total_count=total_count,
    )


@router.get("/{saved_phrase_id}", response_model=SavedPhrase)
def get_saved_phrase(
    saved_phrase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存した表現を取得する"""
    saved_phrase = (
        db.query(SavedPhraseModel)
        .filter(
            SavedPhraseModel.id == saved_phrase_id,
            SavedPhraseModel.user_id == current_user.id,
        )
        .first()
    )

    if not saved_phrase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Saved phrase not found"
        )

    return saved_phrase


@router.delete("/{saved_phrase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_phrase(
    saved_phrase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存した表現を削除する"""
    saved_phrase = (
        db.query(SavedPhraseModel)
        .filter(
            SavedPhraseModel.id == saved_phrase_id,
            SavedPhraseModel.user_id == current_user.id,
        )
        .first()
    )

    if not saved_phrase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Saved phrase not found"
        )

    db.delete(saved_phrase)
    db.commit()

    return None


@router.post(
    "/{saved_phrase_id}/convert-to-review", response_model=ConvertToReviewResponse
)
def convert_to_review(
    saved_phrase_id: int,
    current_user: User = Depends(require_pro_user),
    db: Session = Depends(get_db),
):
    """保存した表現を復習アイテムに変換する"""
    saved_phrase = (
        db.query(SavedPhraseModel)
        .filter(
            SavedPhraseModel.id == saved_phrase_id,
            SavedPhraseModel.user_id == current_user.id,
        )
        .first()
    )

    if not saved_phrase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Saved phrase not found"
        )

    # 既に変換済みの場合はエラー
    if saved_phrase.converted_to_review_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This phrase has already been converted to a review item",
        )

    # ReviewItem を作成（翌日に復習予定）
    now = datetime.utcnow()
    review_item = ReviewItemModel(
        user_id=current_user.id,
        phrase=saved_phrase.phrase,
        explanation=saved_phrase.explanation,
        due_at=now + timedelta(days=1),
        is_completed=False,
    )

    db.add(review_item)
    db.flush()  # ID を取得するため

    # SavedPhrase に変換先を記録
    saved_phrase.converted_to_review_id = review_item.id

    db.commit()
    db.refresh(review_item)
    db.refresh(saved_phrase)

    return ConvertToReviewResponse(
        saved_phrase_id=saved_phrase.id,
        review_item=review_item,
    )


@router.get("/check/{session_id}/{round_index}", response_model=SavedPhrase | None)
def check_saved_phrase(
    session_id: int,
    round_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """特定のセッション・ラウンドの保存状態を確認する"""
    saved_phrase = (
        db.query(SavedPhraseModel)
        .filter(
            SavedPhraseModel.user_id == current_user.id,
            SavedPhraseModel.session_id == session_id,
            SavedPhraseModel.round_index == round_index,
        )
        .first()
    )

    return saved_phrase
