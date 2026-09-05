"""Closed set of LLM feature ids — call sites pass these strings into get_platform_llm."""
from __future__ import annotations

from enum import Enum


class LlmFeature(str, Enum):
    RESUME_PARSE = "resume_parse"
    RESUME_SCORECARD = "resume_scorecard"
    APPLICATION_FIT = "application_fit"
    VAULT_ANALYZE = "vault_analyze"
    INTERVIEW_TURN = "interview_turn"
    INTERVIEW_VOICE = "interview_voice"
    PROFILE_MEMORY = "profile_memory"


def parse_feature(raw: str | LlmFeature) -> LlmFeature:
    if isinstance(raw, LlmFeature):
        return raw
    try:
        return LlmFeature(str(raw).strip())
    except ValueError as exc:
        known = ", ".join(f.value for f in LlmFeature)
        raise ValueError(f"Unknown LLM feature {raw!r}; expected one of: {known}") from exc
