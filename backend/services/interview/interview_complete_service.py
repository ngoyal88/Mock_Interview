"""Interview completion orchestration (REST adapter)."""
from typing import Any

from models.interview import InterviewSession
from services.interview.completion_guard import cached_completion_from_session
from services.interview.interview_completion_core import CompletionOptions, finalize_interview
from services.interview.interview_service import InterviewService
from services.interview.session_store import SessionStore
from utils.redis_client import get_session
from utils.session_access import require_session_owner


async def complete_interview_session(
    session_id: str,
    uid: str,
    *,
    interview_service: InterviewService,
    session_ttl: int,
) -> dict[str, Any]:
    session_data = await get_session(f"interview:{session_id}")
    require_session_owner(session_data, uid)

    result = await finalize_interview(
        session_id,
        session_data,
        interview_service=interview_service,
        options=CompletionOptions(
            completion_reason="complete",
            transport="rest",
            include_replay_highlights=True,
            rest_full_firestore=True,
        ),
    )

    if not result.acquired:
        if result.cached_api_response is not None:
            return result.cached_api_response
        cached = cached_completion_from_session(result.session_data)
        if cached:
            return cached
        return {"message": "Interview completion already in progress"}

    session = result.interview_session
    if session is None:
        session = InterviewSession(**result.session_data)

    session_dict = session.dict()
    session_dict["final_feedback"] = result.final_feedback
    session_dict["duration_minutes"] = result.duration_minutes
    session_dict["questions_answered"] = len(session.responses)
    session_dict["code_problems_attempted"] = len(session.code_submissions)

    store = SessionStore.for_session(session_id, ttl=session_ttl)

    def _apply_terminal(current: dict) -> dict:
        base = dict(current) if isinstance(current, dict) else {}
        base.update(session_dict)
        return base

    await store.update(_apply_terminal)

    return {
        "message": "Interview completed",
        "feedback": result.final_feedback,
        "duration_minutes": result.duration_minutes,
        "questions_answered": len(session.responses),
        "code_problems_attempted": len(session.code_submissions),
    }
