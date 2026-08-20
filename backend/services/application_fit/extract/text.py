"""Ephemeral JD file text extraction and normalization (no persistence)."""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from services.application_fit.weights import MIN_JD_CHARS
from services.resume.resume_parser import extract_text_with_metadata
from utils.domain_errors import DomainError

JD_EXTRACT_MAX_BYTES = 2 * 1024 * 1024
JD_EXTRACT_MAX_CHARS = 8000

_ALLOWED_JD_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


def clean_optional_text(value: Optional[str], max_len: int = 8000) -> Optional[str]:
    if value is None:
        return None
    cleaned = " ".join(str(value).split()).strip()
    if not cleaned:
        return None
    return cleaned[:max_len]


def normalize_job_description_text(value: str | None, *, max_len: int = JD_EXTRACT_MAX_CHARS) -> str | None:
    """Collapse whitespace and cap length for LLM token efficiency."""
    return clean_optional_text(value, max_len=max_len)


def _normalize_jd_text(raw: str) -> str:
    """Collapse all whitespace to single spaces for LLM token efficiency."""
    collapsed = re.sub(r"\s+", " ", raw or "").strip()
    return collapsed[:JD_EXTRACT_MAX_CHARS]


def _allowed_jd_filename(filename: str) -> bool:
    lower = (filename or "").lower().strip()
    return any(lower.endswith(ext) for ext in _ALLOWED_JD_EXTENSIONS)


def extract_jd_text_from_bytes(blob: bytes, filename: str) -> Tuple[str, List[str]]:
    """Extract JD plain text from an uploaded file blob. Raises DomainError on failure."""
    if not blob:
        raise DomainError("empty_file", "empty file")
    if len(blob) > JD_EXTRACT_MAX_BYTES:
        raise DomainError("file_too_large", "File too large. Max size 2 MB.")

    safe_name = (filename or "jd.txt").strip() or "jd.txt"
    if not _allowed_jd_filename(safe_name):
        raise DomainError("unsupported_file_type", "Unsupported file type. Allowed: PDF, TXT, MD, DOCX.")

    try:
        raw_text, meta = extract_text_with_metadata(blob, safe_name)
    except ValueError as exc:
        raise DomainError("extract_failed", str(exc)) from exc
    except Exception as exc:
        raise DomainError("extract_failed", "Could not extract text from file") from exc

    text = _normalize_jd_text(raw_text)
    if not text:
        raise DomainError("extract_failed", "Could not extract text from file")

    warnings: List[str] = []
    if isinstance(meta, dict):
        for item in meta.get("warnings") or []:
            if isinstance(item, str) and item.strip():
                warnings.append(item.strip())

    return text, warnings
