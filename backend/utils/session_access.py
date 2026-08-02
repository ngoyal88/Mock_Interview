"""Fail-closed session ownership checks for interview Redis sessions."""
from __future__ import annotations

from typing import Any, Dict, Optional

from utils.domain_errors import DomainError


def require_session_owner(session_data: Optional[Dict[str, Any]], uid: str) -> Dict[str, Any]:
    """
    Ensure the authenticated user owns the session.

    All interview routes that read Redis session state must call this helper.
    Missing owner fields are treated as unauthorized (403), not public access.
    """
    if not session_data:
        raise DomainError("session_not_found", "Session not found")

    owner = session_data.get("user_id") or session_data.get("uid")
    if not owner:
        raise DomainError("session_owner_missing", "Session ownership could not be verified")

    if str(owner) != str(uid):
        raise DomainError("session_forbidden", "Not authorized for this session")

    return session_data
