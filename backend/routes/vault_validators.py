"""HTTP-boundary validators for vault routes (not domain services)."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException

from services.vault.vault_service import normalize_tags

MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/plain; charset=utf-8",
}
EDITABLE_ENTRY_FIELDS = {"name", "tags"}


def allowed_file(filename: Optional[str], content_type: Optional[str]) -> bool:
    if not filename or not filename.strip():
        return False
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False
    if content_type and content_type.strip():
        base_ct = content_type.split(";")[0].strip().lower()
        allowed_bases = {ct.split(";")[0].strip().lower() for ct in ALLOWED_CONTENT_TYPES}
        if base_ct not in allowed_bases:
            return False
    return True


def clean_optional_string(value: Any, field_name: str) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise HTTPException(400, f"{field_name} must be a string")
    cleaned = value.strip()
    return cleaned or None


def clean_required_string(value: Any, field_name: str) -> str:
    cleaned = clean_optional_string(value, field_name)
    if not cleaned:
        raise HTTPException(400, f"{field_name} is required")
    return cleaned


def normalize_tags_or_400(value: Any, *, allow_string: bool, error_message: str) -> list[str]:
    if value is None:
        return []
    if not allow_string and not isinstance(value, list):
        raise HTTPException(400, error_message)
    try:
        return normalize_tags(value)
    except ValueError as exc:
        if str(exc) == "tags_invalid":
            raise HTTPException(400, error_message) from exc
        raise


def parse_entry_update_payload(payload: dict[str, Any]) -> tuple[Optional[str], Optional[list[str]]]:
    unexpected_fields = sorted(set(payload) - EDITABLE_ENTRY_FIELDS)
    if unexpected_fields:
        joined = ", ".join(unexpected_fields)
        raise HTTPException(400, f"Unsupported fields for vault metadata update: {joined}")

    if not payload:
        raise HTTPException(400, "At least one of name or tags is required")

    has_name = "name" in payload
    has_tags = "tags" in payload
    if not has_name and not has_tags:
        raise HTTPException(400, "At least one of name or tags is required")

    name = payload.get("name")
    tags = payload.get("tags")

    if has_name and not isinstance(name, str):
        raise HTTPException(400, "name must be a string")
    normalized_tags = None
    if has_tags:
        normalized_tags = normalize_tags_or_400(
            tags,
            allow_string=False,
            error_message="tags must be an array of strings",
        )

    return name, normalized_tags
