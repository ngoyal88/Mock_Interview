"""Feature-bound LLM facade — resolve routing + orchestrate primary/fallback calls."""
from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Optional, Union

from config import get_settings
from services.platform.llm.features import LlmFeature, parse_feature
from services.platform.llm.protocol import LLMProvider
from services.platform.llm.registry import build_provider_from_route
from services.platform.llm.routing import FALLBACK_ROUTE, resolve_route
from utils.logger import get_logger
from utils.response_validator import process_response

logger = get_logger("FeatureLLM")

_feature_llm_cache: dict[LlmFeature, "FeatureLLM"] = {}
_policy_logged = False


def _log_llm_policy_once() -> None:
    global _policy_logged
    if _policy_logged:
        return
    logger.info(
        "LLM model policy: services/platform/llm/routing.py "
        "(API keys from env: GROQ_API_KEY / LLM_API_KEY / OPENROUTER_API_KEY)"
    )
    _policy_logged = True


class FeatureLLM:
    """Orchestrates generate / generate_raw / generate_stream / json_completion for one feature."""

    def __init__(
        self,
        feature: LlmFeature,
        primary: LLMProvider,
        fallback: Optional[LLMProvider] = None,
    ) -> None:
        self.feature = feature
        self.primary = primary
        self.fallback = fallback

    @property
    def provider_id(self) -> str:
        return getattr(self.primary, "provider_id", type(self.primary).__name__)

    @property
    def model(self) -> str:
        return str(getattr(self.primary, "model", "") or "")

    def _is_retryable_error(self, e: Exception) -> bool:
        code = getattr(e, "status_code", None) or getattr(e, "code", None)
        if code is not None:
            try:
                return int(code) in (429, 500, 503)
            except (ValueError, TypeError):
                pass
        msg = str(e.args[0]) if e.args else str(e)
        return "429" in msg or "500" in msg or "503" in msg or "timeout" in msg.lower()

    def _looks_like_provider_error_text(self, text: str) -> bool:
        t = (text or "").strip().lower()
        if not t:
            return True
        markers = (
            "error generating response",
            "rate limit",
            "rate_limit_exceeded",
            "too many requests",
            "apiconnectionerror",
            "failed to generate llm completion",
            "service not configured",
        )
        return any(m in t for m in markers)

    async def _call_llm_with_fallback(
        self,
        prompt: str,
        temperature: float = 0.7,
        llm: Optional[Any] = None,
        fallback_llm: Optional[Any] = None,
    ) -> str:
        llm = llm if llm is not None else self.primary
        fallback_llm = fallback_llm if fallback_llm is not None else self.fallback
        safe_fallback = (
            "I'm having trouble generating a response right now. "
            "Could you try rephrasing or continuing?"
        )

        async def _try_one(provider_llm: Any, validate: bool = True) -> Optional[str]:
            try:
                raw = await asyncio.wait_for(
                    provider_llm.generate_text(prompt, temperature=temperature),
                    15.0,
                )
                if not raw:
                    return None
                if self._looks_like_provider_error_text(raw):
                    logger.warning("LLM returned provider error-like text; trying fallback")
                    return None
                if validate:
                    return process_response(raw)
                return raw.strip() or None
            except asyncio.TimeoutError:
                logger.warning("LLM call timed out after 15s feature=%s", self.feature.value)
                return None
            except Exception as e:
                if self._is_retryable_error(e):
                    logger.warning("LLM retryable error: %s", e)
                else:
                    logger.error("LLM error: %s", e, exc_info=True)
                return None

        result = await _try_one(llm)
        if result:
            return result
        if fallback_llm and fallback_llm is not llm:
            logger.info(
                "Trying fallback LLM provider feature=%s",
                self.feature.value,
            )
            result = await _try_one(fallback_llm)
            if result:
                return result
        return safe_fallback

    async def _call_llm_raw_with_fallback(
        self,
        prompt: str,
        temperature: float = 0.0,
        llm: Optional[Any] = None,
        fallback_llm: Optional[Any] = None,
        empty_fallback: str = "{}",
    ) -> str:
        llm = llm if llm is not None else self.primary
        fallback_llm = fallback_llm if fallback_llm is not None else self.fallback

        async def _try_one(provider_llm: Any) -> Optional[str]:
            try:
                raw = await asyncio.wait_for(
                    provider_llm.generate_text(prompt, temperature=temperature),
                    15.0,
                )
                if self._looks_like_provider_error_text(raw or ""):
                    logger.warning("LLM returned provider error-like text; trying fallback")
                    return None
                return (raw or "").strip() or None
            except asyncio.TimeoutError:
                logger.warning("LLM call timed out after 15s feature=%s", self.feature.value)
                return None
            except Exception as e:
                if self._is_retryable_error(e):
                    logger.warning("LLM retryable error: %s", e)
                else:
                    logger.error("LLM error: %s", e, exc_info=True)
                return None

        result = await _try_one(llm)
        if result:
            return result
        if fallback_llm and fallback_llm is not llm:
            result = await _try_one(fallback_llm)
            if result:
                return result
        return empty_fallback

    async def _call_json_completion_with_fallback(
        self,
        system_prompt: str,
        user_prompt: str,
        llm: Optional[Any] = None,
        fallback_llm: Optional[Any] = None,
        empty_fallback: str = "{}",
    ) -> str:
        llm = llm if llm is not None else self.primary
        fallback_llm = fallback_llm if fallback_llm is not None else self.fallback

        async def _try_one(provider_llm: Any) -> Optional[str]:
            try:
                if hasattr(provider_llm, "json_completion"):
                    raw = await asyncio.wait_for(
                        provider_llm.json_completion(system_prompt, user_prompt),
                        15.0,
                    )
                else:
                    raw = await asyncio.wait_for(
                        provider_llm.generate_text(
                            f"{system_prompt}\n\n{user_prompt}",
                            temperature=0.0,
                        ),
                        15.0,
                    )
                if self._looks_like_provider_error_text(raw or ""):
                    logger.warning("LLM returned provider error-like text; trying fallback")
                    return None
                return (raw or "").strip() or None
            except asyncio.TimeoutError:
                logger.warning(
                    "LLM json_completion timed out after 15s feature=%s",
                    self.feature.value,
                )
                return None
            except Exception as e:
                if self._is_retryable_error(e):
                    logger.warning("LLM retryable error: %s", e)
                else:
                    logger.error("LLM error: %s", e, exc_info=True)
                return None

        result = await _try_one(llm)
        if result:
            return result
        if fallback_llm and fallback_llm is not llm:
            logger.info(
                "Trying fallback LLM provider for json_completion feature=%s",
                self.feature.value,
            )
            result = await _try_one(fallback_llm)
            if result:
                return result
        return empty_fallback

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        return await self._call_llm_with_fallback(prompt, temperature)

    async def generate_raw(
        self,
        prompt: str,
        temperature: float = 0.0,
        *,
        llm: Optional[Any] = None,
        fallback_llm: Optional[Any] = None,
        empty_fallback: str = "{}",
    ) -> str:
        return await self._call_llm_raw_with_fallback(
            prompt, temperature, llm, fallback_llm, empty_fallback
        )

    async def generate_stream(
        self, prompt: str, temperature: float = 0.8
    ) -> AsyncGenerator[str, None]:
        if hasattr(self.primary, "generate_text_stream"):
            async for chunk in self.primary.generate_text_stream(prompt, temperature=temperature):
                yield chunk
            return
        text = await self._call_llm_with_fallback(prompt, temperature)
        yield (text or "").strip()

    async def json_completion(self, system_prompt: str, user_prompt: str) -> str:
        return await self._call_json_completion_with_fallback(
            system_prompt,
            user_prompt,
            llm=self.primary,
            fallback_llm=self.fallback,
            empty_fallback="{}",
        )


