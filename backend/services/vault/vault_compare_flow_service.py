"""Vault compare endpoint orchestration."""
from __future__ import annotations

from typing import Any, Optional

from services.vault.compare_service import compare_profiles
from services.vault.vault_service import get_vault_entry
from services.vault.vault_version_service import require_linked_version
from utils.domain_errors import DomainError
from utils.logger import get_logger

logger = get_logger(__name__)


async def compare_vault_versions(
    uid: str,
    *,
    resume_a_id: str,
    resume_b_id: str,
    version_a_id: Optional[str],
    version_b_id: Optional[str],
    role: Optional[str],
) -> dict[str, Any]:
    if (
        resume_a_id == resume_b_id
        and version_a_id
        and version_b_id
        and version_a_id == version_b_id
    ):
        raise DomainError("same_version_compare", "Select two different versions to compare")

    entry_a = await get_vault_entry(uid, resume_a_id)
    entry_b = await get_vault_entry(uid, resume_b_id)
    if not entry_a or not entry_b:
        logger.warning(
            "Vault compare rejected uid=%s resume_a=%s resume_b=%s error=resume_not_found",
            uid,
            resume_a_id,
            resume_b_id,
        )
        raise DomainError("resume_not_found", "Resume entry not found")

    resolved_a_id = version_a_id or entry_a.get("current_version_id")
    resolved_b_id = version_b_id or entry_b.get("current_version_id")
    if not resolved_a_id or not resolved_b_id:
        raise DomainError("version_not_found", "Version not found")

    if resolved_a_id == resolved_b_id:
        raise DomainError("same_version_compare", "Select two different versions to compare")

    try:
        version_a = await require_linked_version(
            uid,
            resume_a_id,
            resolved_a_id,
            mismatch_code="version_a_mismatch",
        )
        version_b = await require_linked_version(
            uid,
            resume_b_id,
            resolved_b_id,
            mismatch_code="version_b_mismatch",
        )
    except DomainError as exc:
        logger.warning(
            "Vault compare rejected uid=%s resume_a=%s resume_b=%s error=%s",
            uid,
            resume_a_id,
            resume_b_id,
            exc.code,
        )
        raise

    profile_a = version_a.get("profile_snapshot") or {}
    profile_b = version_b.get("profile_snapshot") or {}

    result = await compare_profiles(profile_a, profile_b, role=role)
    result["resume_a_id"] = resume_a_id
    result["resume_b_id"] = resume_b_id
    result["resume_a_version_id"] = resolved_a_id
    result["resume_b_version_id"] = resolved_b_id
    result["resume_a_name"] = entry_a.get("name")
    result["resume_b_name"] = entry_b.get("name")
    result["version_a_number"] = version_a.get("version_number")
    result["version_b_number"] = version_b.get("version_number")
    result["version_a_filename"] = version_a.get("source_filename")
    result["version_b_filename"] = version_b.get("source_filename")
    result["version_a_has_source_file"] = bool(version_a.get("has_source_file"))
    result["version_b_has_source_file"] = bool(version_b.get("has_source_file"))
    return result
