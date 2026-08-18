"""Search-index projection writes."""
from __future__ import annotations

from services.job_discovery.models import JobDocument
from services.job_discovery.search import meilisearch_client


async def upsert_batch(jobs: list[JobDocument]) -> None:
    await meilisearch_client.add_documents([job.to_search_document() for job in jobs if job.status == "active"])


async def delete_batch(job_ids: list[str] | set[str]) -> None:
    await meilisearch_client.delete_documents([str(job_id) for job_id in job_ids if job_id])

