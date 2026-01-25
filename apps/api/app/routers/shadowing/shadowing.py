"""
シャドーイング機能のAPIエンドポイント
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, get_current_user
from models.database.models import (
    User,
    Scenario,
    ShadowingSentence,
    UserShadowingProgress,
)
from models.schemas.schemas import (
    ScenarioShadowingResponse,
    ShadowingSentence as ShadowingSentenceSchema,
    ShadowingUserProgress,
    ShadowingAttemptRequest,
    ShadowingAttemptResponse,
    ShadowingProgressResponse,
    ScenarioProgressSummary,
)

router = APIRouter()


@router.get("/scenarios/{scenario_id}", response_model=ScenarioShadowingResponse)
def get_scenario_shadowing(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    指定シナリオのシャドーイング文一覧を取得

    - シナリオに紐づく全てのシャドーイング文を返す
    - ユーザーの進捗情報も含む
    """
    # シナリオの存在確認
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    # シャドーイング文を取得
    sentences = (
        db.query(ShadowingSentence)
        .filter(ShadowingSentence.scenario_id == scenario_id)
        .order_by(ShadowingSentence.order_index)
        .all()
    )

    # ユーザーの進捗を取得
    sentence_ids = [s.id for s in sentences]
    progress_records = (
        db.query(UserShadowingProgress)
        .filter(
            UserShadowingProgress.user_id == current_user.id,
            UserShadowingProgress.shadowing_sentence_id.in_(sentence_ids),
        )
        .all()
    )
    progress_map = {p.shadowing_sentence_id: p for p in progress_records}

    # レスポンス用にデータを整形
    result_sentences: List[ShadowingSentenceSchema] = []
    completed_count = 0

    for sentence in sentences:
        progress = progress_map.get(sentence.id)
        user_progress = None
        if progress:
            user_progress = ShadowingUserProgress(
                attempt_count=progress.attempt_count,
                best_score=progress.best_score,
                is_completed=progress.is_completed,
                last_practiced_at=progress.last_practiced_at,
            )
            if progress.is_completed:
                completed_count += 1

        result_sentences.append(
            ShadowingSentenceSchema(
                id=sentence.id,
                scenario_id=sentence.scenario_id,
                key_phrase=sentence.key_phrase,
                sentence_en=sentence.sentence_en,
                sentence_ja=sentence.sentence_ja,
                order_index=sentence.order_index,
                difficulty=sentence.difficulty.value if hasattr(sentence.difficulty, 'value') else sentence.difficulty,
                audio_url=sentence.audio_url,
                user_progress=user_progress,
            )
        )

    return ScenarioShadowingResponse(
        scenario_id=scenario_id,
        scenario_name=scenario.name,
        sentences=result_sentences,
        total_sentences=len(sentences),
        completed_count=completed_count,
    )


