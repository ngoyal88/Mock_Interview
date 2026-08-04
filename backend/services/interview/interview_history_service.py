"""Interview history and session detail operations."""
from datetime import datetime, timezone
from typing import Any, Optional

from firebase_admin import firestore

from firebase_config import db
from utils.domain_errors import DomainError

from utils.async_io import run_in_thread
from utils.logger import get_logger
from utils.redis_client import delete_session, get_session
from utils.session_access import require_session_owner

logger = get_logger("InterviewHistoryService")


def serialize_timestamp(ts: Any) -> Any:
    """Convert Firestore Timestamp or datetime to an ISO 8601 string."""
    if isinstance(ts, datetime):
        dt = ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    if hasattr(ts, "to_datetime"):
        try:
            dt = ts.to_datetime()
            if isinstance(dt, datetime):
                dt = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
        except Exception:
            pass
    return ts


async def list_interview_history(uid: str, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
    def _read() -> dict[str, list[dict[str, Any]]]:
        safe_limit = max(1, min(limit, 50))
        # Composite index required: interviews — user_id ASC, started_at DESC.
        # All persisted interviews set started_at at start/complete; docs missing it are excluded.
        docs = (
            db.collection("interviews")
            .where("user_id", "==", uid)
            .order_by("started_at", direction=firestore.Query.DESCENDING)
            .limit(safe_limit)
            .stream()
        )
        history: list[dict[str, Any]] = []
        for doc in docs:
            data = doc.to_dict() or {}
            data["id"] = doc.id
            for key in ("started_at", "completed_at", "created_at", "last_updated"):
                if key in data:
                    data[key] = serialize_timestamp(data[key])
            history.append(data)
        return {"history": history}

    return await run_in_thread(_read)


async def get_redis_session_details(session_id: str, uid: str) -> dict[str, Any]:
    session_data = await get_session(f"interview:{session_id}")
    require_session_owner(session_data, uid)
    return session_data


async def delete_interview_history(session_id: str, uid: str) -> dict[str, str]:
    def _delete() -> None:
        doc_ref = db.collection("interviews").document(session_id)
        snapshot = doc_ref.get()
        if not snapshot.exists:
            raise DomainError("interview_not_found", "Interview not found")

        data = snapshot.to_dict() or {}
        if data.get("user_id") != uid:
            raise DomainError("interview_forbidden", "Not authorized to delete this interview")

        doc_ref.delete()

    await run_in_thread(_delete)

    try:
        await delete_session(f"interview:{session_id}")
    except Exception:
        pass

    return {"message": "Interview deleted"}
