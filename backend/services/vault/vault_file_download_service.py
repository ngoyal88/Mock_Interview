"""Vault version file download orchestration."""
from __future__ import annotations

import asyncio

from services.vault import file_storage
from services.vault.vault_service import get_version_by_id
from utils.domain_errors import DomainError


async def load_version_file_bytes(uid: str, version_id: str) -> tuple[bytes, str, str | None]:
    """Return blob, media type, and source filename for a stored vault version."""
    version = await get_version_by_id(uid, version_id)
    if not version:
        raise DomainError("version_not_found", "Version not found")
    if not version.get("has_source_file"):
        raise DomainError("no_source_file", "No file stored for this version")

    resume_id = version.get("resume_id")
    if not resume_id:
        raise DomainError("version_not_found", "Version not found")

    source_filename = version.get("source_filename")
    try:
        blob = await asyncio.to_thread(
            file_storage.read_version_file,
            uid,
            resume_id,
            version_id,
            source_filename,
            storage_path=version.get("storage_path"),
            storage_backend=version.get("storage_backend"),
        )
    except FileNotFoundError:
        raise
    except RuntimeError as exc:
        raise DomainError("file_storage_unavailable", "Resume file storage is not available") from exc

    media_type = version.get("content_type") or file_storage.content_type_for_filename(source_filename)
    return blob, media_type, source_filename
