from __future__ import annotations

import asyncio
from dataclasses import dataclass

from firebase_admin import auth as firebase_auth

from firebase_config import db
from services.resume_builder.draft_store import create_draft
from services.resume_builder.linkedin_import.apify_client import get_apify_linkedin_client
from services.resume_builder.linkedin_import.to_profile import (
    apify_record_to_profile,
    import_warnings,
    merge_import_identity,
)
from services.resume_builder.linkedin_import.url import normalize_linkedin_input
from services.resume_builder.models import (
    CreateDraftRequest,
    LinkedInImportRequest,
    LinkedInImportResponse,
)
from services.resume_builder.template_catalog import get_template
from utils.logger import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class BuilderIdentity:
    name: str
    email: str


async def load_builder_identity(uid: str) -> BuilderIdentity:
    def _load() -> BuilderIdentity:
        name = ""
        email = ""
        snap = db.collection("users").document(uid).get()
        if snap.exists:
            data = snap.to_dict() or {}
            name = str(data.get("name") or "").strip()
            email = str(data.get("email") or "").strip()

        try:
            user = firebase_auth.get_user(uid)
            if not email and user.email:
                email = user.email.strip()
            if not name and user.display_name:
                name = user.display_name.strip()
        except Exception:
            log.debug("Could not load Firebase auth profile for uid=%s", uid, exc_info=True)

        return BuilderIdentity(name=name, email=email)

    return await asyncio.to_thread(_load)


async def import_linkedin_to_draft(uid: str, request: LinkedInImportRequest) -> LinkedInImportResponse:
    linkedin_url, username = normalize_linkedin_input(request.input)
    get_template(request.template_id)

    client = get_apify_linkedin_client()
    row = await client.fetch_profile(username)
    profile = apify_record_to_profile(row, linkedin_url=linkedin_url)

    identity = await load_builder_identity(uid)
    profile = merge_import_identity(
        profile,
        fallback_email=identity.email,
        fallback_name=identity.name,
    )
    warnings = import_warnings(profile, raw_row=row)

    draft = await create_draft(
        uid,
        CreateDraftRequest(template_id=request.template_id),
        source_profile=profile.model_dump(),
        source_kind="linkedin_import",
        source_linkedin_url=linkedin_url,
    )

    return LinkedInImportResponse(
        linkedin_url=linkedin_url,
        profile=draft.profile,
        draft=draft,
        warnings=warnings,
    )
