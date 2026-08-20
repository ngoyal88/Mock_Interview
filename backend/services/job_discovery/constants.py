"""Constants for Job Discovery."""
from __future__ import annotations

from services.platform.reference.enums import (
    COUNTRY_NAME_TO_CODE,
    DEFAULT_EMPLOYMENT_TYPE,
    DEFAULT_TAXONOMIES_PRIMARY,
    SUPPORTED_COUNTRY_CODES,
    primary_supported_country,
)

INDEX_NAME = "jobs"
INGEST_RUNS_COLLECTION = "job_discovery_ingest_runs"
DEMAND_SNAPSHOTS_COLLECTION = "job_discovery_demand_snapshots"
JOBS_COLLECTION = "jobs"
SAVED_JOBS_COLLECTION = "saved_jobs"

STALE_UNSEEN_DAYS = 7
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 50
DEFAULT_FRESHNESS_WINDOW_DAYS = 14
DESCRIPTION_MAX_CHARS = 32_000

# Re-export platform geography (product SSOT).
SUPPORTED_COUNTRY_NAMES = COUNTRY_NAME_TO_CODE

INGEST_DEFAULTS = {
    "description_format": "text",
    "include_basic_organization_details": "true",
    "organization_agency": "exclude",
    "ai_language": "English",
    "ai_employment_type": DEFAULT_EMPLOYMENT_TYPE,
    "ai_taxonomies_a_primary": ",".join(DEFAULT_TAXONOMIES_PRIMARY),
    "location": primary_supported_country(),
}

SEARCHABLE_ATTRIBUTES = ["title", "organization_name", "ai_key_skills"]
FILTERABLE_ATTRIBUTES = [
    "location_ids",
    "country_codes",
    "ai_work_arrangement",
    "ai_experience_level",
    "ai_employment_type",
    "salary_min",
    "salary_max",
    "salary_is_estimated",
    "organization_industry",
    "organization_size",
    "organization_slug",
    "ai_visa_sponsorship",
    "status",
    "date_posted_ts",
    "title",
]
SORTABLE_ATTRIBUTES = ["date_posted_ts", "salary_max"]
RANKING_RULES = ["words", "sort", "typo", "proximity", "attribute", "exactness"]
