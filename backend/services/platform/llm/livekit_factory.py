"""Build LiveKit Agents LLM plugins from the same feature routing table."""
from __future__ import annotations

from typing import Any, Union

from config import get_settings
from services.platform.llm.features import LlmFeature, parse_feature
from services.platform.llm.routing import resolve_route
from utils.logger import get_logger

logger = get_logger("LiveKitLlmFactory")


def build_livekit_llm(feature: Union[str, LlmFeature] = "interview_voice") -> Any:
    """Return a LiveKit plugin LLM for AgentSession (not GroqService)."""
    feat = parse_feature(feature)
    route = resolve_route(feat)
    settings = get_settings()

    if route.provider == "groq":
        if not settings.groq_api_key:
            raise RuntimeError(
                f"LiveKit LLM feature={feat.value} provider=groq requires GROQ_API_KEY"
            )
        from livekit.plugins import groq

        logger.info(
            "LiveKit LLM feature=%s provider=groq model=%s",
            feat.value,
            route.model,
        )
        return groq.LLM(model=route.model, api_key=settings.groq_api_key)

    raise RuntimeError(
        f"LiveKit factory: unsupported provider {route.provider!r} for feature {feat.value!r}"
    )
