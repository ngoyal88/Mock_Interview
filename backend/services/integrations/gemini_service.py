# NOTE: Secondary LLM adapter for platform FeatureLLM (Gemini chat + JSON).

from __future__ import annotations

from typing import Optional

import google.generativeai as genai

from config import get_settings
from utils.async_io import run_in_thread
from utils.logger import get_logger

logger = get_logger("GeminiService")


class GeminiService:
    provider_id = "gemini"

    def __init__(self, *, model: str, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.model_name = (model or "").strip() or "gemini-2.5-flash"
        self.model = self.model_name  # FeatureLLM / meta read .model
        key = api_key if api_key is not None else settings.llm_api_key
        if key:
            genai.configure(api_key=key)
            self._client = genai.GenerativeModel(self.model_name)
            logger.info("Gemini service initialized model=%s", self.model_name)
        else:
            logger.error("Gemini API key not configured")
            self._client = None

    async def generate_text(self, prompt: str, temperature: Optional[float] = None) -> str:
        if not self._client:
            return "LLM service not configured"

        settings = get_settings()

        def _call() -> str:
            temp = temperature if temperature is not None else settings.llm_temperature
            response = self._client.generate_content(
                prompt,
                generation_config={
                    "temperature": temp,
                    "max_output_tokens": settings.llm_max_tokens,
                },
            )
            try:
                return response.text if response.text else "No response generated"
            except Exception:
                finish = None
                candidates_len = None
                try:
                    if hasattr(response, "candidates") and response.candidates is not None:
                        candidates_len = len(response.candidates)
                        first = response.candidates[0] if candidates_len else None
                        finish = getattr(first, "finish_reason", None)
                except Exception:
                    pass
                logger.warning(
                    "Gemini returned no text. candidates=%s finish_reason=%s",
                    candidates_len,
                    finish,
                )
                return "No response generated"

        try:
            return await run_in_thread(_call)
        except Exception as e:
            logger.error("Gemini generation error: %s", e, exc_info=True)
            return f"Error generating response: {str(e)}"

    async def json_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Structured JSON via Gemini response_mime_type=application/json."""
        if not self._client:
            return "{}"

        settings = get_settings()
        combined = f"{system_prompt.strip()}\n\n{user_prompt.strip()}"

        def _call() -> str:
            response = self._client.generate_content(
                combined,
                generation_config={
                    "temperature": 0.0,
                    "max_output_tokens": min(4096, int(settings.llm_max_tokens or 4096)),
                    "response_mime_type": "application/json",
                },
            )
            try:
                return (response.text or "").strip() or "{}"
            except Exception:
                logger.warning("Gemini JSON completion returned no text")
                return "{}"

        try:
            return await run_in_thread(_call)
        except Exception as e:
            logger.error(
                "Gemini JSON completion error (model=%s): %s",
                self.model_name,
                e,
                exc_info=True,
            )
            return "{}"
