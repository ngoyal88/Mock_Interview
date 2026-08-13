"""Apply server defaults to career preference documents."""
from __future__ import annotations

from typing import Any

from services.user.career_preferences.constants import (
    DEFAULT_EMPLOYMENT_TYPES,
    DEFAULT_EXCLUDE_STAFFING_AGENCIES,
    DEFAULT_LANGUAGE,
    DEFAULT_SALARY_CURRENCY,
    DEFAULT_TAXONOMIES_PRIMARY,
    SCHEMA_VERSION,
    SUPPORTED_COUNTRIES,
)
from services.user.career_preferences.models import CareerPreferencesDoc


def empty_doc_dict() -> dict[str, Any]:
    return CareerPreferencesDoc().model_dump()


def normalize_doc(raw: dict[str, Any] | None) -> CareerPreferencesDoc:
    payload = dict(raw or {})
    if not payload.get("schema_version"):
        payload["schema_version"] = SCHEMA_VERSION
    if not payload.get("taxonomies_primary"):
        payload["taxonomies_primary"] = list(DEFAULT_TAXONOMIES_PRIMARY)
    if not payload.get("language"):
        payload["language"] = DEFAULT_LANGUAGE
    if not payload.get("employment_types"):
        payload["employment_types"] = list(DEFAULT_EMPLOYMENT_TYPES)
    if payload.get("exclude_staffing_agencies") is None:
        payload["exclude_staffing_agencies"] = DEFAULT_EXCLUDE_STAFFING_AGENCIES
    if not payload.get("salary_currency"):
        payload["salary_currency"] = DEFAULT_SALARY_CURRENCY

    # Drop legacy US/UK rows after India-only scope change (do not raise on read).
    for key in ("locations", "exclude_locations"):
        rows = payload.get(key)
        if isinstance(rows, list):
            payload[key] = [
                row
                for row in rows
                if isinstance(row, dict) and str(row.get("country") or "").strip() in SUPPORTED_COUNTRIES
            ]

    return CareerPreferencesDoc.model_validate(payload)
