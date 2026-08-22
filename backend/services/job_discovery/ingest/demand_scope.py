"""Build Fantastic.jobs ingest plans from demand snapshots (money + customer floor)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone
from typing import Literal

from firebase_admin import firestore

from firebase_config import db
from services.job_discovery.constants import DEMAND_SNAPSHOTS_COLLECTION
from services.job_discovery.ingest.role_family_taxonomy import (
    ROLE_FAMILIES,
    family_title_expression,
    family_title_terms,
)
from services.platform.reference.enums import EXPERIENCE_LEVELS
from services.user.career_preferences.aggregate import DemandSnapshot
from utils.async_io import run_in_thread
from utils.logger import get_logger

logger = get_logger(__name__)

MIN_SAMPLE_FOR_SEGMENTS = 50
MIN_SEGMENT_SUPPORTERS = 1
MAX_ACTIVE_SEGMENTS = 8

# Launch seed — common India personas; not a full-corpus fallback.
SEED_SEGMENTS: tuple[tuple[str, str], ...] = (
    ("0-2", "sde"),
    ("0-2", "data_ml"),
    ("0-2", "product"),
    ("2-5", "sde"),
    ("2-5", "data_ml"),
    ("2-5", "product"),
    ("5-10", "sde"),
)

_unknown_seed_bands = {band for band, _ in SEED_SEGMENTS if band not in EXPERIENCE_LEVELS}
if _unknown_seed_bands:
    raise AssertionError(f"SEED_SEGMENTS bands not in EXPERIENCE_LEVELS: {_unknown_seed_bands}")

LATEST_DOC_ID = "latest"


@dataclass(frozen=True)
class IngestSegment:
    band: str
    family_key: str
    title_advanced: str
    title_include_terms: tuple[str, ...]
    title_exclude_terms: tuple[str, ...]
    weight: float = 0.0


@dataclass(frozen=True)
class IngestPlan:
    source: Literal["seed", "demand_snapshot"]
    segments: list[IngestSegment]


def _title_with_exclusions(family_key: str, prior_families: list[str]) -> str:
    expr = family_title_expression(family_key)
    if not prior_families:
        return expr
    excluded = " | ".join(family_title_expression(key) for key in prior_families)
    return f"({expr}) & !({excluded})"


def _exclude_terms(prior_families: list[str]) -> tuple[str, ...]:
    terms: list[str] = []
    seen: set[str] = set()
    for key in prior_families:
        try:
            family_terms = family_title_terms(key)
        except KeyError:
            continue
        for term in family_terms:
            folded = term.casefold()
            if folded in seen:
                continue
            seen.add(folded)
            terms.append(term)
    return tuple(terms)


def _segments_from_pairs(
    pairs: list[tuple[str, str, float]],
    *,
    source: Literal["seed", "demand_snapshot"],
) -> IngestPlan:
    # pairs already sorted by weight desc (seed uses equal weights in listed order)
    prior_by_band: dict[str, list[str]] = {}
    segments: list[IngestSegment] = []
    for band, family_key, weight in pairs:
        if family_key not in ROLE_FAMILIES:
            logger.warning("Skipping unknown role family in ingest plan: %s", family_key)
            continue
        try:
            include_terms = family_title_terms(family_key)
        except KeyError:
            logger.warning("Skipping role family without ingest terms: %s", family_key)
            continue
        prior = prior_by_band.setdefault(band, [])
        segments.append(
            IngestSegment(
                band=band,
                family_key=family_key,
                title_advanced=_title_with_exclusions(family_key, prior),
                title_include_terms=include_terms,
                title_exclude_terms=_exclude_terms(prior),
                weight=weight,
            )
        )
        prior.append(family_key)
    return IngestPlan(source=source, segments=segments)


def build_plan(snapshot: DemandSnapshot | None) -> IngestPlan:
    if snapshot is None or snapshot.sample_size < MIN_SAMPLE_FOR_SEGMENTS:
        pairs = [(band, family, 0.0) for band, family in SEED_SEGMENTS]
        return _segments_from_pairs(pairs, source="seed")

    eligible: list[tuple[str, str, float]] = []
    for key, supporters in snapshot.segment_supporters.items():
        if supporters < MIN_SEGMENT_SUPPORTERS:
            continue
        if "::" not in key:
            continue
        band, family = key.split("::", 1)
        if family not in ROLE_FAMILIES:
            continue
        weight = float(snapshot.segment_weights.get(key, 0.0))
        eligible.append((band, family, weight))

    eligible.sort(key=lambda row: (-row[2], row[0], row[1]))
    selected = eligible[:MAX_ACTIVE_SEGMENTS]
    if not selected:
        pairs = [(band, family, 0.0) for band, family in SEED_SEGMENTS]
        return _segments_from_pairs(pairs, source="seed")
    return _segments_from_pairs(selected, source="demand_snapshot")


def _store_demand_snapshot_sync(snapshot: DemandSnapshot) -> None:
    payload = snapshot.model_dump(mode="python")
    date_id = snapshot.computed_at.astimezone(timezone.utc).strftime("%Y-%m-%d")
    col = db.collection(DEMAND_SNAPSHOTS_COLLECTION)
    col.document(date_id).set(payload, merge=True)
    col.document(LATEST_DOC_ID).set(
        {
            **payload,
            "snapshot_date": date_id,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


def _load_latest_snapshot_sync() -> DemandSnapshot | None:
    snap = db.collection(DEMAND_SNAPSHOTS_COLLECTION).document(LATEST_DOC_ID).get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    data.pop("snapshot_date", None)
    data.pop("updated_at", None)
    try:
        return DemandSnapshot.model_validate(data)
    except Exception:
        logger.warning("Invalid job_discovery demand snapshot at latest; using seed plan", exc_info=True)
        return None


async def store_demand_snapshot(snapshot: DemandSnapshot) -> None:
    await run_in_thread(_store_demand_snapshot_sync, snapshot)


async def load_latest_snapshot() -> DemandSnapshot | None:
    return await run_in_thread(_load_latest_snapshot_sync)
