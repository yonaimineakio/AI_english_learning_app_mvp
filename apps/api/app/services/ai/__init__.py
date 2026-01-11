"""AI service package.

This package exposes convenience functions via lazy imports to avoid importing
all providers (and their optional dependencies) at module import time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .factory import generate_conversation_response, initialize_providers

__all__ = ["generate_conversation_response", "initialize_providers"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from . import factory

        return getattr(factory, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
