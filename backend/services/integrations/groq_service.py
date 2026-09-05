# NOTE: Primary LLM adapter for platform FeatureLLM (Groq JSON + chat completions).
import asyncio
import threading
from typing import AsyncGenerator, Optional

from groq import Groq

from config import get_settings
from utils.async_io import run_in_thread
from utils.logger import get_logger

logger = get_logger("GroqService")


class GroqService:
    """Groq LLM client using the official SDK."""

    provider_id = "groq"

    def __init__(self, *, model: str, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        resolved = (model or "").strip()
        if not resolved:
            raise ValueError("GroqService requires a non-empty model id from routing")
        if "guard" in resolved.lower():
            raise ValueError(
                f"Groq model {model!r} is a guard/moderation model; use a chat model from routing.py"
            )
        self.model = resolved
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        key = api_key if api_key is not None else settings.groq_api_key
        if not key:
            logger.error("Groq API key not configured")
            self.client = None
        else:
            self.client = Groq(api_key=key)

    async def generate_text(self, prompt: str, temperature: Optional[float] = None) -> str:
        if not self.client:
            return "LLM service not configured"
        try:

            def _call() -> str:
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    temperature=(temperature if temperature is not None else self.temperature),
                    max_tokens=self.max_tokens,
                    stream=False,
                )
                choice = (chat_completion.choices or [None])[0]
                content = (
                    getattr(choice, "message", None).content
                    if choice and getattr(choice, "message", None)
                    else None
                )
                return content or "No response generated"

            return await run_in_thread(_call)
        except Exception as e:
            logger.error("Groq generation error: %s", e, exc_info=True)
            return f"Error generating response: {str(e)}"

    async def generate_text_stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "LLM service not configured"
            return

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[object] = asyncio.Queue()
        sentinel = object()

        def _run_stream() -> None:
            try:
                stream = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    temperature=(temperature if temperature is not None else self.temperature),
                    max_tokens=self.max_tokens,
                    stream=True,
                )
                for chunk in stream:
                    try:
                        delta = chunk.choices[0].delta.content
                    except Exception:
                        delta = None
                    if delta:
                        loop.call_soon_threadsafe(queue.put_nowait, delta)
            except Exception as e:
                logger.error("Groq streaming error: %s", e, exc_info=True)
                loop.call_soon_threadsafe(queue.put_nowait, e)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, sentinel)

        threading.Thread(target=_run_stream, daemon=True).start()

        while True:
            item = await queue.get()
            if item is sentinel:
                break
            if isinstance(item, Exception):
                yield f"Error generating response: {item}"
                break
            yield str(item)

    async def json_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Generate JSON via Groq with response_format=json_object (uses constructor model)."""
        if not self.client:
            return "{}"

        def _clip(text: str, max_len: int) -> str:
            if not text:
                return ""
            text = text.strip()
            return text if len(text) <= max_len else text[:max_len]

        sys_c = _clip(system_prompt, 12000)
        usr_c = _clip(user_prompt, 24000)
        try:

            def _call() -> str:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": sys_c},
                        {"role": "user", "content": usr_c},
                    ],
                    model=self.model,
                    temperature=0.0,
                    max_tokens=min(4096, int(self.max_tokens or 4096)),
                    stream=False,
                    response_format={"type": "json_object"},
                )
                choice = (chat_completion.choices or [None])[0]
                content = (
                    getattr(choice, "message", None).content
                    if choice and getattr(choice, "message", None)
                    else None
                )
                return content or "{}"

            return await run_in_thread(_call)
        except Exception as e:
            logger.error("Groq JSON completion error (model=%s): %s", self.model, e, exc_info=True)
            return "{}"
