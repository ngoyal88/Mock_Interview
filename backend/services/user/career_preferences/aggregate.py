"""Aggregate career preferences across users for demand-driven ingest."""
from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from firebase_config import db
from services.user.career_preferences.constants import EXPERIENCE_LEVELS
from services.user.career_preferences.normalize import normalize_doc
from utils.async_io import run_in_thread

UNMAPPED_TITLE_SAMPLE_CAP = 50
RoleFamilyMatcher = Callable[[Iterable[str]], set[str]]


class DemandSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    computed_at: datetime
    sample_size: int = 0
    experience_level_counts: dict[str, int] = Field(default_factory=dict)
    employment_type_counts: dict[str, int] = Field(default_factory=dict)
    role_family_counts: dict[str, int] = Field(default_factory=dict)
    segment_weights: dict[str, float] = Field(default_factory=dict)
    segment_supporters: dict[str, int] = Field(default_factory=dict)
    unmapped_title_samples: list[str] = Field(default_factory=list)


def segment_key(band: str, family: str) -> str:
    return f"{band}::{family}"


def _accumulate_user(
    *,
    prefs: dict[str, Any],
    matcher: Optional[RoleFamilyMatcher],
    experience_level_counts: Counter[str],
    employment_type_counts: Counter[str],
    role_family_counts: Counter[str],
    segment_weights: dict[str, float],
    segment_supporters: Counter[str],
    unmapped_samples: list[str],
    seen_unmapped: set[str],
) -> None:
    doc = normalize_doc(prefs)
    # Preserve order while deduping — duplicate multi-selects must not inflate fractional weights.
    bands = list(dict.fromkeys(b for b in doc.experience_levels if b in EXPERIENCE_LEVELS))
    for band in bands:
        experience_level_counts[band] += 1
    for emp in doc.employment_types:
        employment_type_counts[str(emp)] += 1

    titles = [t.strip() for t in doc.target_titles if isinstance(t, str) and t.strip()]
    if not bands or matcher is None:
        return

    families = sorted(matcher(titles)) if titles else []
    if not families:
        for title in titles:
            key = title.casefold()
            if key in seen_unmapped or len(unmapped_samples) >= UNMAPPED_TITLE_SAMPLE_CAP:
                continue
            seen_unmapped.add(key)
            unmapped_samples.append(title)
        return

    for family in families:
        role_family_counts[family] += 1

    weight = 1.0 / (len(bands) * len(families))
    for band in bands:
        for family in families:
            key = segment_key(band, family)
            segment_weights[key] = segment_weights.get(key, 0.0) + weight
            segment_supporters[key] += 1


def _compute_demand_snapshot_sync(
    role_family_matcher: Optional[RoleFamilyMatcher] = None,
) -> DemandSnapshot:
    experience_level_counts: Counter[str] = Counter()
    employment_type_counts: Counter[str] = Counter()
    role_family_counts: Counter[str] = Counter()
    segment_weights: dict[str, float] = {}
    segment_supporters: Counter[str] = Counter()
    unmapped_samples: list[str] = []
    seen_unmapped: set[str] = set()
    sample_size = 0

    query = db.collection("users").select(["career_preferences"])
    for snap in query.stream():
        data = snap.to_dict() or {}
        raw = data.get("career_preferences")
        if not isinstance(raw, dict):
            continue
        sample_size += 1
        _accumulate_user(
            prefs=raw,
            matcher=role_family_matcher,
            experience_level_counts=experience_level_counts,
            employment_type_counts=employment_type_counts,
            role_family_counts=role_family_counts,
            segment_weights=segment_weights,
            segment_supporters=segment_supporters,
            unmapped_samples=unmapped_samples,
            seen_unmapped=seen_unmapped,
        )

    return DemandSnapshot(
        computed_at=datetime.now(timezone.utc),
        sample_size=sample_size,
        experience_level_counts=dict(experience_level_counts),
        employment_type_counts=dict(employment_type_counts),
        role_family_counts=dict(role_family_counts),
        segment_weights=segment_weights,
        segment_supporters=dict(segment_supporters),
        unmapped_title_samples=unmapped_samples,
    )


async def compute_demand_snapshot(
    role_family_matcher: Optional[RoleFamilyMatcher] = None,
) -> DemandSnapshot:
    return await run_in_thread(_compute_demand_snapshot_sync, role_family_matcher)
