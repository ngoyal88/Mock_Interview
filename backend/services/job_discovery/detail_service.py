"""Firestore-backed job detail reads."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from config import get_settings
from firebase_config import db
from services.job_discovery.constants import JOBS_COLLECTION
from services.job_discovery.models import JobDetail, JobDiscoveryDisabledError, JobDocument, JobNotFoundError
from utils.async_io import run_in_thread


def _serialize_ts(value: Any) -> Any:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if hasattr(value, "to_datetime"):
        try:
            return value.to_datetime()
        except Exception:
            return value
    return value


def _normalize_doc(data: dict[str, Any], job_id: str) -> dict[str, Any]:
    normalized = {key: _serialize_ts(value) for key, value in data.items()}
    normalized["id"] = str(normalized.get("id") or job_id)
    return normalized


def _get_job_sync(job_id: str) -> Optional[dict[str, Any]]:
    snap = db.collection(JOBS_COLLECTION).document(job_id).get()
    if not snap.exists:
        return None
    return _normalize_doc(snap.to_dict() or {}, snap.id)


async def get_job_document(job_id: str) -> JobDocument:
    if not get_settings().job_discovery_enabled:
        raise JobDiscoveryDisabledError()
    data = await run_in_thread(_get_job_sync, job_id)
    if not data:
        raise JobNotFoundError(job_id)
    return JobDocument(**data)


async def get_job_detail(job_id: str, *, uid: str | None = None) -> JobDetail:
    job = await get_job_document(job_id)
    saved = False
    if uid:
        saved = await run_in_thread(
            lambda: db.collection("users").document(uid).collection("saved_jobs").document(job_id).get().exists
        )
    return JobDetail(**job.model_dump(), saved=saved)

