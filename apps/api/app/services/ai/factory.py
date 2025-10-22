from __future__ import annotations

from typing import List

from app.core.config import settings
from models.schemas.schemas import DifficultyLevel, ScenarioCategory
from .mock_provider import MockConversationProvider
from .openai_provider import OpenAIConversationProvider
from .provider_registry import AIProviderRegistry
from .types import ConversationProvider, ConversationResponse


def initialize_providers() -> None:
    AIProviderRegistry.register("mock", MockConversationProvider)
    if settings.OPENAI_API_KEY:
        AIProviderRegistry.register("openai", OpenAIConversationProvider)
        AIProviderRegistry.set_default(settings.AI_PROVIDER_DEFAULT)
    else:
        AIProviderRegistry.set_default("mock")


async def generate_conversation_response(
    user_input: str,
    difficulty: str,
    scenario_category: str,
    round_index: int,
    context: List[dict],
    provider_name: str | None = None,
) -> ConversationResponse:
    provider_cls = AIProviderRegistry.get_provider(provider_name)
    provider = provider_cls()
    result = await provider.generate_response(
        user_input=user_input,
        difficulty=difficulty,
        scenario_category=scenario_category,
        round_index=round_index,
        context=context,
    )
    if not result.provider:
        result.provider = provider_name or AIProviderRegistry.default_provider()
    return result


initialize_providers()

