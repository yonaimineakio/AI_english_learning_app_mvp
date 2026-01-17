from __future__ import annotations

from typing import List, Type

from app.core.config import settings
from models.schemas.schemas import DifficultyLevel, ScenarioCategory
from .mock_provider import MockConversationProvider
from .openai_provider import OpenAIConversationProvider
from .groq_provider import GroqConversationProvider
from .provider_registry import AIProviderRegistry
from .types import ConversationProvider, ConversationResponse
import httpx


def initialize_providers() -> None:
    AIProviderRegistry.register("mock", MockConversationProvider)
    if settings.OPENAI_API_KEY:
        AIProviderRegistry.register("openai", OpenAIConversationProvider)
    if settings.GROQ_API_KEY:
        AIProviderRegistry.register("groq", GroqConversationProvider)
    # フォールバック用にデフォルトをmockに設定
    AIProviderRegistry.set_default("mock")


async def generate_conversation_response(
    user_input: str,
    difficulty: str,
    scenario_category: str,
    round_index: int,
    context: List[dict],
    scenario_id: int | None = None,
    provider_name: str | None = None,
) -> ConversationResponse:
    provider_cls: Type[ConversationProvider] = AIProviderRegistry.get_provider(
        provider_name
    )

    try:
        provider = provider_cls()
        result = await provider.generate_response(
            user_input=user_input,
            difficulty=difficulty,
            scenario_category=scenario_category,
            round_index=round_index,
            context=context,
            scenario_id=scenario_id,
        )
        if not result.provider:
            result.provider = provider_name or AIProviderRegistry.default_provider()
        return result
    except httpx.HTTPError as exc:
        # OpenAI など外部API呼び出しの失敗時は、モックプロバイダにフォールバックして
        # セッション自体は継続できるようにする。
        # provider_name 明示指定時はそのまま例外を投げる。
        if provider_name is not None:
            raise

        default_name = AIProviderRegistry.default_provider()
        if default_name == "openai" or default_name == "groq":
            # OpenAI失敗時はログだけ残してMockへフォールバック
            from .mock_provider import (
                MockConversationProvider,
            )  # ローカルimportで循環依存を回避

            fallback_provider: ConversationProvider = MockConversationProvider()
            fallback = await fallback_provider.generate_response(
                user_input=user_input,
                difficulty=difficulty,
                scenario_category=scenario_category,
                round_index=round_index,
                context=context,
                scenario_id=scenario_id,
            )
            if not fallback.provider:
                fallback.provider = "mock"
            return fallback

        # それ以外（デフォルトがmockなど）の場合は従来通り例外を伝播
        raise


initialize_providers()
