from __future__ import annotations

import asyncio
import logging
from typing import List

import httpx

from app.core.config import settings
from models.schemas.schemas import DifficultyLevel

from .types import ConversationProvider, ConversationResponse


logger = logging.getLogger(__name__)

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


SYSTEM_PROMPT = """
You are an English learning conversation AI coach for Japanese learners. Your role is to:
1. Respond naturally to the user's message.
2. Provide a short feedback summary in Japanese within 120 characters.
3. Provide one improved English sentence as a single sentence.

Guidelines:
- Consider conversation context for coherence (up to last 2 turns).
- Adapt response difficulty based on the specified level.
- Avoid personal data and remain concise.
- Provide constructive yet encouraging feedback.
"""


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
        difficulty: DifficultyLevel,
        round_index: int,
        context: List[dict],
    ) -> ConversationResponse:
        start_time = asyncio.get_event_loop().time()
        payload = self._build_request_payload(user_input, difficulty, context)

        try:
            response = await self._client.post(OPENAI_CHAT_COMPLETIONS_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            ai_reply, feedback_short, improved_sentence = self._parse_response(content)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to generate AI response via OpenAI: %s", exc)
            raise

        tags = ["conversation", f"round_{round_index}", difficulty.value]
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

    def _build_request_payload(self, user_input: str, difficulty: DifficultyLevel, context: List[dict]) -> dict:
        difficulty_label = {
            DifficultyLevel.BEGINNER: "beginner",
            DifficultyLevel.INTERMEDIATE: "intermediate",
            DifficultyLevel.ADVANCED: "advanced",
        }[difficulty]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

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
                    f"Difficulty: {difficulty_label}. Respond to the user input. "
                    "Then provide feedback summary in Japanese (max 120 chars) and one improved English sentence.\n"
                    f"User input: {user_input}"
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

