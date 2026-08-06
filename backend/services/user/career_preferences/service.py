"""Orchestration: merge patches, validate, persist, completeness."""
from __future__ import annotations

import re
from typing import Any

from services.user.career_preferences.completeness import evaluate_completeness
from services.user.career_preferences.constants import (
    COMPANY_SIZE_BUCKETS,
    EMPLOYMENT_TYPES,
    EXPERIENCE_LEVELS,
    MAX_COMPANY_SLUGS,
    MAX_EXCLUDE_LOCATIONS,
    MAX_EXCLUDE_TITLES,
    MAX_INDUSTRIES,
    MAX_LOCATIONS,
    MAX_TARGET_TITLES,
    MAX_YEARS_EXPERIENCE,
    SUPPORTED_COUNTRIES,
    WORK_ARRANGEMENTS,
)
from services.user.career_preferences.models import (
    CareerPreferencesDoc,
    CareerPreferencesPatch,
    CareerPreferencesResponse,
    LocationRecord,
)
from services.user.career_preferences.normalize import normalize_doc
from services.user.career_preferences.repository import read_preferences_raw, write_preferences
from utils.domain_errors import DomainError

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _dedupe_ci(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        trimmed = value.strip()
        if not trimmed:
            continue
        key = trimmed.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(trimmed)
    return out


def _sanitize_strings(values: list[str], *, field: str, max_len: int) -> list[str]:
    deduped = _dedupe_ci(values)
    if len(deduped) > max_len:
        raise DomainError(
            "career_preferences_invalid_value",
            f"{field} exceeds maximum of {max_len} items",
        )
    return deduped


def _sanitize_slugs(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        slug = value.strip().lower()
        if not slug:
            continue
        if not _SLUG_RE.match(slug):
            raise DomainError(
                "career_preferences_invalid_value",
                f"Invalid company slug: {value!r}",
            )
        if slug in seen:
            continue
        seen.add(slug)
        deduped.append(slug)
    if len(deduped) > MAX_COMPANY_SLUGS:
        raise DomainError(
            "career_preferences_invalid_value",
            f"target_company_slugs exceeds maximum of {MAX_COMPANY_SLUGS} items",
        )
    return deduped


def _check_enum_values(values: list[str], allowed: frozenset[str], field: str) -> list[str]:
    invalid = [v for v in values if v not in allowed]
    if invalid:
        raise DomainError(
            "career_preferences_invalid_value",
            f"Invalid {field}: {invalid[0]!r}",
        )
    return values


def _sanitize_locations(values: list[LocationRecord], *, field: str, max_len: int) -> list[LocationRecord]:
    if len(values) > max_len:
        raise DomainError(
            "career_preferences_invalid_value",
            f"{field} exceeds maximum of {max_len} items",
        )
    out: list[LocationRecord] = []
    for loc in values:
        country = loc.country.strip()
        if country not in SUPPORTED_COUNTRIES:
            raise DomainError(
                "career_preferences_invalid_value",
                f"Unsupported country: {country!r}",
            )
        city = loc.city.strip() if loc.city else None
        region = loc.region.strip() if loc.region else None
        out.append(
            LocationRecord(
                country=country,
                city=city or None,
                region=region or None,
            )
        )
    return out


def _validate_and_build(raw: dict[str, Any]) -> CareerPreferencesDoc:
    payload = dict(raw)

    if "target_titles" in payload:
        payload["target_titles"] = _sanitize_strings(
            payload["target_titles"], field="target_titles", max_len=MAX_TARGET_TITLES
        )
    if "exclude_titles" in payload:
        payload["exclude_titles"] = _sanitize_strings(
            payload["exclude_titles"], field="exclude_titles", max_len=MAX_EXCLUDE_TITLES
        )
    if "experience_levels" in payload:
        payload["experience_levels"] = _check_enum_values(
            payload["experience_levels"], EXPERIENCE_LEVELS, "experience_levels"
        )
    if "work_arrangements" in payload:
        payload["work_arrangements"] = _check_enum_values(
            payload["work_arrangements"], WORK_ARRANGEMENTS, "work_arrangements"
        )
    if "employment_types" in payload:
        payload["employment_types"] = _check_enum_values(
            payload["employment_types"], EMPLOYMENT_TYPES, "employment_types"
        )
    if "company_size_buckets" in payload:
        payload["company_size_buckets"] = _check_enum_values(
            payload["company_size_buckets"], COMPANY_SIZE_BUCKETS, "company_size_buckets"
        )
    if "locations" in payload:
        locs = [LocationRecord.model_validate(x) for x in payload["locations"]]
        payload["locations"] = _sanitize_locations(locs, field="locations", max_len=MAX_LOCATIONS)
    if "exclude_locations" in payload:
        locs = [LocationRecord.model_validate(x) for x in payload["exclude_locations"]]
        payload["exclude_locations"] = _sanitize_locations(
            locs, field="exclude_locations", max_len=MAX_EXCLUDE_LOCATIONS
        )
    if "target_company_slugs" in payload:
        payload["target_company_slugs"] = _sanitize_slugs(payload["target_company_slugs"])
    if "target_industries" in payload:
        payload["target_industries"] = _sanitize_strings(
            payload["target_industries"], field="target_industries", max_len=MAX_INDUSTRIES
        )
    if payload.get("years_experience") is not None:
        yoe = int(payload["years_experience"])
        if yoe < 0 or yoe > MAX_YEARS_EXPERIENCE:
            raise DomainError(
                "career_preferences_invalid_value",
                f"years_experience must be between 0 and {MAX_YEARS_EXPERIENCE}",
            )
        payload["years_experience"] = yoe

    salary_min = payload.get("salary_min")
    salary_max = payload.get("salary_max")
    if salary_min is not None and salary_min < 0:
        raise DomainError("career_preferences_invalid_value", "salary_min must be non-negative")
    if salary_max is not None and salary_max < 0:
        raise DomainError("career_preferences_invalid_value", "salary_max must be non-negative")
    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        raise DomainError(
            "career_preferences_invalid_value",
            "salary_min cannot exceed salary_max",
        )

    if payload.get("language") is not None:
        lang = str(payload["language"]).strip()
        if not lang:
            raise DomainError("career_preferences_invalid_value", "language cannot be empty")
        payload["language"] = lang

    if payload.get("salary_currency") is not None:
        currency = str(payload["salary_currency"]).strip().upper()
        if len(currency) != 3:
            raise DomainError("career_preferences_invalid_value", "salary_currency must be a 3-letter code")
        payload["salary_currency"] = currency

    return normalize_doc(payload)


def _to_response(doc: CareerPreferencesDoc) -> CareerPreferencesResponse:
    return CareerPreferencesResponse(preferences=doc, completeness=evaluate_completeness(doc))


async def get_preferences(uid: str) -> CareerPreferencesResponse:
    raw = await read_preferences_raw(uid)
    doc = normalize_doc(raw)
    return _to_response(doc)


async def patch_preferences(uid: str, patch: CareerPreferencesPatch) -> CareerPreferencesResponse:
    raw = await read_preferences_raw(uid)
    current = normalize_doc(raw)
    merged = current.model_dump()
    patch_data = patch.model_dump(exclude_unset=True)
    for key, value in patch_data.items():
        merged[key] = value
    doc = _validate_and_build(merged)
    await write_preferences(uid, doc.model_dump())
    return _to_response(doc)
