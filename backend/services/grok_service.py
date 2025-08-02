"""
Async wrapper for xAI Grok (OpenAI-compatible API).
"""

from openai import AsyncOpenAI
from config import get_settings
from utils.logger import get_logger

_settings = get_settings()
_log = get_logger("GrokService")


class GrokService:
    """Singleton-style access to Grok chat completions."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=_settings.xai_api_key,
            base_url=_settings.grok_base_url,
        )

    async def chat(self, messages: list[dict], *, temp: float | None = None) -> str:
        """
        messages: [{'role':'system','content':'…'}, {'role':'user','content':'…'}, …]
        Returns the assistant’s content string (stripped).
        """
        try:
            resp = await self.client.chat.completions.create(
                model=_settings.grok_model,
                temperature=temp or _settings.grok_temp,
                max_tokens=_settings.grok_max_tokens,
                stream=False,
                messages=messages,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            _log.error(f"Grok error → {exc}")
            return "Sorry, I ran into a problem generating the response."
