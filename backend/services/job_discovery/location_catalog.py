"""Canonical Job Discovery location catalog (GeoNames-backed India dump).

Hot path (`resolve_from_text` / ingest) uses a precomputed index — O(tokens)
dict lookups plus a small multi-word phrase scan, not a full catalog × regex sweep.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

from services.job_discovery.constants import SUPPORTED_COUNTRY_CODES, SUPPORTED_COUNTRY_NAMES
from services.job_discovery.models import LocationEntry

_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "job_discovery" / "location_catalog.json"
_TOKEN_SPLIT = re.compile(r"[\s,;/|]+")
_PHRASE_BOUNDARY = re.compile(r"[\s,;/|]")


def _norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _is_city_entry(entry: LocationEntry) -> bool:
    return bool(entry.city) and _norm(entry.city) != "remote" and not entry.catch_all


@dataclass(frozen=True)
class _CatalogIndex:
    entries: tuple[LocationEntry, ...]
    by_id: dict[str, LocationEntry]
    known_ids: frozenset[str]
    # normalized city / alias → location_ids (higher-pop first from generator order)
    city_alias_to_ids: dict[str, tuple[str, ...]]
    # normalized state/UT name → state row id
    region_to_state_id: dict[str, str]
    # multi-word needles only, longest first; (needle, location_id, is_city)
    multi_phrases: tuple[tuple[str, str, bool], ...] = field(default_factory=tuple)


def _build_index(entries: list[LocationEntry]) -> _CatalogIndex:
    by_id = {entry.location_id: entry for entry in entries}
    city_alias: dict[str, list[str]] = {}
    region_to_state: dict[str, str] = {}
    multi: list[tuple[str, str, bool, int]] = []  # needle, id, is_city, needle_len

    def add_city_key(key: str, location_id: str) -> None:
        if not key:
            return
        bucket = city_alias.setdefault(key, [])
        if location_id not in bucket:
            bucket.append(location_id)
        if " " in key:
            multi.append((key, location_id, True, len(key)))

    for entry in entries:
        if entry.catch_all:
            continue
        if _is_city_entry(entry):
            add_city_key(_norm(entry.city), entry.location_id)
            for alias in entry.aliases:
                add_city_key(_norm(alias), entry.location_id)
            continue

        region = _norm(entry.region)
        if region and region != "remote":
            region_to_state.setdefault(region, entry.location_id)
            if " " in region:
                multi.append((region, entry.location_id, False, len(region)))

    # Longest first; cities before states when lengths tie.
    multi.sort(key=lambda row: (row[3], 1 if row[2] else 0), reverse=True)
    return _CatalogIndex(
        entries=tuple(entries),
        by_id=by_id,
        known_ids=frozenset(by_id),
        city_alias_to_ids={key: tuple(ids) for key, ids in city_alias.items()},
        region_to_state_id=region_to_state,
        multi_phrases=tuple((needle, loc_id, is_city) for needle, loc_id, is_city, _ in multi),
    )


@lru_cache(maxsize=1)
def load_catalog() -> list[LocationEntry]:
    raw = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    return [LocationEntry(**item) for item in raw]


@lru_cache(maxsize=1)
def _index() -> _CatalogIndex:
    return _build_index(load_catalog())


def supported_country_code(value: str | None) -> Optional[str]:
    normalized = _norm(value)
    if not normalized:
        return None
    if normalized in SUPPORTED_COUNTRY_NAMES:
        return SUPPORTED_COUNTRY_NAMES[normalized]
    for country_name, code in SUPPORTED_COUNTRY_NAMES.items():
        # Exact-token / contained name only for real names (never 2-letter codes as substrings).
        if len(country_name) > 2 and country_name in normalized:
            return code
    return None


def get_location(location_id: str) -> Optional[LocationEntry]:
    return _index().by_id.get(location_id)


def _pick_city_id(candidates: tuple[str, ...], region: str) -> str:
    if not region:
        return candidates[0]
    idx = _index()
    for location_id in candidates:
        entry = idx.by_id.get(location_id)
        if entry and _norm(entry.region) == region:
            return location_id
    return candidates[0]


def resolve_location_id(country: str, region: str | None = None, city: str | None = None) -> Optional[str]:
    country_code = supported_country_code(country)
    if not country_code:
        return None

    idx = _index()
    city_key = _norm(city)
    region_key = _norm(region)

    if city_key:
        candidates = idx.city_alias_to_ids.get(city_key)
        if candidates:
            return _pick_city_id(candidates, region_key)
        return f"{country_code}_other"

    if region_key:
        return idx.region_to_state_id.get(region_key) or f"{country_code}_other"

    # Country-only preference → no city/state constraint (caller omits location filter).
    return None


def _phrase_in_text(haystack: str, needle: str) -> bool:
    """Whole-phrase match on comma/space boundaries (avoids 'Ranci' inside 'Francisco')."""
    start = 0
    while True:
        pos = haystack.find(needle, start)
        if pos < 0:
            return False
        end = pos + len(needle)
        left_ok = pos == 0 or _PHRASE_BOUNDARY.match(haystack[pos - 1]) is not None
        right_ok = end == len(haystack) or _PHRASE_BOUNDARY.match(haystack[end]) is not None
        if left_ok and right_ok:
            return True
        start = pos + 1


def resolve_from_text(value: str) -> Optional[str]:
    text = _norm(value)
    if not text:
        return None

    idx = _index()

    # Multi-word cities/states first (longest needle wins via sort order).
    for needle, location_id, _is_city in idx.multi_phrases:
        if needle in text and _phrase_in_text(text, needle):
            return location_id

    tokens = [token for token in _TOKEN_SPLIT.split(text) if token]
    if not tokens:
        country_code = supported_country_code(text)
        return f"{country_code}_other" if country_code else None

    token_set = set(tokens)
    city_hits: list[str] = []
    for token in tokens:
        candidates = idx.city_alias_to_ids.get(token)
        if not candidates:
            continue
        for location_id in candidates:
            if location_id not in city_hits:
                city_hits.append(location_id)

    if city_hits:
        # Prefer a city whose state also appears in the job location string.
        for location_id in city_hits:
            entry = idx.by_id.get(location_id)
            region = _norm(entry.region) if entry else ""
            if region and region in token_set:
                return location_id
        return city_hits[0]

    for token in tokens:
        state_id = idx.region_to_state_id.get(token)
        if state_id:
            return state_id

    country_code = supported_country_code(text)
    return f"{country_code}_other" if country_code else None


def catalog_location_ids(values: Iterable[str]) -> list[str]:
    known = _index().known_ids
    return [value for value in values if value in known]


def country_codes_from_location_ids(location_ids: Iterable[str]) -> list[str]:
    """Derive ISO-ish country codes from catalog ids (`in_bengaluru` → `in`)."""
    codes: list[str] = []
    for location_id in location_ids:
        code = str(location_id).split("_", 1)[0].lower()
        if code in SUPPORTED_COUNTRY_CODES and code not in codes:
            codes.append(code)
    # India-only inventory: unresolved jobs still belong to the ingest geography.
    return codes or ["in"]
