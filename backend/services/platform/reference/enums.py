"""Cross-domain closed vocabularies (experience, work mode, employment, geography).

Product SSOT for enums shared by career preferences, job discovery filters, etc.
Provider-specific query phrases (e.g. Fantastic.jobs title terms) do NOT belong here.
"""
from __future__ import annotations

from typing import Final, Optional

WORK_ARRANGEMENTS: Final[frozenset[str]] = frozenset(
    {"On-site", "Hybrid", "Remote OK", "Remote Solely"}
)
REMOTE_ONLY_ARRANGEMENTS: Final[frozenset[str]] = frozenset({"Remote OK", "Remote Solely"})

EXPERIENCE_LEVELS: Final[frozenset[str]] = frozenset({"0-2", "2-5", "5-10", "10+"})

EMPLOYMENT_TYPES: Final[frozenset[str]] = frozenset(
    {
        "FULL_TIME",
        "PART_TIME",
        "CONTRACTOR",
        "TEMPORARY",
        "INTERN",
        "VOLUNTEER",
        "PER_DIEM",
        "OTHER",
    }
)

COMPANY_SIZE_BUCKETS: Final[frozenset[str]] = frozenset(
    {
        "1",
        "2-10",
        "11-50",
        "51-200",
        "201-500",
        "501-1000",
        "1001-5000",
        "5001-10000",
        "10001+",
    }
)

SUPPORTED_COUNTRIES: Final[frozenset[str]] = frozenset({"India"})
SUPPORTED_COUNTRY_CODES: Final[frozenset[str]] = frozenset({"in"})
COUNTRY_NAME_TO_CODE: Final[dict[str, str]] = {
    "india": "in",
    "in": "in",
    "bharat": "in",
}

DEFAULT_TAXONOMIES_PRIMARY: Final[tuple[str, ...]] = ("Technology", "Software")
DEFAULT_EMPLOYMENT_TYPE: Final[str] = "FULL_TIME"
DEFAULT_SALARY_CURRENCY: Final[str] = "INR"
DEFAULT_LANGUAGE: Final[str] = "en"

VISA_FILTER_REQUIRED: Final[str] = "required"


def country_code_for_name(name: str) -> Optional[str]:
    """Resolve a display name or alias to ISO country code."""
    key = name.strip().casefold()
    if not key:
        return None
    return COUNTRY_NAME_TO_CODE.get(key)


def primary_supported_country() -> str:
    """Stable single-country product location string for ingest defaults."""
    return sorted(SUPPORTED_COUNTRIES)[0]
