from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol


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
    should_end_session: bool = False


class ConversationProvider(Protocol):
    async def generate_response(
        self,
        user_input: str,
        difficulty: str,
        scenario_category: str,
        round_index: int,
        context: List[dict],
        scenario_id: int | None = None,
        custom_system_prompt: str | None = None,  # カスタムシナリオ用
    ) -> ConversationResponse:
        ...