@router.post("/{sentence_id}/attempt", response_model=ShadowingAttemptResponse)
def record_shadowing_attempt(
    sentence_id: int,
    request: ShadowingAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    シャドーイング練習結果を記録

    - スコアを記録し、進捗を更新
    - 80点以上で完了とみなす
    """
    # シャドーイング文の存在確認
    sentence = (
        db.query(ShadowingSentence)
        .filter(ShadowingSentence.id == sentence_id)
        .first()
    )
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shadowing sentence not found",
        )

    # 既存の進捗を取得または新規作成
    progress = (
        db.query(UserShadowingProgress)
        .filter(
            UserShadowingProgress.user_id == current_user.id,
            UserShadowingProgress.shadowing_sentence_id == sentence_id,
        )
        .first()
    )

    is_new_best = False
    if not progress:
        progress = UserShadowingProgress(
            user_id=current_user.id,
            shadowing_sentence_id=sentence_id,
            attempt_count=0,
            best_score=None,
            is_completed=False,
        )
        db.add(progress)

    # 進捗を更新
    progress.attempt_count += 1
    progress.last_practiced_at = datetime.utcnow()

    # ベストスコアを更新
    if progress.best_score is None or request.score > progress.best_score:
        progress.best_score = request.score
        is_new_best = True

    # 80点以上で完了とみなす
    if request.score >= 80:
        progress.is_completed = True

    db.commit()
    db.refresh(progress)

    return ShadowingAttemptResponse(
        shadowing_sentence_id=sentence_id,
        attempt_count=progress.attempt_count,
        best_score=progress.best_score,
        is_completed=progress.is_completed,
        is_new_best=is_new_best,
    )


@router.get("/progress", response_model=ShadowingProgressResponse)
def get_shadowing_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    シャドーイング全体の進捗を取得（ホーム画面用）

    - 全シナリオ数、練習したシナリオ数
    - 全シャドーイング文数、完了した文数
    - 今日の練習回数
    - 最近練習したシナリオ一覧
    """
    # 全シナリオ数（シャドーイング文があるもののみ）
    scenarios_with_shadowing = (
        db.query(Scenario.id)
        .join(ShadowingSentence)
        .distinct()
        .all()
    )
    total_scenarios = len(scenarios_with_shadowing)

    # 全シャドーイング文数
    total_sentences = db.query(ShadowingSentence).count()

    # ユーザーの進捗データを取得
    user_progress = (
        db.query(UserShadowingProgress)
        .filter(UserShadowingProgress.user_id == current_user.id)
        .all()
    )

    # 練習したシナリオ数と完了した文数を計算
    practiced_sentence_ids = {p.shadowing_sentence_id for p in user_progress}
    completed_sentences = sum(1 for p in user_progress if p.is_completed)

    # 練習したシナリオIDを取得
    practiced_scenarios = set()
    if practiced_sentence_ids:
        sentences_with_scenario = (
            db.query(ShadowingSentence.scenario_id)
            .filter(ShadowingSentence.id.in_(practiced_sentence_ids))
            .distinct()
            .all()
        )
        practiced_scenarios = {s[0] for s in sentences_with_scenario}

    # 今日の練習回数
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_practice_count = sum(
        1 for p in user_progress
        if p.last_practiced_at and p.last_practiced_at >= today_start
    )

    # 最近練習したシナリオ（最大5件）
    recent_scenarios: List[ScenarioProgressSummary] = []

    if practiced_scenarios:
        # 各シナリオごとの進捗を計算
        for scenario_id in practiced_scenarios:
            scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
            if not scenario:
                continue

            # シナリオのシャドーイング文数
            scenario_sentences = (
                db.query(ShadowingSentence)
                .filter(ShadowingSentence.scenario_id == scenario_id)
                .all()
            )
            scenario_sentence_ids = [s.id for s in scenario_sentences]

            # ユーザーの進捗
            scenario_progress = [
                p for p in user_progress
                if p.shadowing_sentence_id in scenario_sentence_ids
            ]
            completed_in_scenario = sum(1 for p in scenario_progress if p.is_completed)
            last_practiced = max(
                (p.last_practiced_at for p in scenario_progress if p.last_practiced_at),
                default=None,
            )

            progress_percent = (
                int(completed_in_scenario / len(scenario_sentences) * 100)
                if scenario_sentences else 0
            )

            recent_scenarios.append(
                ScenarioProgressSummary(
                    scenario_id=scenario_id,
                    scenario_name=scenario.name,
                    category=scenario.category.value if hasattr(scenario.category, 'value') else scenario.category,
                    difficulty=scenario.difficulty.value if hasattr(scenario.difficulty, 'value') else scenario.difficulty,
                    total_sentences=len(scenario_sentences),
                    completed_sentences=completed_in_scenario,
                    progress_percent=progress_percent,
                    last_practiced_at=last_practiced,
                )
            )

        # 最終練習日時でソートして上位5件
        recent_scenarios.sort(
            key=lambda x: x.last_practiced_at or datetime.min,
            reverse=True,
        )
        recent_scenarios = recent_scenarios[:5]

    return ShadowingProgressResponse(
        total_scenarios=total_scenarios,
        practiced_scenarios=len(practiced_scenarios),
        total_sentences=total_sentences,
        completed_sentences=completed_sentences,
        today_practice_count=today_practice_count,
        recent_scenarios=recent_scenarios,
    )


@router.get("/scenarios", response_model=List[ScenarioProgressSummary])
def get_all_scenarios_with_progress(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    全シナリオのシャドーイング進捗一覧を取得

    - オプションでカテゴリフィルタ可能
    """
    # シャドーイング文があるシナリオを取得
    query = (
        db.query(Scenario)
        .join(ShadowingSentence)
        .distinct()
    )

    if category:
        query = query.filter(Scenario.category == category)

    scenarios = query.order_by(Scenario.id).all()

    # ユーザーの全進捗を取得
    user_progress = (
        db.query(UserShadowingProgress)
        .filter(UserShadowingProgress.user_id == current_user.id)
        .all()
    )
    progress_by_sentence = {p.shadowing_sentence_id: p for p in user_progress}

    result: List[ScenarioProgressSummary] = []

    for scenario in scenarios:
        # シナリオのシャドーイング文
        sentences = (
            db.query(ShadowingSentence)
            .filter(ShadowingSentence.scenario_id == scenario.id)
            .all()
        )

        completed_count = 0
        last_practiced = None

        for sentence in sentences:
            progress = progress_by_sentence.get(sentence.id)
            if progress:
                if progress.is_completed:
                    completed_count += 1
                if progress.last_practiced_at:
                    if last_practiced is None or progress.last_practiced_at > last_practiced:
                        last_practiced = progress.last_practiced_at

        progress_percent = (
            int(completed_count / len(sentences) * 100)
            if sentences else 0
        )

        result.append(
            ScenarioProgressSummary(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                category=scenario.category.value if hasattr(scenario.category, 'value') else scenario.category,
                difficulty=scenario.difficulty.value if hasattr(scenario.difficulty, 'value') else scenario.difficulty,
                total_sentences=len(sentences),
                completed_sentences=completed_count,
                progress_percent=progress_percent,
                last_practiced_at=last_practiced,
            )
        )

    return result
