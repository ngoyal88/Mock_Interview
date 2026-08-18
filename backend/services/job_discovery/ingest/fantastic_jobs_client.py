"""Fantastic.jobs ingest clients — direct API or Apify actor."""
from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable

import httpx

from config import get_settings
from services.job_discovery.constants import INGEST_DEFAULTS
from services.job_discovery.models import IngestPage
from utils.domain_errors import DomainError


@runtime_checkable
class JobIngestClient(Protocol):
    async def fetch_active_ats(
        self,
        *,
        time_frame: str = "1h",
        limit: int = 1000,
        cursor: Optional[str] = None,
        offset: Optional[int] = None,
        **params: Any,
    ) -> IngestPage: ...

    async def fetch_expired_ats(
        self,
        *,
        time_frame: str = "1h",
        limit: int = 1000,
        cursor: Optional[str] = None,
    ) -> IngestPage: ...

    async def active_ats_count(self, **params: Any) -> int: ...


def get_fantastic_jobs_client() -> JobIngestClient:
    settings = get_settings()
    provider = (settings.job_discovery_ingest_provider or "auto").strip().lower()
    fj_key = settings.fantastic_jobs_api_key.strip()
    apify_token = settings.apify_api_token.strip()

    use_apify = provider == "apify" or (
        provider == "auto"
        and (not fj_key or fj_key.startswith("apify_api_"))
        and bool(apify_token or fj_key.startswith("apify_api_"))
    )
    if use_apify:
        from services.job_discovery.ingest.apify_fantastic_jobs_client import ApifyFantasticJobsClient

        token = fj_key if fj_key.startswith("apify_api_") else None
        return ApifyFantasticJobsClient(api_token=token)
    return FantasticJobsClient()


class FantasticJobsClient:
    def __init__(self, *, api_key: str | None = None, base_url: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.fantastic_jobs_api_key
        self.base_url = (base_url or settings.fantastic_jobs_base_url).rstrip("/")

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise DomainError("provider_unconfigured", "Fantastic.jobs API key is not configured")
        return {"Authorization": f"Bearer {self.api_key}"}

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any] | list[Any]:
        url = f"{self.base_url}/v1/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _page_from_payload(payload: dict[str, Any] | list[Any]) -> IngestPage:
        if isinstance(payload, list):
            return IngestPage(jobs=[item for item in payload if isinstance(item, dict)])
        jobs = payload.get("jobs") or payload.get("data") or payload.get("results") or []
        cursor = payload.get("next_cursor") or payload.get("cursor") or payload.get("next")
        credits = int(payload.get("credits_consumed") or payload.get("credits") or len(jobs))
        return IngestPage(jobs=[item for item in jobs if isinstance(item, dict)], next_cursor=cursor, credits_consumed=credits)

    async def fetch_active_ats(
        self,
        *,
        time_frame: str = "1h",
        limit: int = 1000,
        cursor: Optional[str] = None,
        offset: Optional[int] = None,
        **params: Any,
    ) -> IngestPage:
        query = {**INGEST_DEFAULTS, **params, "time_frame": time_frame, "limit": limit}
        if cursor:
            query["cursor"] = cursor
        elif offset is not None:
            query["offset"] = offset
        return self._page_from_payload(await self._get("active-ats", query))

    async def fetch_expired_ats(
        self,
        *,
        time_frame: str = "1h",
        limit: int = 1000,
        cursor: Optional[str] = None,
    ) -> IngestPage:
        query: dict[str, Any] = {"time_frame": time_frame, "limit": limit}
        if cursor:
            query["cursor"] = cursor
        payload = await self._get("expired-ats", query)
        if isinstance(payload, list):
            return IngestPage(jobs=[{"id": str(item)} for item in payload if item])
        ids = payload.get("ids") or payload.get("jobs") or payload.get("data") or []
        jobs = [{"id": str(item.get("id") if isinstance(item, dict) else item)} for item in ids if item]
        return IngestPage(jobs=jobs, next_cursor=payload.get("next_cursor") or payload.get("cursor"))

    async def active_ats_count(self, **params: Any) -> int:
        payload = await self._get("active-ats-count", {**INGEST_DEFAULTS, **params})
        if isinstance(payload, list):
            return len(payload)
        return int(payload.get("count") or payload.get("total") or 0)

