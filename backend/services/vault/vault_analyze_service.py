"""Vault re-analyze orchestration."""
from __future__ import annotations

from typing import Any, Optional

from services.vault.analysis_service import build_vault_scorecard
from services.vault.vault_service import (
    get_vault_entry,
    update_entry_scorecard,
    update_version_score,
)
from services.vault.vault_version_service import require_linked_version
from utils.domain_errors import DomainError
from utils.logger import get_logger

logger = get_logger(__name__)


async def analyze_vault_version(
    uid: str,
    *,
    resume_id: str,
    version_id: Optional[str],
    role: Optional[str],
) -> dict[str, Any]:
    entry = await get_vault_entry(uid, resume_id)
    if not entry:
        logger.warning(
            "Vault analyze rejected uid=%s resume_id=%s error=resume_not_found",
            uid,
            resume_id,
        )
        raise DomainError("resume_not_found", "Resume entry not found")

    resolved_version_id = version_id or entry.get("current_version_id")
    if not resolved_version_id:
        logger.warning(
            "Vault analyze rejected uid=%s resume_id=%s error=no_version_to_analyze",
            uid,
            resume_id,
        )
        raise DomainError("no_version_to_analyze", "No version available to analyze")

    try:
        version = await require_linked_version(uid, resume_id, resolved_version_id)
    except DomainError as exc:
        logger.warning(
            "Vault analyze rejected uid=%s resume_id=%s version_id=%s error=%s",
            uid,
            resume_id,
            resolved_version_id,
            exc.code,
        )
        raise

    profile_snapshot = version.get("profile_snapshot") or {}
    updates_entry_scorecard = resolved_version_id == entry.get("current_version_id")

    scorecard = await build_vault_scorecard(profile_snapshot, role=role)
    await update_version_score(uid, resolved_version_id, scorecard.score)
    if updates_entry_scorecard:
        await update_entry_scorecard(
            uid,
            resume_id,
            scorecard,
            version_number=version.get("version_number"),
            version_id=resolved_version_id,
            action="reanalyze",
            role=role,
        )

    return {
        "resume_id": resume_id,
        "version_id": resolved_version_id,
        "version_number": version.get("version_number"),
        "scorecard": scorecard.model_dump(),
        "entry_scorecard_updated": updates_entry_scorecard,
    }
