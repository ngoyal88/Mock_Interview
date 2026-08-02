from __future__ import annotations

from utils.domain_errors import DomainError


class LinkedInImportError(DomainError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        http_status: int | None = None,
    ) -> None:
        context = {"http_status": http_status} if http_status is not None else None
        super().__init__(code, message, context=context or {})
