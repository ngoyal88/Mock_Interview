"""Job Discovery API routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from services.job_discovery import detail_service, discovery_settings_service, fit_bridge_service, saved_jobs_service
from services.job_discovery.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from services.job_discovery.models import (
    DiscoverySettings,
    DiscoverySettingsPatch,
    JobDetail,
    SaveJobRequest,
    SaveJobResponse,
    SavedJobsResponse,
    SearchFilters,
    SearchResult,
)
from services.job_discovery.search.search_service import search_jobs
from utils.auth import verify_firebase_token
from utils.rate_limit import check_rate_limit

router = APIRouter(prefix="/jobs", tags=["JobDiscovery"])


@router.get("/search", response_model=SearchResult)
async def search(
    q: str = "",
    location_ids: list[str] = Query(default_factory=list),
    country_codes: list[str] = Query(default_factory=list),
    work_arrangements: list[str] = Query(default_factory=list),
    experience_levels: list[str] = Query(default_factory=list),
    employment_types: list[str] = Query(default_factory=list),
    industries: list[str] = Query(default_factory=list),
    organization_sizes: list[str] = Query(default_factory=list),
    organization_slugs: list[str] = Query(default_factory=list),
    visa_sponsorship: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    has_salary_only: bool = False,
    posted_within_days: Optional[int] = None,
    sort: str = "fresh",
    page: int = 0,
    page_size: int = DEFAULT_PAGE_SIZE,
    uid: str = Depends(verify_firebase_token),
) -> SearchResult:
    await check_rate_limit(uid, "job_discovery_search", limit=120, window_seconds=3600)
    filters = SearchFilters(
        q=q,
        location_ids=location_ids,
        country_codes=country_codes,
        work_arrangements=work_arrangements,
        experience_levels=experience_levels,
        employment_types=employment_types,
        industries=industries,
        organization_sizes=organization_sizes,
        organization_slugs=organization_slugs,
        visa_sponsorship=visa_sponsorship,
        salary_min=salary_min,
        salary_max=salary_max,
        has_salary_only=has_salary_only,
        posted_within_days=posted_within_days,
        sort="salary" if sort == "salary" else "fresh",
    )
    return await search_jobs(uid, filters, page=max(0, page), page_size=max(1, min(page_size, MAX_PAGE_SIZE)))


@router.get("/saved", response_model=SavedJobsResponse)
async def saved(uid: str = Depends(verify_firebase_token)) -> SavedJobsResponse:
    await check_rate_limit(uid, "job_discovery_saved_read", limit=120, window_seconds=3600)
    return await saved_jobs_service.list_saved(uid)


@router.get("/discovery-settings", response_model=DiscoverySettings)
async def get_discovery_settings(uid: str = Depends(verify_firebase_token)) -> DiscoverySettings:
    await check_rate_limit(uid, "job_discovery_settings_read", limit=120, window_seconds=3600)
    return await discovery_settings_service.get(uid)


@router.patch("/discovery-settings", response_model=DiscoverySettings)
async def patch_discovery_settings(
    body: DiscoverySettingsPatch,
    uid: str = Depends(verify_firebase_token),
) -> DiscoverySettings:
    await check_rate_limit(uid, "job_discovery_settings_write", limit=30, window_seconds=3600)
    return await discovery_settings_service.patch(uid, body)


@router.get("/{job_id}", response_model=JobDetail)
async def detail(job_id: str, uid: str = Depends(verify_firebase_token)) -> JobDetail:
    await check_rate_limit(uid, "job_discovery_detail", limit=240, window_seconds=3600)
    return await detail_service.get_job_detail(job_id, uid=uid)


@router.post("/{job_id}/fit")
async def fit(job_id: str, uid: str = Depends(verify_firebase_token)):
    await check_rate_limit(uid, "job_discovery_fit", limit=30, window_seconds=3600)
    return await fit_bridge_service.compute_fit_for_job(uid, job_id)


@router.post("/{job_id}/save", response_model=SaveJobResponse)
async def save(
    job_id: str,
    body: SaveJobRequest | None = None,
    uid: str = Depends(verify_firebase_token),
) -> SaveJobResponse:
    await check_rate_limit(uid, "job_discovery_save", limit=120, window_seconds=3600)
    return await saved_jobs_service.save(uid, job_id, body)


@router.delete("/{job_id}/save", response_model=SaveJobResponse)
async def unsave(job_id: str, uid: str = Depends(verify_firebase_token)) -> SaveJobResponse:
    await check_rate_limit(uid, "job_discovery_save", limit=120, window_seconds=3600)
    return await saved_jobs_service.unsave(uid, job_id)

