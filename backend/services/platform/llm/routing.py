"""SSOT: feature → provider/model. Edit this file to change models; restart uvicorn + LiveKit agent.

API keys stay in env (GROQ_API_KEY, LLM_API_KEY, OPENROUTER_API_KEY). Do not put secrets here.

Registered providers: groq | gemini | openrouter
OpenRouter model ids include org prefix, e.g. openai/gpt-4o-mini, anthropic/claude-sonnet-4.
Example:
  LlmFeature.APPLICATION_FIT: LlmRoute(provider="openrouter", model="anthropic/claude-sonnet-4"),
"""
from __future__ import annotations

from dataclasses import dataclass

from services.platform.llm.features import LlmFeature


@dataclass(frozen=True)
class LlmRoute:
    provider: str  # groq | gemini | openrouter
    model: str


_GROQ_STRONG = LlmRoute(provider="groq", model="openai/gpt-oss-120b")
_GROQ_CHEAP = LlmRoute(provider="groq", model="openai/gpt-oss-20b")

FEATURE_ROUTES: dict[LlmFeature, LlmRoute] = {
    LlmFeature.RESUME_PARSE: _GROQ_CHEAP,
    LlmFeature.RESUME_SCORECARD: _GROQ_CHEAP,
    LlmFeature.APPLICATION_FIT: _GROQ_STRONG,
    LlmFeature.VAULT_ANALYZE: _GROQ_STRONG,
    LlmFeature.INTERVIEW_TURN: _GROQ_STRONG,
    LlmFeature.INTERVIEW_VOICE: _GROQ_STRONG,
    LlmFeature.PROFILE_MEMORY: _GROQ_STRONG,
}

# Fixed fallback — never reuse a Groq model id on Gemini.
FALLBACK_ROUTE: LlmRoute | None = LlmRoute(provider="gemini", model="gemini-2.5-flash")


def resolve_route(feature: LlmFeature) -> LlmRoute:
    route = FEATURE_ROUTES.get(feature)
    if route is None:
        raise ValueError(f"No LLM route configured for feature {feature.value!r}")
    return route
