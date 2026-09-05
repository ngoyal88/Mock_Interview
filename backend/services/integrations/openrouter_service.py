# NOTE: OpenRouter adapter for platform FeatureLLM (OpenAI-compatible chat + JSON).
"""OpenRouter: https://openrouter.ai/api/v1/chat/completions (OpenAI-compatible).

Auth: Bearer OPENROUTER_API_KEY.
Optional attribution headers: HTTP-Referer, X-OpenRouter-Title.
Model ids include org prefix, e.g. openai/gpt-4o, anthropic/claude-sonnet-4.
"""
from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Optional

import httpx

from config import get_settings
from utils.logger import get_logger

logger = get_logger("OpenRouterService")

_OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
_DEFAULT_TIMEOUT_S = 60.0


class OpenRouterService:
    """Leaf LLM adapter — use via registry provider id `openrouter`."""

    provider_id = "openrouter"

    def __init__(self, *, model: str, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.model = (model or "").strip()
        if not self.model:
            raise ValueError("OpenRouter model is required (e.g. openai/gpt-4o-mini)")
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        self._api_key = api_key if api_key is not None else settings.openrouter_api_key
        self._http_referer = (getattr(settings, "openrouter_http_referer", None) or "").strip()
        self._app_title = (getattr(settings, "openrouter_app_title", None) or "").strip() or "Vetta.ai"
        if not self._api_key:
            logger.error("OpenRouter API key not configured")

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if self._http_referer:
            headers["HTTP-Referer"] = self._http_referer
        if self._app_title:
            headers["X-OpenRouter-Title"] = self._app_title
        return headers

    def _extract_content(self, payload: dict[str, Any]) -> str:
        choices = payload.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            # Some models return multimodal content parts
            parts: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(str(part.get("text") or ""))
                elif isinstance(part, str):
                    parts.append(part)
            return "".join(parts)
        return ""

    async def generate_text(self, prompt: str, temperature: Optional[float] = None) -> str:
        if not self._api_key:
            return "LLM service not configured"
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT_S) as client:
                response = await client.post(
                    _OPENROUTER_CHAT_URL,
                    headers=self._headers(),
                    json=body,
                )
                response.raise_for_status()
                payload = response.json()
            text = self._extract_content(payload if isinstance(payload, dict) else {})
            return text or "No response generated"
        except Exception as e:
            logger.error("OpenRouter generation error (model=%s): %s", self.model, e, exc_info=True)
            return f"Error generating response: {str(e)}"

    async def generate_text_stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        if not self._api_key:
            yield "LLM service not configured"
            return
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,
        }
        try:
            async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT_S) as client:
                async with client.stream(
                    "POST",
                    _OPENROUTER_CHAT_URL,
                    headers=self._headers(),
                    json=body,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data = line[6:].strip()
                        else:
                            continue
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        choices = chunk.get("choices") or []
                        if not choices:
                            continue
                        delta = (choices[0].get("delta") or {}).get("content")
                        if delta:
                            yield str(delta)
        except Exception as e:
            logger.error("OpenRouter streaming error (model=%s): %s", self.model, e, exc_info=True)
            yield f"Error generating response: {str(e)}"

    async def json_completion(self, system_prompt: str, user_prompt: str) -> str:
        """JSON via response_format=json_object (OpenAI-compatible path)."""
        if not self._api_key:
            return "{}"

        def _clip(text: str, max_len: int) -> str:
            if not text:
                return ""
            text = text.strip()
            return text if len(text) <= max_len else text[:max_len]

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _clip(system_prompt, 12000)},
                {"role": "user", "content": _clip(user_prompt, 24000)},
            ],
            "temperature": 0.0,
            "max_tokens": min(4096, int(self.max_tokens or 4096)),
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        try:
            async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT_S) as client:
                response = await client.post(
                    _OPENROUTER_CHAT_URL,
                    headers=self._headers(),
                    json=body,
                )
                response.raise_for_status()
                payload = response.json()
            text = self._extract_content(payload if isinstance(payload, dict) else {})
            return (text or "").strip() or "{}"
        except Exception as e:
            logger.error(
                "OpenRouter JSON completion error (model=%s): %s",
                self.model,
                e,
                exc_info=True,
            )
            return "{}"
