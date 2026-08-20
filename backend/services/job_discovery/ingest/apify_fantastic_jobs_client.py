"""Apify actor client for Fantastic.jobs career-site listings (dev / Apify-only plans)."""
from __future__ import annotations

from typing import Any, Optional

import httpx

from config import get_settings
from services.job_discovery.constants import INGEST_DEFAULTS
from services.job_discovery.models import IngestPage
from utils.domain_errors import DomainError
from utils.logger import get_logger

log = get_logger(__name__)

APIFY_BASE_URL = "https://api.apify.com/v2"


def _map_time_frame(time_frame: str) -> str:
    allowed = {"1h", "24h", "7d", "6m"}
    normalized = (time_frame or "7d").strip()
    return normalized if normalized in allowed else "7d"


def _build_actor_input(
    *,
    time_frame: str,
    limit: int,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Map direct-API ingest params to Apify actor input."""
    taxonomy_csv = str(INGEST_DEFAULTS.get("ai_taxonomies_a_primary") or "")
    taxonomy_list = [part.strip() for part in taxonomy_csv.split(",") if part.strip()]
    employment = str(INGEST_DEFAULTS.get("ai_employment_type") or "").strip()
    employment_list = [employment] if employment else []

    payload: dict[str, Any] = {
        "timeRange": _map_time_frame(time_frame),
        # Keep limit honest for credit budgets (do not inflate small remaining budgets to 10).
        "limit": max(1, min(int(limit), 5000)),
        "descriptionType": "text",
        "includeCompanyDetails": True,
        "removeAgency": True,
        "aiLanguageFilter": ["English"],
        "aiTaxonomiesPrimaryFilter": taxonomy_list,
        "aiEmploymentTypeFilter": employment_list,
    }

    # Match direct client: always apply INGEST_DEFAULTS location (India) unless params override.
    location = (
        params.get("location")
        or params.get("locationSearch")
        or params.get("geography")
        or INGEST_DEFAULTS.get("location")
    )
    if location:
        locations = location if isinstance(location, list) else [str(location)]
        payload["locationSearch"] = [str(item).strip() for item in locations if str(item).strip()]

    experience = params.get("ai_experience_level") or params.get("aiExperienceLevelFilter")
    if experience:
        if isinstance(experience, list):
            payload["aiExperienceLevelFilter"] = [str(item).strip() for item in experience if str(item).strip()]
        else:
            payload["aiExperienceLevelFilter"] = [
                part.strip() for part in str(experience).split(",") if part.strip()
            ]

    include_terms = params.get("title_include_terms") or params.get("titleSearch")
    if include_terms:
        if isinstance(include_terms, list):
            payload["titleSearch"] = [str(item).strip() for item in include_terms if str(item).strip()]
        else:
            payload["titleSearch"] = [str(include_terms).strip()]

    exclude_terms = params.get("title_exclude_terms") or params.get("titleExclusionSearch")
    if exclude_terms:
        if isinstance(exclude_terms, list):
            payload["titleExclusionSearch"] = [str(item).strip() for item in exclude_terms if str(item).strip()]
        else:
            payload["titleExclusionSearch"] = [str(exclude_terms).strip()]

    # Direct-API boolean title_advanced is not supported on Apify — term lists above approximate it.
    skip_keys = {
        "location",
        "locationSearch",
        "geography",
        "ai_experience_level",
        "aiExperienceLevelFilter",
        "title_advanced",
        "title_include_terms",
        "title_exclude_terms",
        "titleSearch",
        "titleExclusionSearch",
    }
    for key, value in params.items():
        if key in skip_keys:
            continue
        if value not in (None, ""):
            payload[key] = value

    if INGEST_DEFAULTS.get("organization_agency") == "exclude":
        payload.setdefault("removeAgency", True)
    return payload


class ApifyFantasticJobsClient:
    """Runs `fantastic-jobs/career-site-job-listing-api` via Apify sync dataset API."""

    def __init__(
        self,
        *,
        api_token: str | None = None,
        actor_id: str | None = None,
        timeout_s: float | None = None,
    ) -> None:
        settings = get_settings()
        self.api_token = (api_token if api_token is not None else settings.apify_api_token).strip()
        self.actor_id = (actor_id or settings.apify_fantastic_jobs_actor_id).strip()
        self.timeout_s = float(timeout_s if timeout_s is not None else settings.apify_fantastic_jobs_timeout_s)

    async def _run_actor(self, actor_input: dict[str, Any]) -> list[dict[str, Any]]:
        if not self.api_token:
            raise DomainError("provider_unconfigured", "Apify API token is not configured")
        url = f"{APIFY_BASE_URL}/acts/{self.actor_id}/run-sync-get-dataset-items"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        timeout = httpx.Timeout(self.timeout_s)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=actor_input)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, list):
            raise DomainError("provider_invalid_response", "Apify actor returned a non-list payload")
        return [item for item in payload if isinstance(item, dict)]

    async def fetch_active_ats(
        self,
        *,
        time_frame: str = "1h",
        limit: int = 1000,
        cursor: Optional[str] = None,
        offset: Optional[int] = None,
        **params: Any,
    ) -> IngestPage:
        if cursor or offset:
            log.info("Apify ingest ignores cursor/offset; single sync run per page request")
        actor_input = _build_actor_input(time_frame=time_frame, limit=limit, params=params)
        jobs = await self._run_actor(actor_input)
        return IngestPage(jobs=jobs, next_cursor=None, credits_consumed=len(jobs))

    async def fetch_expired_ats(
        self,
        *,
        time_frame: str = "1h",
        limit: int = 1000,
        cursor: Optional[str] = None,
    ) -> IngestPage:
        # ponytail: Apify expiry uses a separate paid companion actor; staleness sweep covers P1 locally.
        log.info("Apify ingest expiry sweep skipped; rely on staleness sweep or direct Fantastic.jobs API")
        return IngestPage(jobs=[])

    async def active_ats_count(self, **params: Any) -> int:
        page = await self.fetch_active_ats(time_frame="1h", limit=10, **params)
        return len(page.jobs)
