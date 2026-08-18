"""Reconcile Firestore active jobs against the active-only Meilisearch index."""
from __future__ import annotations

from firebase_admin import firestore

from firebase_config import db
from services.job_discovery.constants import JOBS_COLLECTION
from services.job_discovery.detail_service import get_job_document
from services.job_discovery.models import ReconciliationResult
from services.job_discovery.search import meilisearch_client, search_index_sync
from utils.async_io import run_in_thread


def _stream_active_job_ids_sync() -> set[str]:
    query = db.collection(JOBS_COLLECTION).where(filter=firestore.FieldFilter("status", "==", "active")).select([])
    return {doc.id for doc in query.stream()}


async def stream_active_job_ids() -> set[str]:
    return await run_in_thread(_stream_active_job_ids_sync)


def diff_id_sets(firestore_ids: set[str], meili_ids: set[str]) -> tuple[set[str], set[str]]:
    return firestore_ids - meili_ids, meili_ids - firestore_ids


async def run_reconciliation() -> ReconciliationResult:
    firestore_ids = await stream_active_job_ids()
    meili_ids = await meilisearch_client.list_all_ids()
    missing, extra = diff_id_sets(firestore_ids, meili_ids)

    upserted = 0
    if missing:
        docs = [await get_job_document(job_id) for job_id in sorted(missing)]
        await search_index_sync.upsert_batch(docs)
        upserted = len(docs)

    deleted = 0
    if extra:
        await search_index_sync.delete_batch(extra)
        deleted = len(extra)

    return ReconciliationResult(
        missing_in_meili=missing,
        extra_in_meili=extra,
        upserted=upserted,
        deleted=deleted,
    )

