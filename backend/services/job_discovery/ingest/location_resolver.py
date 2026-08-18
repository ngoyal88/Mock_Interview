"""Resolve Fantastic.jobs location strings to catalog IDs."""
from __future__ import annotations

from dataclasses import dataclass

from services.job_discovery.location_catalog import resolve_from_text
from services.job_discovery.models import JobDocument


@dataclass(frozen=True)
class LocationResolution:
    location_ids: list[str]
    unresolved_count: int = 0


def resolve_job_locations(job: JobDocument) -> LocationResolution:
    seen: set[str] = set()
    ids: list[str] = []
    unresolved = 0
    for raw in job.locations_derived:
        if not isinstance(raw, str) or not raw.strip():
            unresolved += 1
            continue
        location_id = resolve_from_text(raw)
        if not location_id:
            unresolved += 1
            continue
        if location_id in seen:
            continue
        seen.add(location_id)
        ids.append(location_id)
    return LocationResolution(location_ids=ids, unresolved_count=unresolved)
