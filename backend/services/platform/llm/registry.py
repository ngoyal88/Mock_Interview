"""Build leaf LLM adapters by provider id + model."""
from __future__ import annotations

from typing import Callable

from config import get_settings
from services.integrations.gemini_service import GeminiService
from services.integrations.groq_service import GroqService
from services.integrations.openrouter_service import OpenRouterService
from services.platform.llm.protocol import LLMProvider
from services.platform.llm.routing import LlmRoute


def _build_groq(model: str) -> LLMProvider:
    settings = get_settings()
    return GroqService(model=model, api_key=settings.groq_api_key or None)


def _build_gemini(model: str) -> LLMProvider:
    settings = get_settings()
    return GeminiService(model=model, api_key=settings.llm_api_key or None)


def _build_openrouter(model: str) -> LLMProvider:
    settings = get_settings()
    return OpenRouterService(model=model, api_key=settings.openrouter_api_key or None)


_PROVIDERS: dict[str, Callable[[str], LLMProvider]] = {
    "groq": _build_groq,
    "gemini": _build_gemini,
    "openrouter": _build_openrouter,
}


def build_provider(provider: str, model: str) -> LLMProvider:
    key = (provider or "").strip().lower()
    factory = _PROVIDERS.get(key)
    if factory is None:
        known = ", ".join(sorted(_PROVIDERS))
        raise ValueError(f"Unknown LLM provider {provider!r}; expected one of: {known}")
    return factory(model)


def build_provider_from_route(route: LlmRoute) -> LLMProvider:
    return build_provider(route.provider, route.model)


def registered_providers() -> tuple[str, ...]:
    return tuple(sorted(_PROVIDERS))
