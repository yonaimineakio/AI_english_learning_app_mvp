from __future__ import annotations

import asyncio
import logging
from typing import List

import httpx

from app.core.config import settings
from models.schemas.schemas import DifficultyLevel, ScenarioCategory

from .types import ConversationProvider, ConversationResponse
from app.prompts import get_prompt_by_category_difficulty

logger = logging.getLogger(__name__)

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"



class OpenAIConversationProvider(ConversationProvider):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            timeout=httpx.Timeout(12.0, connect=5.0, read=12.0),
        )

    async def generate_response(
        self,
        user_input: str,
        difficulty: str,
        scenario_category: str,
        round_index: int,
        context: List[dict],
    ) -> ConversationResponse:
        start_time = asyncio.get_event_loop().time()
        payload = self._build_request_payload(user_input, difficulty, scenario_category, context)

        try:
            response = await self._client.post(OPENAI_CHAT_COMPLETIONS_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            ai_reply, feedback_short, improved_sentence = self._parse_response(content)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to generate AI response via OpenAI: %s", exc)
            raise

        tags = ["conversation", f"round_{round_index}", difficulty] + [scenario_category]
        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        details = {"explanation": None, "suggestions": None}
        scores = None

        return ConversationResponse(
            ai_reply=ai_reply,
            feedback_short=feedback_short[:120],
            improved_sentence=improved_sentence,
            tags=tags,
            details=details,
            scores=scores,
            latency_ms=latency_ms,
            provider="openai",
        )

    def _build_request_payload(self, user_input: str, difficulty: str, scenario_category: str, context: List[dict]) -> dict:
        
        system_prompt = get_prompt_by_category_difficulty(scenario_category, difficulty)
        logger.info(f"System prompt: {system_prompt}")
        messages = [{"role": "system", "content": system_prompt}]

        for turn in context[-2:]:  # Include last two rounds as context
            messages.extend(
                [
                    {"role": "user", "content": turn.get("user_input", "")},
                    {"role": "assistant", "content": turn.get("ai_reply", "")},
                ]
            )

        messages.append(
            {
                "role": "user",
                "content": (
                    f"難易度: {difficulty}。ユーザーの入力に応答してください。\n\n"
                    "出力形式を以下のように厳密に守ってください：\n"
                    "AI: [英語での自然な応答のみ]\n"
                    "Feedback: [日本語でのフィードバック要約（最大120文字）]\n"
                    "Improved: [改善された英語文1つ]\n\n"
                    f"ユーザー入力: {user_input}"
                ),
            }
        )

        return {
            "model": settings.OPENAI_MODEL_NAME,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 400,
        }

    def _parse_response(self, content: str) -> tuple[str, str, str]:
        # For this MVP, we expect the LLM to respond in a structured way using delimiters.
        # Example format:
        # AI: ...
        # Feedback: ...
        # Improved: ...
        lines = content.strip().splitlines()
        ai_reply = ""
        feedback_short = ""
        improved_sentence = ""
        for line in lines:
            if line.lower().startswith("ai:"):
                ai_reply = line.split(":", 1)[1].strip()
            elif line.lower().startswith("feedback:"):
                feedback_short = line.split(":", 1)[1].strip()
            elif line.lower().startswith("improved:"):
                improved_sentence = line.split(":", 1)[1].strip()

        if not ai_reply:
            ai_reply = content.strip()
        if not feedback_short:
            feedback_short = "改善点を120字以内で記述してください。"
        if not improved_sentence:
            improved_sentence = "Please provide an improved sentence."

        return ai_reply, feedback_short, improved_sentence

    async def __aenter__(self) -> "OpenAIConversationProvider":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.aclose()


async def warm_up_provider() -> None:
    if not settings.OPENAI_API_KEY:
        return
    provider = OpenAIConversationProvider()
    try:
        await provider.generate_response("Hello", DifficultyLevel.INTERMEDIATE, 1, [])
    except Exception:  # noqa: BLE001
        logger.info("OpenAI warm-up failed (expected if key invalid)" )
    finally:
        await provider._client.aclose()

