from __future__ import annotations

import random
from typing import List

from models.schemas.schemas import DifficultyLevel

from .types import ConversationProvider, ConversationResponse


MOCK_RESPONSES = {
    DifficultyLevel.BEGINNER: {
        "ai_reply": "That's a great effort! Let's practice together.",
        "feedback_short": "よくできています。シンプルな文で伝えられています。",
        "improved_sentence": "I would like to talk more about this topic.",
        "tags": ["beginner", "encouragement"],
    },
    DifficultyLevel.INTERMEDIATE: {
        "ai_reply": "Nicely expressed! Could you add more details?",
        "feedback_short": "自然な流れです。具体的な情報を足してみましょう。",
        "improved_sentence": "I would appreciate it if you could share more specific information about this topic.",
        "tags": ["intermediate", "expansion"],
    },
    DifficultyLevel.ADVANCED: {
        "ai_reply": "Interesting viewpoint! How would you support that?",
        "feedback_short": "構成がよいです。説得力のある理由を添えてみましょう。",
        "improved_sentence": "I believe this approach could generate long-term benefits for the entire team.",
        "tags": ["advanced", "reasoning"],
    },
}


def _generate_tags(round_index: int, difficulty: DifficultyLevel) -> List[str]:
    base_tags = ["conversation", f"round_{round_index}"]
    difficulty_tag = difficulty.value
    return base_tags + [difficulty_tag, random.choice(["fluency", "grammar", "vocabulary"])]


class MockConversationProvider(ConversationProvider):
    async def generate_response(
        self,
        user_input: str,
        difficulty: DifficultyLevel,
        round_index: int,
        context: List[dict],
    ) -> ConversationResponse:
        response_template = MOCK_RESPONSES.get(difficulty, MOCK_RESPONSES[DifficultyLevel.INTERMEDIATE])
        tags = _generate_tags(round_index, difficulty)
        return ConversationResponse(
            ai_reply=response_template["ai_reply"],
            feedback_short=response_template["feedback_short"][:120],
            improved_sentence=response_template["improved_sentence"],
            tags=tags,
            details={
                "explanation": "文法・語彙の改善ポイントを意識して練習しましょう。",
                "suggestions": [
                    "文末の表現をバリエーション豊富に",
                    "より具体的な情報を追加",
                ],
            },
            scores={
                "pronunciation": random.randint(60, 90),
                "grammar": random.randint(60, 90),
            },
            provider="mock",
            latency_ms=0,
        )

