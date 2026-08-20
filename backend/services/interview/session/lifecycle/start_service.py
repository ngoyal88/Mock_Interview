"""Interview start orchestration."""
import uuid
from typing import Any, Dict, Optional

from firebase_admin import firestore
from utils.domain_errors import DomainError

from firebase_config import db
from models.interview import InterviewSession, InterviewType
from services.profile_memory.profile_claims_repository import get_profile_memory_summary
from services.interview.session.lifecycle.session_events import SessionEvent, SessionEventType, SessionStateMachine
from services.interview.catalog.registry import get_mode_capabilities, is_startable_interview_type
from services.interview.catalog.start_request import (
    StartBlindRequest,
    StartInterviewRequest,
    StartPairProgrammingRequest,
    StartPressureRequest,
    StartResumeRequest,
    StartRoleTargetedRequest,
)
from services.interview.modes.role_targeted.start import hydrate_role_targeted_start
from services.interview.session.runtime.interview_service import InterviewService
from utils.async_io import run_in_thread
from utils.logger import get_logger
from utils.redis_client import create_session

logger = get_logger("InterviewStartService")

# Re-export for routes/tests
__all__ = [
    "StartInterviewRequest",
    "StartRoleTargetedRequest",
    "StartResumeRequest",
    "StartPairProgrammingRequest",
    "extract_candidate_name",
    "load_active_resume",
    "start_interview_session",
]


def extract_candidate_name(resume_data: Optional[dict]) -> Optional[str]:
    if not isinstance(resume_data, dict):
        return None
    name = resume_data.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    if isinstance(name, dict):
        raw = name.get("raw")
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return None


async def load_active_resume(uid: str) -> Dict[str, Any]:
    from services.vault.resume_snapshot_loader import load_active_resume_snapshot

    return await load_active_resume_snapshot(uid)


def _session_target_fields(
    interview_type: InterviewType,
    target_context: Dict[str, Any],
) -> Dict[str, Optional[str]]:
    """Map mode target_context well-known keys onto flat session fields."""
    tc = target_context or {}
    fields: Dict[str, Optional[str]] = {
        "target_company": tc.get("target_company"),
        "target_role": tc.get("target_role"),
        "job_description": tc.get("job_description"),
        "interview_focus": None,
        "track": None,
        "session_focus": None,
    }
    if interview_type == InterviewType.ROLE_TARGETED:
        fields["interview_focus"] = tc.get("interview_focus")
    elif interview_type == InterviewType.PAIR_PROGRAMMING:
        fields["track"] = tc.get("track") or "dsa"
        fields["session_focus"] = tc.get("session_focus")
    return fields


async def start_interview_session(
    request: StartInterviewRequest,
    uid: str,
    *,
    interview_service: InterviewService,
    session_ttl: int,
) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    interview_type = request.interview_type

    resume_data: Dict[str, Any] = request.resume_data or {}
    if not resume_data:
        resume_data = await load_active_resume(uid)

    if not is_startable_interview_type(interview_type):
        raise DomainError(
            "mode_disabled",
            f"{interview_type.value} mode is currently disabled.",
        )

    caps = get_mode_capabilities(interview_type)
    if caps.requires_resume and not resume_data:
        raise DomainError(
            "resume_required",
            "Upload an active resume in Vault before starting this interview mode.",
        )

    mode_config = request.config
    snapshot_data: Optional[Dict[str, Any]] = None
    if interview_type == InterviewType.ROLE_TARGETED:
        mode_config, snapshot_data = await hydrate_role_targeted_start(uid, request.config)

    start_payload = await interview_service.prepare_mode_start(
        interview_type=interview_type,
        difficulty=request.difficulty,
        resume_data=resume_data,
        years_experience=request.years_experience,
        config=mode_config,
    )
    jd_fit_context = start_payload["jd_fit_context"]
    if snapshot_data and isinstance(snapshot_data.get("jd_fit_context"), dict):
        jd_fit_context = snapshot_data["jd_fit_context"]
    resume_probe_context = start_payload["resume_probe_context"]
    target_context = dict(start_payload["target_context"] or {})
    profile_memory_summary = await get_profile_memory_summary(uid)
    if profile_memory_summary.get("accepted_count"):
        target_context["profile_memory_summary"] = profile_memory_summary
    seeded_questions: list[Dict[str, Any]] = start_payload["seeded_questions"]

    session_fields = _session_target_fields(interview_type, target_context)
    target_company = session_fields["target_company"]
    target_role = session_fields["target_role"]
    job_description = session_fields["job_description"]
    interview_focus = session_fields["interview_focus"]
    pair_track = session_fields["track"]
    session_focus = session_fields["session_focus"]

    if not seeded_questions:
        first_question = await interview_service.generate_first_question(
            interview_type,
            request.difficulty,
            resume_data,
            target_role if interview_type == InterviewType.ROLE_TARGETED else None,
            request.years_experience,
            target_context=target_context,
        )
        seeded_questions = [first_question]
    first_question = seeded_questions[0]

    candidate_name = request.candidate_name or extract_candidate_name(resume_data) or uid

    session = InterviewSession(
        session_id=session_id,
        user_id=uid,
        candidate_name=candidate_name,
        years_experience=request.years_experience,
        interview_type=interview_type,
        custom_role=None,
        target_company=target_company,
        target_role=target_role,
        job_description=job_description,
        interview_focus=interview_focus,
        track=pair_track,
        session_focus=session_focus,
        jd_fit_context=jd_fit_context,
        resume_probe_context=resume_probe_context,
        difficulty=request.difficulty,
        questions=seeded_questions,
        resume_data=resume_data or {},
        last_event_id=f"{session_id}:start",
    )
    session.status = SessionStateMachine.transition(
        session.status,
        SessionEvent(type=SessionEventType.START),
    ).value

    await create_session(
        f"interview:{session_id}",
        session.model_dump(mode="json"),
        expire_seconds=session_ttl,
    )

    try:
        seed_payload = {
            "session_id": session_id,
            "user_id": uid,
            "candidate_name": candidate_name,
            "years_experience": request.years_experience,
            "interview_type": interview_type.value,
            "difficulty": request.difficulty.value,
            "custom_role": None,
            "target_company": target_company,
            "target_role": target_role,
            "job_description": job_description,
            "interview_focus": interview_focus,
            "track": pair_track,
            "session_focus": session_focus,
            "jd_fit_context": jd_fit_context,
            "resume_probe_context": resume_probe_context,
            "questions": seeded_questions,
            "current_question_index": 0,
            "status": "active",
            "started_at": firestore.SERVER_TIMESTAMP,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_updated": firestore.SERVER_TIMESTAMP,
            "questions_answered": 0,
            "code_problems_attempted": 0,
        }

        def _write() -> None:
            db.collection("interviews").document(session_id).set(seed_payload)

        await run_in_thread(_write)
    except Exception as e:
        logger.warning("Failed to persist interview start to Firestore: %s", e)

    logger.info(
        "interview_started",
        extra={
            "session_id": session_id,
            "user_id": uid,
            "interview_type": str(interview_type),
        },
    )

    return {
        "message": "Interview session started",
        "session_id": session_id,
        "question": first_question,
        "interview_type": interview_type,
        "difficulty": request.difficulty,
    }
