"""Vault version resolution helpers."""
from __future__ import annotations

from typing import Any

from services.vault.vault_service import get_version_by_id, get_version_for_resume
from utils.domain_errors import DomainError

_MISMATCH_MESSAGES = {
    "version_resume_mismatch": "version_id does not belong to resume_id",
    "version_a_mismatch": "version_a_id is no longer linked to resume_a_id",
    "version_b_mismatch": "version_b_id is no longer linked to resume_b_id",
}


async def require_linked_version(
    uid: str,
    resume_id: str,
    version_id: str,
    *,
    mismatch_code: str = "version_resume_mismatch",
) -> dict[str, Any]:
    """Return version doc linked to resume_id or raise DomainError with a stable code."""
    version = await get_version_for_resume(uid, resume_id, version_id)
    if version:
        return version

    detached_version = await get_version_by_id(uid, version_id)
    if detached_version:
        raise DomainError(
            mismatch_code,
            _MISMATCH_MESSAGES.get(mismatch_code, mismatch_code),
        )

    raise DomainError("version_not_found", "Version not found")
