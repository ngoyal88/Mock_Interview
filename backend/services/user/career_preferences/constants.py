"""Career preferences enums, limits, and supported geography (Fantastic.jobs-aligned)."""
from __future__ import annotations

from typing import Final

SCHEMA_VERSION: Final[int] = 1

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

SUPPORTED_COUNTRIES: Final[frozenset[str]] = frozenset(
    {"United States", "United Kingdom", "India"}
)

DEFAULT_TAXONOMIES_PRIMARY: Final[list[str]] = ["Technology", "Software"]
DEFAULT_LANGUAGE: Final[str] = "en"
DEFAULT_EMPLOYMENT_TYPES: Final[list[str]] = ["FULL_TIME"]
DEFAULT_EXCLUDE_STAFFING_AGENCIES: Final[bool] = True
DEFAULT_SALARY_CURRENCY: Final[str] = "USD"

MAX_TARGET_TITLES: Final[int] = 5
MAX_EXCLUDE_TITLES: Final[int] = 10
MAX_LOCATIONS: Final[int] = 10
MAX_EXCLUDE_LOCATIONS: Final[int] = 10
MAX_COMPANY_SLUGS: Final[int] = 20
MAX_INDUSTRIES: Final[int] = 20
MAX_YEARS_EXPERIENCE: Final[int] = 50

INCOMPLETE_MESSAGE: Final[str] = (
    "Your career preferences are incomplete. Jobs and suggestions may not match "
    "what you want until you finish updating them."
)
