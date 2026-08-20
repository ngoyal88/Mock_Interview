"""Interview mode catalog — startable types, capabilities, HTTP start union.

Owns: LIVE_STARTABLE_TYPES, capabilities, labels, ModeStrategyRegistry, start request union.
Does not own: session persistence, transport, per-mode prepare_start implementations.
Entry: registry exports (see __all__)
"""
from services.interview.catalog.registry import (
    LIVE_STARTABLE_TYPES,
    MODE_CAPABILITIES,
    ModeCapabilities,
    ModeStrategyRegistry,
    get_mode_capabilities,
    get_mode_metadata,
    is_coding_interview_type,
    is_startable_interview_type,
    parse_interview_type,
    require_coding_session,
)

__all__ = [
    "LIVE_STARTABLE_TYPES",
    "MODE_CAPABILITIES",
    "ModeCapabilities",
    "ModeStrategyRegistry",
    "get_mode_capabilities",
    "get_mode_metadata",
    "is_coding_interview_type",
    "is_startable_interview_type",
    "parse_interview_type",
    "require_coding_session",
]
