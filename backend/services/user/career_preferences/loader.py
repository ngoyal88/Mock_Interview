"""Read-only facade for cross-domain consumers (interview, job discovery)."""
from __future__ import annotations

from services.user.career_preferences.models import CareerPreferencesDoc
from services.user.career_preferences.normalize import normalize_doc
from services.user.career_preferences.repository import read_preferences_raw


async def get_career_preferences(uid: str) -> CareerPreferencesDoc:
    raw = await read_preferences_raw(uid)
    return normalize_doc(raw)
