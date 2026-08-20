"""Pure Meilisearch query builder for Job Discovery."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from services.job_discovery.location_catalog import resolve_location_id
from services.job_discovery.models import SearchFilters
from services.user.career_preferences.models import CareerPreferencesDoc


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _in_filter(field: str, values: Iterable[str]) -> str | None:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    if not cleaned:
        return None
    return f"{field} IN [{', '.join(_quote(value) for value in cleaned)}]"


def _not_in_filter(field: str, values: Iterable[str]) -> str | None:
    inner = _in_filter(field, values)
    return f"NOT {inner}" if inner else None


def _equals_filter(field: str, value: str | None) -> str | None:
    return f"{field} = {_quote(value)}" if value else None


def _visa_index_value(value: str | None) -> str | None:
    """Map API/UI visa intent onto ingest index values (`true`/`false`)."""
    if not value:
        return None
    normalized = value.strip().lower()
    if normalized in {"required", "true", "yes", "1"}:
        return "true"
    if normalized in {"false", "no", "0", "not_required"}:
        return "false"
    return value.strip()


def merge_with_preferences(filters: SearchFilters, prefs: CareerPreferencesDoc) -> SearchFilters:
    data = filters.model_dump()
    if not data["location_ids"] and prefs.locations:
        data["location_ids"] = [
            location_id
            for location in prefs.locations
            if (location_id := resolve_location_id(location.country, location.region, location.city))
        ]
    if not data["work_arrangements"]:
        data["work_arrangements"] = prefs.work_arrangements
    if not data["experience_levels"]:
        data["experience_levels"] = prefs.experience_levels
    if not data["employment_types"]:
        data["employment_types"] = prefs.employment_types
    if not data["industries"]:
        data["industries"] = prefs.target_industries
    if not data["organization_sizes"]:
        data["organization_sizes"] = prefs.company_size_buckets
    if filters.salary_min is None and prefs.salary_min is not None:
        data["salary_min"] = prefs.salary_min
    if filters.salary_max is None and prefs.salary_max is not None:
        data["salary_max"] = prefs.salary_max
    if filters.visa_sponsorship is None and prefs.visa_sponsorship_required:
        data["visa_sponsorship"] = "required"
    if not data.get("exclude_location_ids") and prefs.exclude_locations:
        data["exclude_location_ids"] = [
            location_id
            for location in prefs.exclude_locations
            if (location_id := resolve_location_id(location.country, location.region, location.city))
        ]
    if not data.get("exclude_titles") and prefs.exclude_titles:
        data["exclude_titles"] = [title.strip() for title in prefs.exclude_titles if title.strip()]
    return SearchFilters(**data)


def _salary_filter(filters: SearchFilters) -> str | None:
    clauses: list[str] = []
    if filters.has_salary_only:
        clauses.append("salary_min EXISTS")

    range_clauses: list[str] = []
    if filters.salary_min is not None:
        range_clauses.append(f"salary_max >= {filters.salary_min}")
    if filters.salary_max is not None:
        range_clauses.append(f"salary_min <= {filters.salary_max}")
    if not range_clauses:
        return " AND ".join(clauses) if clauses else None

    hard_range = " AND ".join(range_clauses)
    slack_clauses: list[str] = []
    if filters.salary_min is not None:
        slack_clauses.append(f"salary_max >= {int(filters.salary_min * 0.8)}")
    if filters.salary_max is not None:
        slack_clauses.append(f"salary_min <= {int(filters.salary_max * 1.2)}")
    soft_range = " AND ".join(slack_clauses)
    clauses.append(f"((salary_is_estimated = false AND {hard_range}) OR (salary_is_estimated = true AND {soft_range}))")
    return " AND ".join(clauses)


def build_filter(filters: SearchFilters, *, now: datetime | None = None) -> str:
    clauses = ["status = active"]
    for clause in [
        _in_filter("location_ids", filters.location_ids),
        _in_filter("country_codes", filters.country_codes),
        _in_filter("ai_work_arrangement", filters.work_arrangements),
        _in_filter("ai_experience_level", filters.experience_levels),
        _in_filter("ai_employment_type", filters.employment_types),
        _in_filter("organization_industry", filters.industries),
        _in_filter("organization_size", filters.organization_sizes),
        _in_filter("organization_slug", filters.organization_slugs),
        _equals_filter("ai_visa_sponsorship", _visa_index_value(filters.visa_sponsorship)),
        _salary_filter(filters),
        _not_in_filter("location_ids", filters.exclude_location_ids),
        # ponytail: exact title match only — Meili has no contains-NOT; paraphrased excludes need a later query rewrite.
        _not_in_filter("title", filters.exclude_titles),
    ]:
        if clause:
            clauses.append(clause)

    if filters.posted_within_days:
        cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=filters.posted_within_days)
        clauses.append(f"date_posted_ts >= {int(cutoff.timestamp())}")

    return " AND ".join(clauses)


def build_sort(filters: SearchFilters) -> list[str]:
    if filters.sort == "salary":
        return ["salary_max:desc", "date_posted_ts:desc"]
    return ["date_posted_ts:desc"]

