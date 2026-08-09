"""Constants for Job Discovery."""
from __future__ import annotations

INDEX_NAME = "jobs"
INGEST_RUNS_COLLECTION = "job_discovery_ingest_runs"
JOBS_COLLECTION = "jobs"
SAVED_JOBS_COLLECTION = "saved_jobs"

STALE_UNSEEN_DAYS = 7
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 50
DEFAULT_FRESHNESS_WINDOW_DAYS = 14
DESCRIPTION_MAX_CHARS = 32_000

# Product scope: India-first. US/UK intentionally out of inventory for now.
SUPPORTED_COUNTRY_CODES = {"in"}
SUPPORTED_COUNTRY_NAMES = {
    "india": "in",
    "in": "in",
    "bharat": "in",
}

INGEST_DEFAULTS = {
    "description_format": "text",
    "include_basic_organization_details": "true",
    "organization_agency": "exclude",
    "ai_language": "English",
    "ai_employment_type": "FULL_TIME",
    "ai_taxonomies_a_primary": "Technology,Software",
    # Fantastic.jobs location filter — India-only inventory.
    "location": "India",
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
]
SORTABLE_ATTRIBUTES = ["date_posted_ts", "salary_max"]
RANKING_RULES = ["words", "sort", "typo", "proximity", "attribute", "exactness"]

