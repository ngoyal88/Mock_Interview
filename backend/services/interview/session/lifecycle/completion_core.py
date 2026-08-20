"""Shared interview completion logic for REST, LiveKit, and WS transports."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from fastapi.encoders import jsonable_encoder
from firebase_admin import firestore

from config import get_settings
from firebase_config import db
from models.interview import InterviewSession
from services.interview.session.lifecycle.completion_guard import try_begin_completion
from services.interview.session.lifecycle.session_events import (
    SessionEvent,
    SessionEventType,
    SessionStateMachine,
)
from services.interview.session.runtime.interview_service import InterviewService
from services.interview.session.persistence.transcript_service import attach_transcript_to_session
from services.profile_memory.profile_claims_service import run_profile_claims_pipeline
from utils.async_io import run_in_thread
from utils.feedback_parser import parse_scores_from_feedback
from utils.logger import get_logger

logger = get_logger("InterviewCompletionCore")

TransportKind = Literal["rest", "livekit", "websocket"]


def parse_started_at(session_data: dict[str, Any]) -> datetime:
    started_at_raw = session_data.get("started_at")
    if isinstance(started_at_raw, str):
        try:
            return datetime.fromisoformat(started_at_raw.replace("Z", "+00:00"))
        except Exception:
            pass
    elif isinstance(started_at_raw, datetime):
        return started_at_raw if started_at_raw.tzinfo else started_at_raw.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def compute_duration_minutes(session_data: dict[str, Any]) -> int:
    started_at = parse_started_at(session_data)
    return int(max(0, (datetime.now(timezone.utc) - started_at).total_seconds() / 60))


def build_feedback_payload(
    session_data: dict[str, Any],
    *,
    completion_reason: str,
    duration_minutes: int,
) -> dict[str, Any]:
    return {
        "interview_type": session_data.get("interview_type"),
        "custom_role": session_data.get("custom_role"),
        "target_company": session_data.get("target_company"),
        "target_role": session_data.get("target_role"),
        "job_description": session_data.get("job_description"),
        "interview_focus": session_data.get("interview_focus"),
        "jd_fit_context": session_data.get("jd_fit_context"),
        "resume_probe_context": session_data.get("resume_probe_context"),
        "completion_reason": completion_reason,
        "duration": duration_minutes,
        "responses": session_data.get("responses", []),
        "code_submissions": session_data.get("code_submissions", []),
        "live_transcription": session_data.get("live_transcription", []),
        "session_conductor": session_data.get("session_conductor"),
    }


def completion_reason_to_event(
    completion_reason: str,
    *,
    disconnect_mode: bool,
    transport: TransportKind = "livekit",
) -> SessionEventType:
    if disconnect_mode:
        return SessionEventType.DISCONNECT_TIMEOUT
    if completion_reason == "complete":
        return SessionEventType.COMPLETE
    if completion_reason == "silence_timeout":
        return SessionEventType.SILENCE_TIMEOUT
    if completion_reason == "tab_away_timeout":
        return SessionEventType.TAB_AWAY_TIMEOUT
    if completion_reason == "max_duration":
        return SessionEventType.MAX_DURATION
    if completion_reason == "user_ended":
        return SessionEventType.MANUAL_END
    if completion_reason == "candidate_disconnected":
        if transport == "websocket":
            return SessionEventType.DISCONNECT_TIMEOUT
        return SessionEventType.ERROR_END
    if completion_reason == "error":
        return SessionEventType.ERROR_END
    return SessionEventType.MANUAL_END


def resolve_terminal_status(current_status: str, completion_reason: str, *, disconnect_mode: bool, transport: TransportKind) -> str:
    event_type = completion_reason_to_event(
        completion_reason,
        disconnect_mode=disconnect_mode,
        transport=transport,
    )
    return SessionStateMachine.transition(
        current_status or "active",
        SessionEvent(type=event_type, reason=completion_reason),
    ).value


def parse_feedback_scores(final_feedback: Any) -> Optional[dict[str, Any]]:
    if not isinstance(final_feedback, dict):
        return None
    scores = parse_scores_from_feedback(final_feedback.get("feedback"))
    return scores if scores else None


def build_terminal_patch(
    session_data: dict[str, Any],
    *,
    terminal_status: str,
    completion_reason: str,
    completed_at_iso: str,
    duration_minutes: int,
    final_feedback: Any | None,
) -> dict[str, Any]:
    patch: dict[str, Any] = {
        "status": terminal_status,
        "completion_reason": completion_reason,
        "completed_at": completed_at_iso,
        "last_updated": completed_at_iso,
        "duration_minutes": duration_minutes,
        "questions_answered": len(session_data.get("responses", []) or []),
        "code_problems_attempted": len(session_data.get("code_submissions", []) or []),
        "live_transcription": session_data.get("live_transcription", []),
    }
    if final_feedback is not None:
        patch["final_feedback"] = final_feedback
    return patch


def build_firestore_completion_payload(
    session_id: str,
    session_data: dict[str, Any],
    *,
    terminal_status: str,
    completion_reason: str,
    duration_minutes: int,
    final_feedback: Any,
    scores: Optional[dict[str, Any]],
    replay_highlights: Any = None,
    interview_session: Optional[InterviewSession] = None,
) -> dict[str, Any]:
    if interview_session is not None:
        payload = jsonable_encoder(
            {
                "session_id": session_id,
                "user_id": interview_session.user_id,
                "candidate_name": interview_session.candidate_name,
                "interview_type": interview_session.interview_type.value,
                "difficulty": interview_session.difficulty.value,
                "custom_role": interview_session.custom_role,
                "target_company": interview_session.target_company,
                "target_role": interview_session.target_role,
                "job_description": interview_session.job_description,
                "interview_focus": interview_session.interview_focus,
                "jd_fit_context": interview_session.jd_fit_context,
                "status": terminal_status,
                "duration_minutes": duration_minutes,
                "questions_answered": len(interview_session.responses),
                "code_problems_attempted": len(interview_session.code_submissions),
                "responses": interview_session.responses,
                "questions": interview_session.questions,
                "code_submissions": [s.dict() for s in interview_session.code_submissions],
                "live_transcription": session_data.get("live_transcription", []),
                "final_feedback": final_feedback,
                "replay_highlights": replay_highlights,
                "scores": scores,
                "pass": (scores or {}).get("overall", 0) >= 6 if scores else False,
            }
        )
        payload.setdefault("started_at", interview_session.started_at)
        payload.setdefault("created_at", interview_session.started_at)
        if not payload.get("scores"):
            payload.pop("scores", None)
    else:
        payload = {
            "status": terminal_status,
            "completion_reason": completion_reason,
            "duration_minutes": duration_minutes,
            "questions_answered": len(session_data.get("responses", []) or []),
            "code_problems_attempted": len(session_data.get("code_submissions", []) or []),
            "responses": session_data.get("responses", []),
            "questions": session_data.get("questions", []),
            "code_submissions": session_data.get("code_submissions", []),
            "live_transcription": session_data.get("live_transcription", []),
            "final_feedback": final_feedback,
            "scores": scores,
        }

    payload["last_updated"] = firestore.SERVER_TIMESTAMP
    payload["completed_at"] = firestore.SERVER_TIMESTAMP
    return payload


async def persist_completion_firestore(session_id: str, payload: dict[str, Any]) -> None:
    try:
        def _write() -> None:
            db.collection("interviews").document(session_id).set(payload, merge=True)

        await run_in_thread(_write)
    except Exception as exc:
        logger.warning("Failed to persist interview completion to Firestore: %s", exc)


def schedule_vpm_after_completion(
    session_id: str,
    session_data: dict[str, Any],
    interview_service: InterviewService,
) -> None:
    async def _run_vpm_task() -> None:
        if not get_settings().vpm_enabled:
            return
        try:
            result = await run_profile_claims_pipeline(
                uid=str(session_data.get("user_id") or ""),
                session_id=session_id,
                session_data=session_data,
                engine=interview_service._engine,  # noqa: SLF001
            )
            if result.get("failed") or result.get("pipeline_status") == "failed":
                logger.warning(
                    "VPM pipeline failed session=%s reason=%s",
                    session_id,
                    result.get("reason"),
                )
        except Exception as vpm_error:
            logger.warning("VPM pipeline failed session=%s error=%s", session_id, vpm_error)

    asyncio.create_task(_run_vpm_task())


@dataclass(frozen=True)
class CompletionOptions:
    completion_reason: str
    transport: TransportKind = "livekit"
    include_replay_highlights: bool = False
    trigger_vpm: bool = False
    disconnect_mode: bool = False
    feedback_timeout_seconds: float | None = None
    rest_full_firestore: bool = False


@dataclass
class CompletionResult:
    acquired: bool
    cached_api_response: dict[str, Any] | None
    session_data: dict[str, Any]
    terminal_patch: dict[str, Any]
    final_feedback: Any | None
    replay_highlights: Any | None
    terminal_status: str
    duration_minutes: int
    completed_at_iso: str
    scores: dict[str, Any] | None
    interview_session: InterviewSession | None = None


async def _generate_feedback(
    interview_service: InterviewService,
    feedback_payload: dict[str, Any],
    *,
    timeout_seconds: float | None,
) -> Any | None:
    if timeout_seconds is not None:
        try:
            return await asyncio.wait_for(
                interview_service.generate_final_feedback(feedback_payload),
                timeout_seconds,
            )
        except (asyncio.TimeoutError, Exception) as exc:
            logger.warning("Partial feedback generation failed: %s", exc)
            return None
    return await interview_service.generate_final_feedback(feedback_payload)


async def finalize_interview(
    session_id: str,
    session_data: dict[str, Any],
    *,
    interview_service: InterviewService,
    options: CompletionOptions,
    redis_client: Any | None = None,
) -> CompletionResult:
    begin = await try_begin_completion(session_id, session_data, redis_client=redis_client)
    if not begin.proceed:
        return CompletionResult(
            acquired=False,
            cached_api_response=begin.cached_response,
            session_data=dict(begin.session_data or session_data),
            terminal_patch={},
            final_feedback=(begin.session_data or session_data).get("final_feedback"),
            replay_highlights=None,
            terminal_status=str((begin.session_data or session_data).get("status") or ""),
            duration_minutes=int((begin.session_data or session_data).get("duration_minutes") or 0),
            completed_at_iso=str((begin.session_data or session_data).get("completed_at") or ""),
            scores=parse_feedback_scores((begin.session_data or session_data).get("final_feedback")),
        )

    working = dict(begin.session_data or session_data)
    attach_transcript_to_session(working)
    duration_minutes = compute_duration_minutes(working)
    completion_reason = options.completion_reason
    if not completion_reason and options.disconnect_mode:
        completion_reason = "candidate_disconnected"
    if not completion_reason:
        completion_reason = "ended_early" if working.get("status") != "completed" else "completed"

    responses = working.get("responses", []) or []
    final_feedback = working.get("final_feedback")
    should_generate_feedback = True
    if options.disconnect_mode:
        should_generate_feedback = len(responses) >= 2 and not final_feedback
    elif final_feedback:
        should_generate_feedback = False

    feedback_payload = build_feedback_payload(
        working,
        completion_reason=completion_reason,
        duration_minutes=duration_minutes,
    )
    if should_generate_feedback:
        final_feedback = await _generate_feedback(
            interview_service,
            feedback_payload,
            timeout_seconds=options.feedback_timeout_seconds,
        )

    replay_highlights = None
    if options.include_replay_highlights and final_feedback is not None:
        replay_highlights = await interview_service.generate_replay_highlights(feedback_payload)

    terminal_status = resolve_terminal_status(
        str(working.get("status") or "active"),
        completion_reason,
        disconnect_mode=options.disconnect_mode,
        transport=options.transport,
    )
    completed_at_iso = datetime.now(timezone.utc).isoformat()
    terminal_patch = build_terminal_patch(
        working,
        terminal_status=terminal_status,
        completion_reason=completion_reason,
        completed_at_iso=completed_at_iso,
        duration_minutes=duration_minutes,
        final_feedback=final_feedback,
    )
    working.update(terminal_patch)

    scores = parse_feedback_scores(final_feedback)
    interview_session: InterviewSession | None = None
    if options.rest_full_firestore:
        interview_session = InterviewSession(**working)
        interview_session.status = terminal_status
        interview_session.last_event_id = f"{session_id}:complete"
        interview_session.completion_reason = interview_session.completion_reason or completion_reason
        interview_session.completed_at = datetime.now(timezone.utc)
        interview_session.live_transcription = working.get("live_transcription", [])

    firestore_payload = build_firestore_completion_payload(
        session_id,
        working,
        terminal_status=terminal_status,
        completion_reason=completion_reason,
        duration_minutes=duration_minutes,
        final_feedback=final_feedback,
        scores=scores,
        replay_highlights=replay_highlights,
        interview_session=interview_session,
    )
    await persist_completion_firestore(session_id, firestore_payload)

    if options.trigger_vpm:
        schedule_vpm_after_completion(session_id, working, interview_service)

    return CompletionResult(
        acquired=True,
        cached_api_response=None,
        session_data=working,
        terminal_patch=terminal_patch,
        final_feedback=final_feedback,
        replay_highlights=replay_highlights,
        terminal_status=terminal_status,
        duration_minutes=duration_minutes,
        completed_at_iso=completed_at_iso,
        scores=scores,
        interview_session=interview_session,
    )
