"""User discovery settings stored on users/{uid}.job_discovery."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from config import get_settings
from firebase_admin import firestore

from firebase_config import db
from services.job_discovery.models import DiscoverySettings, DiscoverySettingsPatch, JobDiscoveryDisabledError
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


def _read_sync(uid: str) -> dict[str, Any]:
    snap = db.collection("users").document(uid).get()
    if not snap.exists:
        return {}
    data = snap.to_dict() or {}
    settings = data.get("job_discovery")
    return settings if isinstance(settings, dict) else {}


async def get(uid: str) -> DiscoverySettings:
    if not get_settings().job_discovery_enabled:
        raise JobDiscoveryDisabledError()
    raw = await run_in_thread(_read_sync, uid)
    normalized = {key: _serialize_ts(value) for key, value in raw.items()}
    return DiscoverySettings(**normalized)


async def patch(uid: str, body: DiscoverySettingsPatch) -> DiscoverySettings:
    current = await get(uid)
    updates = body.model_dump(exclude_unset=True)
    merged = current.model_copy(update=updates)
    payload = merged.model_dump(mode="python")
    payload["updated_at"] = firestore.SERVER_TIMESTAMP
    await run_in_thread(lambda: db.collection("users").document(uid).set({"job_discovery": payload}, merge=True))
    return merged

