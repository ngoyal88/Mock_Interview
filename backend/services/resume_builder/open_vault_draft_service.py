"""Open an existing Builder draft for a Vault resume, or restore one from a version."""

from __future__ import annotations

from typing import Any, Optional

from services.resume_builder.draft_store import create_draft, find_draft_for_resume
from services.resume_builder.models import CreateDraftRequest, ResumeBuilderDraft
from services.resume_builder.vault_draft_seed import seed_draft_from_vault_version
from services.vault.vault_service import get_vault_entry, get_version_by_id, get_version_for_resume
from utils.domain_errors import DomainError


def _version_id(version: dict[str, Any]) -> str:
    return str(version.get("id") or "").strip()


async def _load_vault_version(
    uid: str,
    *,
    resume_id: str,
    version_id: Optional[str],
) -> dict[str, Any]:
    if version_id:
        version = await get_version_for_resume(uid, resume_id, version_id)
        if version:
            return version
        raise DomainError("version_not_found", "Source version not found")

    entry = await get_vault_entry(uid, resume_id)
    if not entry:
        raise DomainError("resume_not_found", "Source resume not found")
    current_version_id = str(entry.get("current_version_id") or "").strip()
    if not current_version_id:
        raise DomainError("version_not_found", "Source resume has no version")
    version = await get_version_for_resume(uid, resume_id, current_version_id)
    if not version:
        raise DomainError("version_not_found", "Source version not found")
    return version


async def open_or_restore_vault_draft(uid: str, request: CreateDraftRequest) -> ResumeBuilderDraft:
    resume_id = (request.resume_id or "").strip() or None
    version_id = (request.version_id or "").strip() or None
    cached_version: Optional[dict[str, Any]] = None

    if resume_id is None and version_id:
        cached_version = await get_version_by_id(uid, version_id)
        if not cached_version:
            raise DomainError("version_not_found", "Source version not found")
        resume_id = str(cached_version.get("resume_id") or "").strip() or None
        if not resume_id:
            raise DomainError("version_not_found", "Source version not found")

    if resume_id:
        existing = await find_draft_for_resume(uid, resume_id)
        if existing is not None:
            return existing

    if resume_id is None:
        raise DomainError("resume_not_found", "Source resume not found")

    if cached_version is not None:
        version = cached_version
    else:
        version = await _load_vault_version(uid, resume_id=resume_id, version_id=version_id)

    resolved_resume_id = str(version.get("resume_id") or resume_id).strip()
    resolved_version_id = _version_id(version) or version_id
    seed = seed_draft_from_vault_version(version, fallback_template_id=request.template_id)
    linked_request = request.model_copy(
        update={"resume_id": resolved_resume_id, "version_id": resolved_version_id},
    )
    return await create_draft(
        uid,
        linked_request,
        vault_draft_seed=seed,
        source_version_id=resolved_version_id,
    )
