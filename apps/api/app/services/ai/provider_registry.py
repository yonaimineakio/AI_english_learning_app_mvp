from __future__ import annotations

from typing import Dict, Type

from .types import ConversationProvider


class AIProviderRegistry:
    """Registry to manage AI providers for conversation generation."""

    _providers: Dict[str, Type[ConversationProvider]] = {}
    _default_provider: str = "mock"

    @classmethod
    def register(cls, name: str, provider_cls: Type[ConversationProvider]) -> None:
        cls._providers[name] = provider_cls

    @classmethod
    def get_provider(cls, name: str | None = None) -> Type[ConversationProvider]:
        provider_name = name or cls._default_provider
        provider_cls = cls._providers.get(provider_name)
        if not provider_cls:
            raise ValueError(f"AI provider '{provider_name}' is not registered")
        return provider_cls

    @classmethod
    def set_default(cls, name: str) -> None:
        if name not in cls._providers:
            raise ValueError(f"AI provider '{name}' is not registered")
        cls._default_provider = name

    @classmethod
    def default_provider(cls) -> str:
        return cls._default_provider

    @classmethod
    def clear(cls) -> None:
        """Reset provider registry (primarily for testing)."""
        cls._providers.clear()
        cls._default_provider = "mock"

