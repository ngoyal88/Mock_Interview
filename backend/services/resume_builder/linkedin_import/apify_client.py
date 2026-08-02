from __future__ import annotations

from typing import Any

import httpx

from config import get_settings
from services.resume_builder.linkedin_import.errors import LinkedInImportError
from utils.logger import get_logger

log = get_logger(__name__)

APIFY_BASE_URL = "https://api.apify.com/v2"


class ApifyLinkedInClient:
    def __init__(
        self,
        *,
        api_token: str,
        actor_id: str,
        timeout_s: float,
    ) -> None:
        self._api_token = api_token.strip()
        self._actor_id = actor_id.strip()
        self._timeout_s = timeout_s

    async def fetch_profile(self, username: str) -> dict[str, Any]:
        if not self._api_token:
            raise LinkedInImportError(
                "provider_unconfigured",
                "LinkedIn import is not configured on the server.",
                http_status=503,
            )

        url = f"{APIFY_BASE_URL}/acts/{self._actor_id}/run-sync-get-dataset-items"
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }
        payload = {"username": username, "includeEmail": False}
        timeout = httpx.Timeout(self._timeout_s)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise LinkedInImportError(
                "scrape_timeout",
                "LinkedIn import timed out. Try again in a moment.",
                http_status=504,
            ) from exc
        except httpx.HTTPError as exc:
            log.warning("Apify LinkedIn request failed", exc_info=True)
            raise LinkedInImportError(
                "scrape_failed",
                "Could not fetch the LinkedIn profile. Try again later.",
                http_status=502,
            ) from exc

        if response.status_code == 401:
            raise LinkedInImportError(
                "provider_auth_failed",
                "LinkedIn import provider authentication failed.",
                http_status=503,
            )

        if response.status_code >= 400:
            log.warning("Apify LinkedIn HTTP error status=%s body=%s", response.status_code, response.text[:500])
            raise LinkedInImportError(
                "scrape_failed",
                "Could not fetch the LinkedIn profile. Try again later.",
                http_status=502 if response.status_code >= 500 else 422,
            )

        try:
            items = response.json()
        except ValueError as exc:
            raise LinkedInImportError(
                "scrape_failed",
                "LinkedIn import returned an invalid response.",
                http_status=502,
            ) from exc

        if not isinstance(items, list) or not items:
            raise LinkedInImportError(
                "profile_not_found",
                "No public LinkedIn profile was found for that username.",
                http_status=404,
            )

        first = items[0]
        if not isinstance(first, dict):
            raise LinkedInImportError(
                "scrape_failed",
                "LinkedIn import returned an invalid profile payload.",
                http_status=502,
            )

        basic = first.get("basic_info")
        if not isinstance(basic, dict) or not str(basic.get("fullname") or basic.get("public_identifier") or "").strip():
            raise LinkedInImportError(
                "profile_not_found",
                "No public LinkedIn profile was found for that username.",
                http_status=404,
            )

        return first


def get_apify_linkedin_client() -> ApifyLinkedInClient:
    settings = get_settings()
    return ApifyLinkedInClient(
        api_token=settings.apify_api_token,
        actor_id=settings.apify_linkedin_actor_id,
        timeout_s=float(settings.apify_linkedin_timeout_s),
    )
