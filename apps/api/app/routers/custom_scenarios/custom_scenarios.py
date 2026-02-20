"""Custom Scenarios router - オリジナルシナリオのCRUD操作"""

from __future__ import annotations

import logging
from datetime import datetime, date
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user, get_db
from app.services.ai.generate_custom_goals import generate_custom_scenario_goals
from models.database.models import (
    User,
    CustomScenario as CustomScenarioModel,
)
from models.schemas.schemas import (
    CustomScenario,
    CustomScenarioCreate,
    CustomScenarioListResponse,
    CustomScenarioLimitResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# 日次制限
FREE_USER_DAILY_LIMIT = 1
PRO_USER_DAILY_LIMIT = 5

# タイムゾーン（JST）
JST = ZoneInfo("Asia/Tokyo")


def get_today_jst() -> date:
    """JSTの今日の日付を取得"""
    return datetime.now(JST).date()


def get_created_today_count(db: Session, user_id: str) -> int:
    """本日作成されたカスタムシナリオ数をカウント"""
    today = get_today_jst()
    # JSTの今日の開始時刻と終了時刻を計算
    today_start = datetime(today.year, today.month, today.day, tzinfo=JST)
    tomorrow_start = datetime(today.year, today.month, today.day, tzinfo=JST)
    tomorrow_start = today_start.replace(day=today.day + 1) if today.day < 28 else today_start

    # SQLiteとPostgreSQL両対応で日付部分を比較
    count = (
        db.query(func.count(CustomScenarioModel.id))
        .filter(
            CustomScenarioModel.user_id == user_id,
            func.date(CustomScenarioModel.created_at) == today,
        )
        .scalar()
    )
    return count or 0


@router.get("/limit", response_model=CustomScenarioLimitResponse)
def get_creation_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """本日の作成制限情報を取得"""
    is_pro = getattr(current_user, "is_pro", False)
    daily_limit = PRO_USER_DAILY_LIMIT
    created_today = get_created_today_count(db, current_user.id)
    remaining = max(0, daily_limit - created_today) if is_pro else 0

    return CustomScenarioLimitResponse(
        daily_limit=daily_limit,
        created_today=created_today,
        remaining=remaining,
        is_pro=is_pro,
    )


@router.post("", response_model=CustomScenario, status_code=status.HTTP_201_CREATED)
async def create_custom_scenario(
    payload: CustomScenarioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """オリジナルシナリオを作成する"""
    # Proユーザーのみ作成可能
    is_pro = getattr(current_user, "is_pro", False)
    if not is_pro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="オリジナルシナリオの作成はProユーザー限定の機能です。",
        )

    # 日次制限チェック
    daily_limit = PRO_USER_DAILY_LIMIT
    created_today = get_created_today_count(db, current_user.id)

    if created_today >= daily_limit:
        limit_type = "Pro" if is_pro else "無料"
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"{limit_type}ユーザーは1日{daily_limit}個までシナリオを作成できます。明日また作成してください。",
        )

    # AIでゴールを自動生成（失敗時は None → デフォルトゴールにフォールバック）
    goals = None
    try:
        goals = await generate_custom_scenario_goals(
            scenario_name=payload.name,
            description=payload.description,
            user_role=payload.user_role,
            ai_role=payload.ai_role,
        )
    except Exception as exc:
        logger.warning("Custom goal generation failed, using default: %s", exc)

    # シナリオ作成
    custom_scenario = CustomScenarioModel(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        user_role=payload.user_role,
        ai_role=payload.ai_role,
        goals=goals,
        difficulty="intermediate",  # 固定
        is_active=True,
    )

    db.add(custom_scenario)
    db.commit()
    db.refresh(custom_scenario)

    return custom_scenario


@router.get("", response_model=CustomScenarioListResponse)
def list_custom_scenarios(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """自分のオリジナルシナリオ一覧を取得する"""
    query = (
        db.query(CustomScenarioModel)
        .filter(
            CustomScenarioModel.user_id == current_user.id,
            CustomScenarioModel.is_active == True,
        )
        .order_by(CustomScenarioModel.created_at.desc())
    )

    total_count = query.count()
    custom_scenarios = query.offset(offset).limit(limit).all()

    return CustomScenarioListResponse(
        custom_scenarios=custom_scenarios,
        total_count=total_count,
    )


@router.get("/{custom_scenario_id}", response_model=CustomScenario)
def get_custom_scenario(
    custom_scenario_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """オリジナルシナリオを取得する"""
    custom_scenario = (
        db.query(CustomScenarioModel)
        .filter(
            CustomScenarioModel.id == custom_scenario_id,
            CustomScenarioModel.user_id == current_user.id,
        )
        .first()
    )

    if not custom_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom scenario not found",
        )

    return custom_scenario


@router.delete("/{custom_scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_custom_scenario(
    custom_scenario_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """オリジナルシナリオを削除する（論理削除）"""
    custom_scenario = (
        db.query(CustomScenarioModel)
        .filter(
            CustomScenarioModel.id == custom_scenario_id,
            CustomScenarioModel.user_id == current_user.id,
        )
        .first()
    )

    if not custom_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom scenario not found",
        )

    # 論理削除（is_active = False）
    custom_scenario.is_active = False
    db.commit()

    return None
