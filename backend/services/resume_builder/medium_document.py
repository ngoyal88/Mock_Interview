from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal, Sequence
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from models.resume import ResumeProfile
from services.resume_builder.layout_from_profile import section_has_content
from services.resume_builder.models import BuilderCustomSection, BuilderSection, ResumeBuilderDraft
from services.resume_builder.style_spec import StyleSpec, hydrate_style_spec
from services.resume_builder.template_catalog import get_template

MediumSchemaVersion = Literal[1]

_MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)
_PRESENT_TOKENS = frozenset({"present", "current", "now", "ongoing"})


class MediumLink(BaseModel):
    kind: str
    href: str
    display_text: str


class MediumIdentity(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[MediumLink] = Field(default_factory=list)


class MediumEntry(BaseModel):
    primary: str = ""
    secondary: str = ""
    tertiary: str = ""
    date_display: str = ""
    location: str = ""
    bullets: list[str] = Field(default_factory=list)
    links: list[MediumLink] = Field(default_factory=list)
    extra_lines: list[str] = Field(default_factory=list)


class MediumSkillGroup(BaseModel):
    label: str
    items: list[str] = Field(default_factory=list)


class MediumSection(BaseModel):
    id: str
    kind: str
    heading: str
    summary_text: str = ""
    entries: list[MediumEntry] = Field(default_factory=list)
    skill_groups: list[MediumSkillGroup] = Field(default_factory=list)
    flat_skills: list[str] = Field(default_factory=list)
    custom_lines: list[str] = Field(default_factory=list)


class MediumReadyDocument(BaseModel):
    schema_version: MediumSchemaVersion = 1
    page_size: str
    template_id: str
    identity: MediumIdentity
    sections: list[MediumSection] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _parse_year_month(raw: str) -> tuple[int | None, int | None]:
    text = _clean(raw).lower()
    if not text or text in _PRESENT_TOKENS:
        return None, None
    if re.fullmatch(r"\d{4}", text):
        return int(text), None
    m = re.fullmatch(r"(\d{4})[-/](\d{1,2})", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(\d{1,2})[-/](\d{4})", text)
    if m:
        return int(m.group(2)), int(m.group(1))
    for idx, month in enumerate(_MONTHS, start=1):
        if month.lower() in text:
            year_match = re.search(r"(19|20)\d{2}", text)
            if year_match:
                return int(year_match.group(0)), idx
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.year, parsed.month
    except ValueError:
        return None, None


def _format_month_year(year: int | None, month: int | None, date_format: str) -> str:
    if year is None:
        return ""
    if date_format == "year_only":
        return str(year)
    if date_format == "numeric":
        if month is None:
            return f"{year:04d}"
        return f"{month:02d}/{year:04d}"
    if month is None:
        return str(year)
    return f"{_MONTHS[month - 1]} {year}"


def format_date_display(start: str, end: str, *, date_format: str) -> str:
    start_text = _clean(start)
    end_text = _clean(end)
    end_present = end_text.lower() in _PRESENT_TOKENS if end_text else False
    start_fmt = _format_month_year(*_parse_year_month(start_text), date_format)
    if end_present:
        end_fmt = "Present"
    else:
        end_fmt = _format_month_year(*_parse_year_month(end_text), date_format)
    if start_fmt and end_fmt:
        return f"{start_fmt} – {end_fmt}"
    return start_fmt or end_fmt


def _short_link_label(kind: str, href: str) -> str:
    lowered = kind.lower()
    if lowered == "linkedin":
        return "LinkedIn"
    if lowered == "github":
        return "GitHub"
    if lowered == "portfolio":
        return "Portfolio"
    if lowered == "project":
        return "(Try it here)"
    host = urlparse(href).netloc.lower()
    if "linkedin.com" in host:
        return "LinkedIn"
    if "github.com" in host:
        return "GitHub"
    if host:
        return host.removeprefix("www.")
    return "Link"


def resolve_link(kind: str, href: str, *, link_display: str) -> MediumLink | None:
    url = _clean(href)
    if not url:
        return None
    display = url if link_display == "full_url" else _short_link_label(kind, url)
    return MediumLink(kind=kind, href=url, display_text=display)


def _identity_links(profile: ResumeProfile, style: StyleSpec) -> list[MediumLink]:
    links: list[MediumLink] = []
    contact = profile.contact
    if not contact:
        return links
    link_map = contact.links
    if not link_map:
        return links
    for kind in ("linkedin", "github", "portfolio"):
        resolved = resolve_link(kind, getattr(link_map, kind, "") or "", link_display=style.link_display)
        if resolved:
            links.append(resolved)
    for other in link_map.other or []:
        resolved = resolve_link("other", other, link_display=style.link_display)
        if resolved:
            links.append(resolved)
    return links


def _section_heading(section: BuilderSection) -> str:
    return _clean(section.label) or section.kind.replace("_", " ").title()


def _work_entries(profile: ResumeProfile, style: StyleSpec) -> list[MediumEntry]:
    entries: list[MediumEntry] = []
    for row in profile.work_experience:
        if not any(_clean(value) for value in (row.title, row.company, row.location)):
            continue
        bullets = [_clean(b) for b in [*row.responsibilities, *row.impact] if _clean(b)]
        entries.append(
            MediumEntry(
                primary=_clean(row.title),
                secondary=_clean(row.company),
                tertiary="",
                date_display=format_date_display(row.start_date or "", row.end_date or "", date_format=style.date_format),
                location=_clean(row.location),
                bullets=bullets,
            )
        )
    return entries


def _education_entries(profile: ResumeProfile, style: StyleSpec) -> list[MediumEntry]:
    entries: list[MediumEntry] = []
    for row in profile.education:
        if not any(_clean(value) for value in (row.degree, row.field, row.institution)):
            continue
        degree_bits = [_clean(row.degree), _clean(row.field)]
        degree_line = ", ".join(part for part in degree_bits if part)
        extra: list[str] = []
        for highlight in row.highlights or []:
            label = _clean(highlight.label)
            text = _clean(highlight.text)
            if label and text:
                extra.append(f"{label}: {text}")
            elif text:
                extra.append(text)
        cgpa = _clean(row.cgpa)
        if cgpa:
            extra.append(cgpa if cgpa.lower().startswith(("cgpa", "gpa")) else f"CGPA: {cgpa}")
        entries.append(
            MediumEntry(
                primary=degree_line,
                secondary=_clean(row.institution),
                date_display=format_date_display(row.start_date or "", row.end_date or "", date_format=style.date_format),
                location=_clean(row.location),
                extra_lines=extra,
            )
        )
    return entries


def _project_entries(profile: ResumeProfile, style: StyleSpec) -> list[MediumEntry]:
    entries: list[MediumEntry] = []
    for row in profile.projects:
        if not any(_clean(value) for value in (row.name, row.description, row.link)):
            continue
        bullets = [_clean(line) for line in (row.description or "").splitlines() if _clean(line)]
        link = resolve_link("project", row.link or "", link_display=style.link_display)
        entries.append(
            MediumEntry(
                primary=_clean(row.name) or "Project",
                secondary=_clean(row.role),
                date_display=format_date_display(row.start_date or "", row.end_date or "", date_format=style.date_format),
                bullets=bullets,
                links=[link] if link else [],
            )
        )
    return entries


def _achievement_entries(profile: ResumeProfile, style: StyleSpec) -> list[MediumEntry]:
    entries: list[MediumEntry] = []
    for row in profile.achievements:
        if not _clean(row.title) and not _clean(row.description):
            continue
        date_text = _clean(row.date)
        date_display = format_date_display(date_text, "", date_format=style.date_format) if date_text else ""
        entries.append(
            MediumEntry(
                primary=_clean(row.title) or "Achievement",
                date_display=date_display,
                bullets=[_clean(row.description)] if _clean(row.description) else [],
            )
        )
    return entries


def _publication_entries(profile: ResumeProfile) -> list[MediumEntry]:
    entries: list[MediumEntry] = []
    for row in profile.publications:
        if not _clean(row.title):
            continue
        secondary_bits = []
        if _clean(row.year):
            secondary_bits.append(_clean(row.year))
        if _clean(row.venue):
            secondary_bits.append(_clean(row.venue))
        entries.append(
            MediumEntry(
                primary=_clean(row.title),
                secondary=". ".join(secondary_bits),
            )
        )
    return entries


def _skills_section(profile: ResumeProfile, style: StyleSpec, heading: str) -> MediumSection | None:
    groups: list[MediumSkillGroup] = []
    flat: list[str] = []
    for group in profile.skills:
        label = _clean(group.label) or "Skills"
        items = [_clean(item) for item in group.items if _clean(item)]
        if not items:
            continue
        groups.append(MediumSkillGroup(label=label, items=items))
        flat.extend(items)
    if not groups:
        return None
    section = MediumSection(id="skills", kind="skills", heading=heading, skill_groups=groups, flat_skills=flat)
    if style.skills_layout == "flat_line":
        section.skill_groups = []
    else:
        section.flat_skills = []
    return section


def _custom_lines(custom: BuilderCustomSection | None) -> list[str]:
    if custom is None:
        return []
    return [_clean(line) for line in custom.content.splitlines() if _clean(line)]


def _template_field_warnings(template_id: str, profile: ResumeProfile) -> list[str]:
    metadata = get_template(template_id)
    warnings: list[str] = []
    section_fields = metadata.sections or {}
    if section_fields.get("projects") and profile.projects:
        allowed = set(section_fields["projects"].fields or [])
        if allowed and "tech_stack" not in allowed:
            if any(item.tech_stack for item in profile.projects):
                warnings.append("projects.tech_stack ignored by template")
    return warnings


def build_medium_ready_document(
    draft: ResumeBuilderDraft,
    *,
    style_spec: StyleSpec | None = None,
) -> MediumReadyDocument:
    if isinstance(style_spec, StyleSpec):
        style = style_spec
    else:
        style = hydrate_style_spec(style_spec or getattr(draft, "style_spec", None))
    profile = draft.profile
    custom_lookup = {section.id: section for section in draft.custom_sections}
    sections: list[MediumSection] = []

    for section in draft.section_layout:
        if not section.enabled or section.kind == "identity":
            continue
        if section.kind != "custom" and not section_has_content(profile, section.kind):
            continue
        heading = _section_heading(section)
        if section.kind == "summary" and _clean(profile.summary):
            sections.append(
                MediumSection(
                    id=section.id,
                    kind="summary",
                    heading=heading,
                    summary_text=_clean(profile.summary),
                )
            )
        elif section.kind == "work_experience":
            entries = _work_entries(profile, style)
            if entries:
                sections.append(MediumSection(id=section.id, kind="work_experience", heading=heading, entries=entries))
        elif section.kind == "education":
            entries = _education_entries(profile, style)
            if entries:
                sections.append(MediumSection(id=section.id, kind="education", heading=heading, entries=entries))
        elif section.kind == "skills":
            skills = _skills_section(profile, style, heading)
            if skills:
                sections.append(skills)
        elif section.kind == "projects":
            entries = _project_entries(profile, style)
            if entries:
                sections.append(MediumSection(id=section.id, kind="projects", heading=heading, entries=entries))
        elif section.kind == "achievements":
            entries = _achievement_entries(profile, style)
            if entries:
                sections.append(MediumSection(id=section.id, kind="achievements", heading=heading, entries=entries))
        elif section.kind == "publications":
            entries = _publication_entries(profile)
            if entries:
                sections.append(MediumSection(id=section.id, kind="publications", heading=heading, entries=entries))
        elif section.kind == "custom":
            lines = _custom_lines(custom_lookup.get(section.id))
            if lines:
                sections.append(
                    MediumSection(id=section.id, kind="custom", heading=heading, custom_lines=lines)
                )

    identity = MediumIdentity(
        name=_clean(profile.name),
        email=_clean(profile.contact.email if profile.contact else ""),
        phone=_clean(profile.contact.phone if profile.contact else ""),
        location=_clean(profile.contact.location if profile.contact else ""),
        links=_identity_links(profile, style),
    )
    if profile.contact and _clean(profile.contact.email):
        email_link = resolve_link("email", f"mailto:{_clean(profile.contact.email)}", link_display=style.link_display)
        if email_link:
            email_link.display_text = _clean(profile.contact.email)
            identity.links.insert(0, email_link)

    return MediumReadyDocument(
        page_size=style.page_size,
        template_id=draft.template_id,
        identity=identity,
        sections=sections,
        warnings=_template_field_warnings(draft.template_id, profile),
    )
