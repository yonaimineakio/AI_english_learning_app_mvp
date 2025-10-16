from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol

from models.schemas.schemas import DifficultyLevel


@dataclass
class ConversationResponse:
    ai_reply: str
    feedback_short: str
    improved_sentence: str
    tags: List[str]
    details: Optional[dict] = None
    scores: Optional[dict] = None
    latency_ms: Optional[int] = None
    provider: Optional[str] = None


class ConversationProvider(Protocol):
    async def generate_response(
        self,
        user_input: str,
        difficulty: DifficultyLevel,
        round_index: int,
        context: List[dict],
    ) -> ConversationResponse:
        ...

