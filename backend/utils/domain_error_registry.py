"""Map DomainError codes to HTTP status + response detail shape."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException

from utils.domain_errors import DomainError

_VAULT_CONTEXT_FALLBACKS = {
    "analyze": "Resume analysis failed",
    "compare": "Resume comparison failed",
    "restore": "Restore failed",
    "download": "Download failed",
    "update": "Update failed",
}


@dataclass(frozen=True)
class ErrorSpec:
    status: int
    structured: bool = False


ERROR_REGISTRY: dict[str, ErrorSpec] = {
    # Vault
    "resume_not_found": ErrorSpec(404),
    "version_not_found": ErrorSpec(404),
    "no_version_to_analyze": ErrorSpec(404),
    "no_source_file": ErrorSpec(404),
    "file_storage_unavailable": ErrorSpec(503),
    "same_version_compare": ErrorSpec(400),
    "version_a_mismatch": ErrorSpec(409),
    "version_b_mismatch": ErrorSpec(409),
    "version_resume_mismatch": ErrorSpec(400),
    "invalid_name": ErrorSpec(400),
    "tags_invalid": ErrorSpec(400),
    "empty_file": ErrorSpec(400),
    "file_too_large": ErrorSpec(413),
    "unsupported_file_type": ErrorSpec(400),
    "resume_limit_reached": ErrorSpec(403),
    "version_limit_reached": ErrorSpec(403),
    "version_create_failed": ErrorSpec(400),
    "parse_rejected": ErrorSpec(400),
    # JD Fit
    "jd_fit_disabled": ErrorSpec(503),
    "target_role_required": ErrorSpec(400, structured=True),
    "jd_too_short": ErrorSpec(400, structured=True),
    "profile_insufficient": ErrorSpec(422, structured=True),
    "snapshot_not_found": ErrorSpec(404, structured=True),
    "extract_failed": ErrorSpec(400),
    # Job Discovery
    "job_discovery_disabled": ErrorSpec(503),
    "job_discovery.search_unavailable": ErrorSpec(503, structured=True),
    "job_not_found": ErrorSpec(404),
    # Interview / session
    "session_not_found": ErrorSpec(404),
    "session_owner_missing": ErrorSpec(403),
    "session_forbidden": ErrorSpec(403),
    "interview_not_found": ErrorSpec(404),
    "interview_forbidden": ErrorSpec(403),
    "question_not_found": ErrorSpec(404),
    "no_test_cases": ErrorSpec(400),
    "mode_disabled": ErrorSpec(400),
    "resume_required": ErrorSpec(400),
    "coding_mode_required": ErrorSpec(403),
    "pair_track_unavailable": ErrorSpec(400),
    # Resume builder / LinkedIn
    "identity_name_missing": ErrorSpec(422, structured=True),
    "identity_email_missing": ErrorSpec(422, structured=True),
    "identity_email_invalid": ErrorSpec(422, structured=True),
    "content_empty_resume": ErrorSpec(422, structured=True),
    "invalid_input": ErrorSpec(400, structured=True),
    "provider_unconfigured": ErrorSpec(503, structured=True),
    "scrape_timeout": ErrorSpec(504, structured=True),
    "scrape_failed": ErrorSpec(502, structured=True),
    "provider_auth_failed": ErrorSpec(503, structured=True),
    "profile_not_found": ErrorSpec(404, structured=True),
    # Career preferences
    "career_preferences_invalid_value": ErrorSpec(400, structured=True),
}


def _resolve_status(exc: DomainError, spec: ErrorSpec) -> int:
    override = exc.context.get("http_status")
    if isinstance(override, int):
        return override
    return spec.status


def resolve_domain_error(exc: DomainError) -> HTTPException:
    spec = ERROR_REGISTRY.get(exc.code)
    if spec is None:
        return HTTPException(400, exc.message or exc.code)

    status = _resolve_status(exc, spec)
    structured = spec.structured or bool(exc.context.get("structured"))
    detail: object = exc.as_detail() if structured else exc.message
    return HTTPException(status, detail)


def resolve_value_error_code(code: str, *, context: str = "vault") -> HTTPException:
    """Bridge legacy ValueError string codes (vault_service) to HTTP responses."""
    if code == "version_resume_mismatch":
        if context in {"compare", "restore"}:
            return HTTPException(409, "Version is no longer linked to its resume entry")
        return HTTPException(400, "version_id does not belong to resume_id")

    known_messages = {
        "resume_not_found": "Resume entry not found",
        "version_not_found": "Version not found",
        "no_version_to_analyze": "No version available to analyze",
        "no_source_file": "No file stored for this version",
        "file_storage_unavailable": "Resume file storage is not available",
        "same_version_compare": "Select two different versions to compare",
        "version_a_mismatch": "version_a_id is no longer linked to resume_a_id",
        "version_b_mismatch": "version_b_id is no longer linked to resume_b_id",
        "invalid_name": "Resume name cannot be blank.",
        "tags_invalid": "tags must be an array of strings",
    }
    if code in known_messages:
        return resolve_domain_error(DomainError(code, known_messages[code]))

    fallback = _VAULT_CONTEXT_FALLBACKS.get(context, f"{context} request failed")
    return HTTPException(400, fallback)
