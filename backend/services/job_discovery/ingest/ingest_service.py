"""Job Discovery ingest orchestration."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from firebase_admin import firestore

from config import get_settings
from firebase_config import db
from services.job_discovery.constants import INGEST_RUNS_COLLECTION, JOBS_COLLECTION, STALE_UNSEEN_DAYS
from services.job_discovery.ingest.credit_budget import CreditBudgetExceeded
from services.job_discovery.ingest.fantastic_jobs_client import JobIngestClient, get_fantastic_jobs_client
from services.job_discovery.ingest.job_mapper import to_job_document
from services.job_discovery.ingest.location_resolver import resolve_job_locations
from services.job_discovery.models import IngestRunResult, JobDocument
from services.job_discovery.search import search_index_sync
from services.job_discovery.search.meilisearch_client import meili_unavailable_errors
from utils.async_io import run_in_thread
from utils.logger import get_logger

logger = get_logger(__name__)


def _start_run_sync(kind: str, time_frame: str) -> str:
    run_id = f"{kind}_{uuid.uuid4().hex[:12]}"
    db.collection(INGEST_RUNS_COLLECTION).document(run_id).set(
        {
            "kind": kind,
            "time_frame": time_frame,
            "started_at": firestore.SERVER_TIMESTAMP,
            "status": "running",
            "pages_completed": 0,
            "jobs_upserted": 0,
            "jobs_expired": 0,
            "credits_consumed": 0,
        }
    )
    return run_id


def _finish_run_sync(result: IngestRunResult, *, time_frame: str, kind: str) -> None:
    db.collection(INGEST_RUNS_COLLECTION).document(result.run_id).set(
        {
            **result.model_dump(mode="python"),
            "kind": kind,
            "time_frame": time_frame,
            "finished_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


def _upsert_jobs_sync(jobs: list[JobDocument]) -> None:
    if not jobs:
        return
    for offset in range(0, len(jobs), 400):
        batch = db.batch()
        for job in jobs[offset : offset + 400]:
            batch.set(db.collection(JOBS_COLLECTION).document(job.id), job.to_firestore(), merge=True)
        batch.commit()


def _mark_expired_sync(job_ids: Iterable[str]) -> int:
    ids = [str(job_id) for job_id in job_ids if job_id]
    if not ids:
        return 0
    now = datetime.now(timezone.utc)
    for offset in range(0, len(ids), 400):
        batch = db.batch()
        for job_id in ids[offset : offset + 400]:
            batch.set(
                db.collection(JOBS_COLLECTION).document(job_id),
                {"status": "expired", "expired_at": now},
                merge=True,
            )
        batch.commit()
    return len(ids)


async def firestore_upsert_batch(jobs: list[JobDocument]) -> None:
    await run_in_thread(_upsert_jobs_sync, jobs)


async def firestore_mark_expired_batch(job_ids: Iterable[str]) -> int:
    return await run_in_thread(_mark_expired_sync, list(job_ids))


async def _finish(result: IngestRunResult, *, kind: str, time_frame: str) -> IngestRunResult:
    await run_in_thread(_finish_run_sync, result, time_frame=time_frame, kind=kind)
    return result


async def run_incremental_ingest(
    *,
    time_frame: str = "1h",
    client: Optional[JobIngestClient] = None,
) -> IngestRunResult:
    fj = client or get_fantastic_jobs_client()
    run_id = await run_in_thread(_start_run_sync, "incremental", time_frame)
    result = IngestRunResult(run_id=run_id, status="completed")
    cursor: str | None = None
    try:
        while True:
            page = await fj.fetch_active_ats(time_frame=time_frame, limit=1000, cursor=cursor)
            if not page.jobs:
                break
            docs: list[JobDocument] = []
            for raw in page.jobs:
                doc = to_job_document(raw)
                resolved = resolve_job_locations(doc)
                docs.append(doc.model_copy(update={"location_ids": resolved.location_ids}))
                result.unresolved_location_count += resolved.unresolved_count

            await firestore_upsert_batch(docs)
            try:
                await search_index_sync.upsert_batch(docs)
            except meili_unavailable_errors() as exc:
                logger.warning("Job Discovery Meili upsert failed: %s", exc)

            result.pages_completed += 1
            result.jobs_upserted += len(docs)
            result.credits_consumed += page.credits_consumed
            cursor = page.next_cursor
            if not cursor:
                break
    except Exception as exc:
        result.status = "failed"
        result.error = str(exc)
        await _finish(result, kind="incremental", time_frame=time_frame)
        raise
    return await _finish(result, kind="incremental", time_frame=time_frame)


async def run_expiry_sweep(
    *,
    time_frame: str = "1h",
    client: Optional[JobIngestClient] = None,
) -> IngestRunResult:
    fj = client or get_fantastic_jobs_client()
    run_id = await run_in_thread(_start_run_sync, "expiry", time_frame)
    result = IngestRunResult(run_id=run_id, status="completed")
    cursor: str | None = None
    try:
        while True:
            page = await fj.fetch_expired_ats(time_frame=time_frame, limit=1000, cursor=cursor)
            ids = [str(row.get("id")) for row in page.jobs if row.get("id")]
            if not ids:
                break
            result.jobs_expired += await firestore_mark_expired_batch(ids)
            try:
                await search_index_sync.delete_batch(ids)
            except meili_unavailable_errors() as exc:
                logger.warning("Job Discovery Meili expiry delete failed: %s", exc)
            result.pages_completed += 1
            cursor = page.next_cursor
            if not cursor:
                break
    except Exception as exc:
        result.status = "failed"
        result.error = str(exc)
        await _finish(result, kind="expiry", time_frame=time_frame)
        raise
    return await _finish(result, kind="expiry", time_frame=time_frame)


def _stale_active_ids_sync(days: int) -> list[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = (
        db.collection(JOBS_COLLECTION)
        .where(filter=firestore.FieldFilter("status", "==", "active"))
        .where(filter=firestore.FieldFilter("last_seen_at", "<", cutoff))
    )
    return [doc.id for doc in query.stream()]


async def run_staleness_sweep(*, days: int | None = None) -> IngestRunResult:
    stale_days = days or getattr(get_settings(), "job_discovery_stale_unseen_days", STALE_UNSEEN_DAYS)
    run_id = await run_in_thread(_start_run_sync, "staleness", f"{stale_days}d")
    result = IngestRunResult(run_id=run_id, status="completed")
    try:
        ids = await run_in_thread(_stale_active_ids_sync, stale_days)
        result.jobs_expired = await firestore_mark_expired_batch(ids)
        try:
            await search_index_sync.delete_batch(ids)
        except meili_unavailable_errors() as exc:
            logger.warning("Job Discovery Meili stale delete failed: %s", exc)
    except Exception as exc:
        result.status = "failed"
        result.error = str(exc)
        await _finish(result, kind="staleness", time_frame=f"{stale_days}d")
        raise
    return await _finish(result, kind="staleness", time_frame=f"{stale_days}d")


async def run_backfill_ingest(
    *,
    time_frame: str = "7d",
    credit_budget: int | None = None,
    client: Optional[JobIngestClient] = None,
    **params: str,
) -> IngestRunResult:
    fj = client or get_fantastic_jobs_client()
    budget = credit_budget if credit_budget is not None else get_settings().job_discovery_credit_budget
    run_id = await run_in_thread(_start_run_sync, "backfill", time_frame)
    result = IngestRunResult(run_id=run_id, status="completed")
    cursor: str | None = None
    try:
        while True:
            remaining = budget - result.credits_consumed
            if remaining <= 0:
                result.status = "partial_budget_exhausted"
                break
            page_limit = max(10, min(1000, remaining))
            page = await fj.fetch_active_ats(
                time_frame=time_frame,
                limit=page_limit,
                cursor=cursor,
                **params,
            )
            if not page.jobs:
                break
            batch = page.jobs[:remaining]
            credits = len(batch)
            docs = []
            for raw in batch:
                doc = to_job_document(raw)
                resolved = resolve_job_locations(doc)
                docs.append(doc.model_copy(update={"location_ids": resolved.location_ids}))
                result.unresolved_location_count += resolved.unresolved_count
            await firestore_upsert_batch(docs)
            try:
                await search_index_sync.upsert_batch(docs)
            except meili_unavailable_errors() as exc:
                logger.warning("Job Discovery Meili backfill upsert failed: %s", exc)
            result.pages_completed += 1
            result.jobs_upserted += len(docs)
            result.credits_consumed += credits
            cursor = page.next_cursor
            if not cursor or result.credits_consumed >= budget:
                if result.credits_consumed >= budget and cursor:
                    result.status = "partial_budget_exhausted"
                break
    except Exception as exc:
        result.status = "failed"
        result.error = str(exc)
        await _finish(result, kind="backfill", time_frame=time_frame)
        raise
    return await _finish(result, kind="backfill", time_frame=time_frame)

