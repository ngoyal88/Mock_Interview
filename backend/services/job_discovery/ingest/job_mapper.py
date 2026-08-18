"""Map Fantastic.jobs payloads into Job Discovery documents."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional

from config import get_settings
from services.job_discovery.constants import DESCRIPTION_MAX_CHARS
from services.job_discovery.models import JobDocument


def _first(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = raw.get(key)
        if value not in (None, ""):
            return value
    return None


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = _string(value)
    if not text:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def _list_of_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[,;\n]", value) if part.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _int_or_none(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def _salary(raw: dict[str, Any]) -> tuple[Optional[int], Optional[int], Optional[str], bool]:
    salary = raw.get("salary") or raw.get("ai_salary") or {}
    if isinstance(salary, dict):
        minimum = _int_or_none(_first(salary, "min", "minimum", "salary_min"))
        maximum = _int_or_none(_first(salary, "max", "maximum", "salary_max"))
        raw_text = _first(salary, "raw", "text", "display")
    else:
        minimum = _int_or_none(_first(raw, "ai_salary_min", "salary_min"))
        maximum = _int_or_none(_first(raw, "ai_salary_max", "salary_max"))
        raw_text = salary if isinstance(salary, str) else _first(raw, "salary_raw")
    raw_salary = _string(raw_text) or None
    return minimum, maximum, raw_salary, raw_salary is None


def _organization(raw: dict[str, Any]) -> dict[str, Any]:
    org = raw.get("organization") if isinstance(raw.get("organization"), dict) else {}
    return {
        "name": _first(raw, "organization_name", "org_linkedin_name", "company_name") or _first(org, "name", "linkedin_name"),
        "slug": _first(raw, "organization_slug", "org_linkedin_slug") or _first(org, "slug", "linkedin_slug"),
        "industry": _first(raw, "organization_industry") or _first(org, "industry"),
        "size": _first(raw, "organization_size") or _first(org, "size"),
        "logo": _first(raw, "org_logo_permalink", "organization_logo") or _first(org, "logo", "logo_permalink"),
    }


def to_job_document(raw: dict[str, Any], *, now: datetime | None = None) -> JobDocument:
    timestamp = now or datetime.now(timezone.utc)
    org = _organization(raw)
    salary_min, salary_max, salary_raw, salary_is_estimated = _salary(raw)
    description = _string(_first(raw, "description_text", "description", "description_text_formatted"))
    max_chars = getattr(get_settings(), "job_discovery_description_max_chars", DESCRIPTION_MAX_CHARS)
    employment = _first(raw, "ai_employment_type", "employment_type")
    if isinstance(employment, list):
        employment = employment[0] if employment else None
    visa = _first(raw, "ai_visa_sponsorship", "visa_sponsorship")
    if visa is True:
        visa_value: str | None = "true"
    elif visa is False:
        visa_value = "false"
    else:
        visa_value = _string(visa) or None

    return JobDocument(
        id=_string(_first(raw, "id", "job_id", "ats_job_id")),
        title=_string(_first(raw, "title", "job_title")),
        organization_name=_string(org["name"] or "Unknown company"),
        organization_slug=_string(org["slug"]) or None,
        url=_string(_first(raw, "url", "apply_url", "ats_url")),
        date_posted=_parse_datetime(_first(raw, "date_posted", "posted_at", "created_at")),
        date_created=_parse_datetime(raw["date_created"]) if raw.get("date_created") else None,
        locations_derived=_list_of_strings(_first(raw, "locations_derived", "locations", "location")),
        ai_work_arrangement=_string(_first(raw, "ai_work_arrangement", "work_arrangement")) or None,
        ai_experience_level=_string(_first(raw, "ai_experience_level", "experience_level")) or None,
        ai_employment_type=_string(employment) or None,
        ai_salary_min=salary_min,
        ai_salary_max=salary_max,
        salary_raw=salary_raw,
        salary_is_estimated=salary_is_estimated,
        ai_key_skills=_list_of_strings(_first(raw, "ai_key_skills", "key_skills", "skills")),
        ai_core_responsibilities=_string(_first(raw, "ai_core_responsibilities", "core_responsibilities")) or None,
        ai_requirements_summary=_string(_first(raw, "ai_requirements_summary", "requirements_summary")) or None,
        ai_visa_sponsorship=visa_value,
        organization_industry=_string(org["industry"]) or None,
        organization_size=_string(org["size"]) or None,
        org_logo_permalink=_string(org["logo"]) or None,
        description_text=description[:max_chars] if description else None,
        source=_string(_first(raw, "source", "ats_platform", "platform")),
        ingested_at=timestamp,
        last_seen_at=timestamp,
    )

