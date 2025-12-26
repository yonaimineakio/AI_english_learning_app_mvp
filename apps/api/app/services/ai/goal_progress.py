from __future__ import annotations

import asyncio
import json
import logging
from typing import List

import httpx

from app.core.config import settings
from app.prompts.goal_progress_evaluation import GOAL_PROGRESS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def evaluate_goal_progress(goals: List[str], history: List[dict]) -> List[int]:
    """
    学習ゴールの達成率を判定し、各ゴールごとの 0/1 配列を返す。

    Args:
        goals: 学習ゴールのリスト（最大3件程度）
        history: これまでの会話履歴（round_index, user_input, ai_reply などを含む dict のリスト）
    """
    if not goals:
        return []

    # OpenAIキーが未設定の場合は、常に未達成として扱う
    if not settings.OPENAI_API_KEY:
        return [0] * len(goals)

    # 会話履歴をプレーンテキストに整形
    history_lines: List[str] = []
    for item in history:
        round_index = item.get("round_index")
        user_input = item.get("user_input", "")
        ai_reply = item.get("ai_reply", "")
        prefix = f"Round {round_index}" if round_index is not None else "Round"
        history_lines.append(f"{prefix} - User: {user_input}")
        if ai_reply:
            history_lines.append(f"{prefix} - AI: {ai_reply}")
    history_text = "\n".join(history_lines) if history_lines else "（まだ会話履歴はほとんどありません）"

    goals_text = "\n".join(f"{idx + 1}. {g}" for idx, g in enumerate(goals))

    instruction = (
        GOAL_PROGRESS_SYSTEM_PROMPT
        + "\n\n--- 学習ゴール ---\n"
        + goals_text
        + "\n\n--- これまでの会話履歴（新しい順ではなく、読みやすさ優先でそのまま時系列） ---\n"
        + history_text
    )

    messages = [
        {"role": "system", "content": GOAL_PROGRESS_SYSTEM_PROMPT},
        {"role": "assistant", "content": instruction},
    ]

    payload = {
        "model": settings.OPENAI_MODEL_NAME,
        "input": json.dumps(messages, ensure_ascii=False),
    }

    try:
        async with httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=5.0, read=30.0),
        ) as client:
            response = await client.post(settings.OPENAI_CHAT_COMPLETIONS_URL, json=payload)
            response.raise_for_status()
            data = response.json()

        texts: List[str] = []
        outputs = data.get("output", [])
        for out in outputs:
            contents = out.get("content") or []
            for item in contents:
                t = item.get("type")
                if t in ("output_text", "text"):
                    txt = item.get("text")
                    if txt:
                        texts.append(txt)
        content = "".join(texts).strip()

        logger.info("Goal progress raw response: %s", content)

        # 返ってきたテキストを JSON として解釈する
        parsed = json.loads(content)
        status = parsed.get("goals_status", [])
        if not isinstance(status, list):
            raise ValueError("goals_status is not a list")

        result: List[int] = []
        for v in status:
            try:
                iv = int(v)
            except Exception:
                iv = 0
            result.append(1 if iv == 1 else 0)

        # ゴール数と配列長を合わせる（不足分は0、余分は切り捨て）
        if len(result) < len(goals):
            result.extend([0] * (len(goals) - len(result)))
        elif len(result) > len(goals):
            result = result[: len(goals)]

        return result

    except (httpx.HTTPError, json.JSONDecodeError, ValueError) as exc:
        # 評価失敗時も会話自体は継続できるよう、ログに残して全て未達成扱いにする
        logger.warning("Failed to evaluate goal progress: %s", exc)
        return [0] * len(goals)


