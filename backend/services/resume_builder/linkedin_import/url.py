from __future__ import annotations

import re
from urllib.parse import unquote, urlparse

from services.resume_builder.linkedin_import.errors import LinkedInImportError

_SLUG_RE = re.compile(r"^[A-Za-z0-9\-_%]+$")
_BLOCKED_PATH_PREFIXES = ("/company/", "/school/", "/jobs/", "/groups/", "/showcase/")


def _canonical_profile_url(username: str) -> str:
    slug = username.strip().strip("/")
    return f"https://www.linkedin.com/in/{slug}"


def normalize_linkedin_input(raw: str) -> tuple[str, str]:
    """Return canonical profile URL and LinkedIn username slug."""
    text = (raw or "").strip()
    if not text:
        raise LinkedInImportError("invalid_input", "Enter a LinkedIn username or profile URL.", status_code=400)

    if "linkedin.com" in text.lower():
        candidate = text if "://" in text else f"https://{text.lstrip('/')}"
        parsed = urlparse(candidate)
        host = (parsed.netloc or "").lower()
        if host and "linkedin.com" not in host:
            raise LinkedInImportError("invalid_input", "Enter a LinkedIn profile URL or username.", status_code=400)

        path = unquote(parsed.path or "").lower()
        for blocked in _BLOCKED_PATH_PREFIXES:
            if blocked in path:
                raise LinkedInImportError(
                    "invalid_input",
                    "Use a personal profile URL (linkedin.com/in/username), not a company or job page.",
                    status_code=400,
                )

        match = re.search(r"/in/([^/?#]+)", path, flags=re.IGNORECASE)
        if not match:
            raise LinkedInImportError(
                "invalid_input",
                "Use a personal profile URL (linkedin.com/in/username).",
                status_code=400,
            )
        username = match.group(1).strip("/")
    else:
        username = text.strip("/@")

    if not username or not _SLUG_RE.match(username):
        raise LinkedInImportError("invalid_input", "Enter a valid LinkedIn username.", status_code=400)

    return _canonical_profile_url(username), username
