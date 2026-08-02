"""Domain-layer errors — no HTTP status; routes/registry map to HTTP responses."""
from __future__ import annotations

from typing import Any


class DomainError(Exception):
    def __init__(self, code: str, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.context = context or {}

    def as_detail(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}
