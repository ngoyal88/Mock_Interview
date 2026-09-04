"""Pure helpers: turn a Vault version into Builder draft fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

from pydantic import ValidationError

from models.resume import ResumeProfile
from services.resume.profile_normalizer import profile_snapshot_dict
from services.resume_builder.layout_from_profile import derive_layout_from_profile
from services.resume_builder.models import BuilderCustomSection, BuilderSection
from services.resume_builder.style_spec import StyleSpec, default_style_spec, hydrate_style_spec
from services.resume_builder.template_catalog import get_template


@dataclass(frozen=True)
class VaultDraftSeed:
    profile: ResumeProfile
    template_id: str
    template_version: str
    style_spec: StyleSpec
    section_layout: list[BuilderSection]
    custom_sections: list[BuilderCustomSection]


def _resolve_template_ids(template_id: str, fallback_template_id: str) -> tuple[str, str]:
    try:
        template = get_template(template_id)
    except ValueError:
        template = get_template(fallback_template_id)
        return template.id, template.version
    if template.status != "live":
        fallback = get_template(fallback_template_id)
        return fallback.id, fallback.version
    return template.id, template.version


def _parse_stored_layout(raw: Any) -> Optional[list[BuilderSection]]:
    if not isinstance(raw, list) or not raw:
        return None
    sections: list[BuilderSection] = []
    try:
        for item in raw:
            if not isinstance(item, dict):
                return None
            sections.append(BuilderSection.model_validate(item))
    except ValidationError:
        return None
    identity = [section for section in sections if section.kind == "identity"]
    if len(identity) != 1 or not identity[0].enabled:
        return None
    ids = [section.id for section in sections]
    if len(ids) != len(set(ids)):
        return None
    return sections


def _custom_sections_from_layout(
    layout: Sequence[BuilderSection],
    profile: ResumeProfile,
) -> tuple[list[BuilderCustomSection], ResumeProfile]:
    custom_rows = [section for section in layout if section.kind == "custom"]
    profile_items = list(profile.custom_sections)
    custom_sections: list[BuilderCustomSection] = []
    for index, row in enumerate(custom_rows):
        if index < len(profile_items):
            item = profile_items[index]
            title = (item.title or "").strip() or row.label.strip() or "Custom Section"
            content = "\n".join(
                line.strip() for line in item.lines if isinstance(line, str) and line.strip()
            )
        else:
            title = row.label.strip() or "Custom Section"
            content = ""
        custom_sections.append(BuilderCustomSection(id=row.id, title=title, content=content))
    cleared = profile.model_copy(update={"custom_sections": []})
    return custom_sections, cleared


def _seed_from_derived_layout(
    profile: ResumeProfile,
    *,
    fallback_template_id: str,
) -> VaultDraftSeed:
    layout, custom_sections, cleared = derive_layout_from_profile(profile)
    template_id, template_version = _resolve_template_ids(fallback_template_id, fallback_template_id)
    return VaultDraftSeed(
        profile=cleared,
        template_id=template_id,
        template_version=template_version,
        style_spec=default_style_spec(),
        section_layout=layout,
        custom_sections=custom_sections,
    )


def seed_draft_from_vault_version(
    version: dict[str, Any],
    *,
    fallback_template_id: str,
) -> VaultDraftSeed:
    """Build draft fields from a Vault version. Client template_id is fallback only."""
    snapshot = version.get("profile_snapshot") or {}
    profile = ResumeProfile.model_validate(profile_snapshot_dict(snapshot if isinstance(snapshot, dict) else {}))
    builder = version.get("builder")
    if not isinstance(builder, dict) or not builder:
        return _seed_from_derived_layout(profile, fallback_template_id=fallback_template_id)

    layout = _parse_stored_layout(builder.get("section_layout"))
    if layout is None:
        return _seed_from_derived_layout(profile, fallback_template_id=fallback_template_id)

    stored_template_id = str(builder.get("template_id") or "").strip() or fallback_template_id
    template_id, template_version = _resolve_template_ids(stored_template_id, fallback_template_id)
    custom_sections, cleared = _custom_sections_from_layout(layout, profile)
    return VaultDraftSeed(
        profile=cleared,
        template_id=template_id,
        template_version=template_version,
        style_spec=hydrate_style_spec(builder.get("style_spec")),
        section_layout=list(layout),
        custom_sections=custom_sections,
    )
