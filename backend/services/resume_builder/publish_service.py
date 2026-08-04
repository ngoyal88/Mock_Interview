from __future__ import annotations

from services.resume_builder.draft_store import delete_draft, get_draft
from services.resume_builder.layout_from_profile import builder_custom_sections_to_profile
from services.resume_builder.models import (
    PublishDraftRequest,
    PublishDraftResponse,
    default_resume_name,
    validate_publish_profile,
)
from services.resume_builder.render_service import render_draft_pdf
from services.vault.vault_service import (
    add_version,
    create_resume_entry,
    delete_resume_entry,
    get_vault_entry,
    set_active_resume,
)
from utils.logger import get_logger

log = get_logger(__name__)

_BUILDER_SOURCE_FILENAME = "resume-builder.pdf"
_BUILDER_CONTENT_TYPE = "application/pdf"


async def _rollback_created_entry(uid: str, resume_id: str) -> None:
    try:
        await delete_resume_entry(uid, resume_id)
    except Exception:
        log.exception("Resume Builder publish rollback failed uid=%s resume_id=%s", uid, resume_id)


def _builder_metadata(render_hash: str, draft, page_count: int) -> dict[str, object]:
    return {
        "template_id": draft.template_id,
        "template_version": draft.template_version,
        "render_engine": "typst",
        "render_input_hash": render_hash,
        "style_spec": draft.style_spec.model_dump(),
        "page_count": page_count,
        "section_layout": [section.model_dump() for section in draft.section_layout],
    }


async def publish_draft(uid: str, draft_id: str, request: PublishDraftRequest) -> PublishDraftResponse:
    draft = await get_draft(uid, draft_id)
    if not draft:
        raise ValueError("draft_not_found")

    validate_publish_profile(draft.profile, custom_sections=draft.custom_sections)
    publish_profile = builder_custom_sections_to_profile(draft.profile, draft.custom_sections)
    pdf_bytes, page_count, render_hash, _payload = await render_draft_pdf(draft)

    target_resume_id = request.target_resume_id or draft.target_resume_id
    if target_resume_id:
        entry = await get_vault_entry(uid, target_resume_id)
        if not entry:
            raise ValueError("resume_not_found")
        resume_id = target_resume_id
        created_new_entry = False
    else:
        resume_name = (request.resume_name or "").strip() or default_resume_name(draft.profile)
        entry = await create_resume_entry(
            uid,
            resume_name,
            request.tags,
            request.set_active,
            origin="builder",
        )
        resume_id = str(entry["id"])
        created_new_entry = True

    try:
        version, scorecard = await add_version(
            uid,
            resume_id,
            publish_profile.model_dump(),
            request.user_note.strip(),
            source_filename=_BUILDER_SOURCE_FILENAME,
            source_blob=pdf_bytes,
            content_type=_BUILDER_CONTENT_TYPE,
            action="builder_publish",
            builder_metadata=_builder_metadata(render_hash, draft, page_count),
        )
    except Exception:
        if created_new_entry:
            await _rollback_created_entry(uid, resume_id)
        raise

    if request.set_active:
        await set_active_resume(uid, resume_id)

    await delete_draft(uid, draft_id)

    entry = await get_vault_entry(uid, resume_id)
    if not entry:
        raise ValueError("resume_not_found")

    return PublishDraftResponse(
        resume_id=resume_id,
        version_id=str(version["id"]),
        entry=entry,
        version=version,
        scorecard=scorecard.model_dump(),
    )
