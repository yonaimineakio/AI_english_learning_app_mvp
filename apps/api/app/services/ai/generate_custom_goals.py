"""カスタムシナリオのゴール自動生成（OpenAI API呼び出し）

review_top_phrases.py と同じ httpx → OpenAI → JSON parse パターンで実装。
失敗時は None を返し、呼び出し元でデフォルトゴールにフォールバックする。
"""

from __future__ import annotations

import json
import logging
from typing import Any, List, Optional

import httpx

from app.core.config import settings
from app.prompts.custom_scenario_goals_generation import (
    get_custom_scenario_goals_generation_prompt,
)

logger = logging.getLogger(__name__)


def _extract_response_text(payload: dict[str, Any]) -> str:
    """OpenAI Responses API のレスポンスからテキストを抽出する。"""
    texts: list[str] = []
    for out in payload.get("output", []):
        for item in out.get("content") or []:
            item_type = item.get("type")
            if item_type in ("output_text", "text"):
                txt = item.get("text")
                if txt:
                    texts.append(txt)
    return "".join(texts).strip()


def _normalize_goals(raw: Any) -> Optional[List[str]]:
    """AI応答から goals 配列を検証・正規化する。"""
    if not isinstance(raw, list):
        return None

    goals: List[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            goals.append(item.strip())

    if len(goals) != 3:
        logger.warning("Goal generation returned %d goals (expected 3)", len(goals))
        if len(goals) == 0:
            return None
        # 3つ未満なら足りない分をスキップ（呼び出し元でフォールバック）
        # 3つ超なら先頭3つだけ使う
        if len(goals) > 3:
            goals = goals[:3]

    return goals if goals else None


async def generate_custom_scenario_goals(
    scenario_name: str,
    description: str,
    user_role: str,
    ai_role: str,
) -> Optional[List[str]]:
    """カスタムシナリオのゴールをAIで生成する。

    Args:
        scenario_name: シナリオ名
        description: シナリオの説明
        user_role: ユーザーの役割
        ai_role: AIの役割

    Returns:
        list[str]: 生成されたゴール（3つ）
        None: API呼び出し失敗やパース失敗（呼び出し元でフォールバック）
    """
    if not settings.OPENAI_API_KEY:
        logger.info("Custom goal generation skipped: OPENAI_API_KEY is not configured")
        return None

    prompt = get_custom_scenario_goals_generation_prompt(
        scenario_name=scenario_name,
        description=description,
        user_role=user_role,
        ai_role=ai_role,
    )

    payload = {
        "model": settings.OPENAI_MODEL_NAME,
        "input": json.dumps(
            [{"role": "user", "content": prompt}], ensure_ascii=False
        ),
    }

    try:
        async with httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=5.0, read=30.0),
        ) as client:
            response = await client.post(
                settings.OPENAI_CHAT_COMPLETIONS_URL,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = _extract_response_text(data)
        if not content:
            logger.warning("Custom goal generation failed: empty response")
            return None

        parsed = json.loads(content)
        goals = _normalize_goals(parsed.get("goals"))
        if goals is None:
            logger.warning("Custom goal generation failed: invalid goals payload")
            return None

        logger.info("Custom goals generated: %s", goals)
        return goals

    except (httpx.HTTPError, json.JSONDecodeError, KeyError) as exc:
        logger.warning("Custom goal generation failed: %s", exc)
        return None