def _build_feature_llm(feature: LlmFeature) -> FeatureLLM:
    settings = get_settings()
    route = resolve_route(feature)
    primary = build_provider_from_route(route)
    fallback: Optional[LLMProvider] = None
    if FALLBACK_ROUTE is not None:
        # Only attach Gemini fallback when key exists and primary is not already that route
        if FALLBACK_ROUTE.provider == "gemini" and settings.llm_api_key:
            if not (
                route.provider == FALLBACK_ROUTE.provider and route.model == FALLBACK_ROUTE.model
            ):
                fallback = build_provider_from_route(FALLBACK_ROUTE)
        elif FALLBACK_ROUTE.provider == "groq" and settings.groq_api_key:
            if not (
                route.provider == FALLBACK_ROUTE.provider and route.model == FALLBACK_ROUTE.model
            ):
                fallback = build_provider_from_route(FALLBACK_ROUTE)
    logger.info(
        "LLM feature=%s provider=%s model=%s fallback=%s",
        feature.value,
        route.provider,
        route.model,
        f"{FALLBACK_ROUTE.provider}/{FALLBACK_ROUTE.model}" if fallback and FALLBACK_ROUTE else "none",
    )
    return FeatureLLM(feature=feature, primary=primary, fallback=fallback)


def get_platform_llm(feature: Union[str, LlmFeature]) -> FeatureLLM:
    """Return a cached FeatureLLM for the given feature id (required)."""
    _log_llm_policy_once()
    feat = parse_feature(feature)
    cached = _feature_llm_cache.get(feat)
    if cached is not None:
        return cached
    built = _build_feature_llm(feat)
    _feature_llm_cache[feat] = built
    return built


def clear_llm_caches() -> None:
    """Test helper — drop FeatureLLM instances so routing/settings changes apply."""
    _feature_llm_cache.clear()


# Back-compat alias for type hints / imports during migration
LLMEngine = FeatureLLM
