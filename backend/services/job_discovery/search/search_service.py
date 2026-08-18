"""Job Discovery search orchestration."""
from __future__ import annotations

from config import get_settings
from services.job_discovery.models import (
    JobCard,
    JobDiscoveryDisabledError,
    SearchBackendUnavailableError,
    SearchFilters,
    SearchResult,
)
from services.job_discovery.search import meilisearch_client
from services.job_discovery.search.search_query_builder import build_filter, build_sort, merge_with_preferences
from services.user.career_preferences.loader import get_career_preferences


def _card_from_hit(hit: dict) -> JobCard:
    return JobCard(
        id=str(hit.get("id") or ""),
        title=str(hit.get("title") or ""),
        organization_name=str(hit.get("organization_name") or ""),
        organization_slug=hit.get("organization_slug"),
        org_logo_permalink=hit.get("org_logo_permalink"),
        location_ids=list(hit.get("location_ids") or []),
        ai_work_arrangement=hit.get("ai_work_arrangement"),
        ai_experience_level=hit.get("ai_experience_level"),
        ai_employment_type=hit.get("ai_employment_type"),
        salary_min=hit.get("salary_min"),
        salary_max=hit.get("salary_max"),
        salary_is_estimated=bool(hit.get("salary_is_estimated", True)),
        date_posted_ts=hit.get("date_posted_ts"),
        status=hit.get("status") or "active",
    )


async def search_jobs(uid: str, filters: SearchFilters, *, page: int, page_size: int) -> SearchResult:
    if not get_settings().job_discovery_enabled:
        raise JobDiscoveryDisabledError()

    prefs = await get_career_preferences(uid)
    merged = merge_with_preferences(filters, prefs)
    offset = max(0, page) * page_size
    try:
        raw = await meilisearch_client.search(
            query=merged.q,
            filter=build_filter(merged),
            sort=build_sort(merged),
            offset=offset,
            limit=page_size,
        )
    except meilisearch_client.meili_unavailable_errors() as exc:
        raise SearchBackendUnavailableError() from exc

    hits = raw.get("hits") or []
    total = int(raw.get("estimatedTotalHits") or raw.get("totalHits") or len(hits))
    return SearchResult(cards=[_card_from_hit(hit) for hit in hits], total=total, page=page, page_size=page_size)

