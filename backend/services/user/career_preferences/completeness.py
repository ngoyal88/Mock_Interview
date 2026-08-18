"""Pure completeness rules for career preferences."""
from __future__ import annotations

from services.user.career_preferences.constants import INCOMPLETE_MESSAGE, REMOTE_ONLY_ARRANGEMENTS
from services.user.career_preferences.models import CareerPreferencesDoc, CompletenessMeta


def _locations_satisfied(doc: CareerPreferencesDoc) -> bool:
    if len(doc.locations) >= 1:
        return True
    if not doc.work_arrangements:
        return False
    return set(doc.work_arrangements).issubset(REMOTE_ONLY_ARRANGEMENTS)


def evaluate_completeness(doc: CareerPreferencesDoc) -> CompletenessMeta:
    missing: list[str] = []

    if len(doc.target_titles) < 1:
        missing.append("target_titles")
    if len(doc.experience_levels) < 1:
        missing.append("experience_levels")
    if len(doc.work_arrangements) < 1:
        missing.append("work_arrangements")
    if not _locations_satisfied(doc):
        missing.append("locations")

    is_complete = len(missing) == 0
    return CompletenessMeta(
        is_complete=is_complete,
        missing=missing,
        message="" if is_complete else INCOMPLETE_MESSAGE,
    )
