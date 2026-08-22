"""Saved jobs user subcollection service."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from config import get_settings
from firebase_admin import firestore

from firebase_config import db
from services.job_discovery.constants import SAVED_JOBS_COLLECTION
from services.job_discovery.detail_service import get_job_detail, get_job_document
from services.job_discovery.models import (
    JobDiscoveryDisabledError,
    SaveJobRequest,
    SaveJobResponse,
    SavedJob,
    SavedJobsResponse,
)
from utils.async_io import run_in_thread


def _saved_ref(uid: str, job_id: str):
    return db.collection("users").document(uid).collection(SAVED_JOBS_COLLECTION).document(job_id)


def _serialize_ts(value: Any) -> Any:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if hasattr(value, "to_datetime"):
        try:
            return value.to_datetime()
        except Exception:
            return value
    return value


async def save(uid: str, job_id: str, body: Optional[SaveJobRequest] = None) -> SaveJobResponse:
    await get_job_document(job_id)
    payload: dict[str, Any] = {"saved_at": firestore.SERVER_TIMESTAMP}
    if body:
        updates = body.model_dump(exclude_unset=True)
        if "fit_snapshot_id" in updates:
            payload["fit_snapshot_id"] = updates["fit_snapshot_id"]
        if "applied_at" in updates:
            payload["applied_at"] = updates["applied_at"] or firestore.DELETE_FIELD
    await run_in_thread(lambda: _saved_ref(uid, job_id).set(payload, merge=True))
    return SaveJobResponse(job_id=job_id, saved=True)


async def unsave(uid: str, job_id: str) -> SaveJobResponse:
    if not get_settings().job_discovery_enabled:
        raise JobDiscoveryDisabledError()
    await run_in_thread(lambda: _saved_ref(uid, job_id).delete())
    return SaveJobResponse(job_id=job_id, saved=False)


def _list_saved_sync(uid: str, limit: int) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    query = (
        db.collection("users")
        .document(uid)
        .collection(SAVED_JOBS_COLLECTION)
        .order_by("saved_at", direction=firestore.Query.DESCENDING)
        .limit(max(1, min(limit, 100)))
    )
    for doc in query.stream():
        rows.append((doc.id, doc.to_dict() or {}))
    return rows


async def list_saved(uid: str, *, limit: int = 50) -> SavedJobsResponse:
    if not get_settings().job_discovery_enabled:
        raise JobDiscoveryDisabledError()
    rows = await run_in_thread(_list_saved_sync, uid, limit)
    saved_jobs: list[SavedJob] = []
    for job_id, row in rows:
        job = None
        try:
            job = await get_job_detail(job_id, uid=uid)
        except Exception:
            job = None
        saved_jobs.append(
            SavedJob(
                job_id=job_id,
                saved_at=_serialize_ts(row.get("saved_at")) or datetime.now(timezone.utc),
                applied_at=_serialize_ts(row.get("applied_at")),
                fit_snapshot_id=row.get("fit_snapshot_id"),
                job=job,
            )
        )
    return SavedJobsResponse(saved_jobs=saved_jobs)

