from __future__ import annotations

import json
import logging
from typing import Any, List, Optional

import httpx

from app.core.config import settings
from app.prompts.review_top_phrases_selection import (
    get_review_top_phrases_selection_prompt,
)

logger = logging.getLogger(__name__)


def _extract_response_text(payload: dict[str, Any]) -> str:
    texts: list[str] = []
    for out in payload.get("output", []):
        for item in out.get("content") or []:
            item_type = item.get("type")
            if item_type in ("output_text", "text"):
                txt = item.get("text")
                if txt:
                    texts.append(txt)
    return "".join(texts).strip()


def _normalize_top_phrases(raw_items: Any) -> Optional[List[dict[str, Any]]]:
    if not isinstance(raw_items, list):
        return None

    normalized: List[dict[str, Any]] = []
    seen_keys: set[tuple[int, str]] = set()

    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        round_index = raw.get("round_index")
        phrase = raw.get("phrase")
        explanation = raw.get("explanation")
        reason = raw.get("reason")
        score = raw.get("score")

        if not isinstance(round_index, int):
            continue
        if not isinstance(phrase, str) or not phrase.strip():
            continue
        if not isinstance(explanation, str) or not explanation.strip():
            continue

        dedupe_key = (round_index, phrase.strip().lower())
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        parsed_score = 0
        if isinstance(score, int):
            parsed_score = score
        elif isinstance(score, str) and score.isdigit():
            parsed_score = int(score)

        if parsed_score < 0:
            parsed_score = 0
        if parsed_score > 100:
            parsed_score = 100

        normalized.append(
            {
                "round_index": round_index,
                "phrase": phrase.strip(),
                "explanation": explanation.strip(),
                "reason": reason.strip() if isinstance(reason, str) else "",
                "score": parsed_score,
            }
        )

    normalized.sort(key=lambda item: item.get("score", 0), reverse=True)
    return normalized[:3]


async def select_top_review_phrases(session_rounds: List[dict[str, Any]]) -> Optional[List[dict[str, Any]]]:
    """
    セッション履歴をもとに復習対象フレーズを選定する。

    Returns:
        list: 正常系（空リストを含む）
        None: API呼び出し失敗やパース失敗（呼び出し元でフォールバック）
    """
    if not session_rounds:
        return []

    if not settings.OPENAI_API_KEY:
        logger.info("Top phrase selection skipped: OPENAI_API_KEY is not configured")
        return None

    prompt = get_review_top_phrases_selection_prompt(session_rounds)
    payload = {
        "model": settings.OPENAI_MODEL_NAME,
        "input": json.dumps([{"role": "user", "content": prompt}], ensure_ascii=False),
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
            logger.warning("Top phrase selection failed: empty response")
            return None

        parsed = json.loads(content)
        normalized = _normalize_top_phrases(parsed.get("top_phrases"))
        if normalized is None:
            logger.warning("Top phrase selection failed: invalid top_phrases payload")
            return None
        return normalized

    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.warning("Top phrase selection failed: %s", exc)
        return None
