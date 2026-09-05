"""Leaf LLM adapter contract — FeatureLLM orchestrates these."""
from __future__ import annotations

from typing import Optional, Protocol


class LLMProvider(Protocol):
    provider_id: str
    model: str

    async def generate_text(self, prompt: str, temperature: Optional[float] = None) -> str: ...

    async def json_completion(self, system_prompt: str, user_prompt: str) -> str: ...
