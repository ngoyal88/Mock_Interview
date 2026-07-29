from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from models.resume import (
    AchievementItem,
    ContactInfo,
    ContactLinks,
    EducationRecord,
    ProjectItem,
    ResumeProfile,
    SkillGroup,
    WorkExperienceItem,
)

_SKILL_NOISE_RE = re.compile(r"\s*and\s*\+\d+\s+skills?$", re.IGNORECASE)


def _pick_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _format_date(value: dict[str, Any] | None, *, is_current: bool = False) -> str | None:
    if is_current:
        return "Present"
    if not isinstance(value, dict):
        return None
    year = value.get("year")
    month = _pick_str(value.get("month"))
    if month and year:
        return f"{month} {year}"
    if year:
        return str(year)
    return None



def _clean_skill_label(value: str) -> str:
    text = _SKILL_NOISE_RE.sub("", value.strip())
    return text.strip(" ,")


def _collect_skills(row: dict[str, Any]) -> list[str]:
    basic = row.get("basic_info") if isinstance(row.get("basic_info"), dict) else {}
    skills: list[str] = []
    seen: set[str] = set()

    def add(item: Any) -> None:
        label = _clean_skill_label(_pick_str(item))
        if not label:
            return
        key = label.lower()
        if key in seen:
            return
        seen.add(key)
        skills.append(label)

    for item in basic.get("top_skills") or []:
        add(item)

    for exp in row.get("experience") or []:
        if not isinstance(exp, dict):
            continue
        for item in exp.get("skills") or []:
            add(item)

    return skills[:40]


def _featured_links(featured: list[Any]) -> tuple[str | None, list[str]]:
    github: str | None = None
    other: list[str] = []
    seen: set[str] = set()

    for item in featured:
        if not isinstance(item, dict):
            continue
        url = _pick_str(item.get("url"))
        if not url or url.lower() in seen:
            continue
        seen.add(url.lower())
        host = (urlparse(url).netloc or "").lower()
        if "github.com" in host and github is None:
            github = url
        else:
            other.append(url)

    return github, other


def _map_experience(rows: list[Any]) -> list[WorkExperienceItem]:
    items: list[WorkExperienceItem] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = _pick_str(row.get("title"))
        company = _pick_str(row.get("company"))
        if not title and not company:
            continue
        tech_stack = [_clean_skill_label(_pick_str(item)) for item in row.get("skills") or []]
        tech_stack = [item for item in tech_stack if item]
        items.append(
            WorkExperienceItem(
                title=title or None,
                company=company or None,
                location=_pick_str(row.get("location")) or None,
                start_date=_format_date(row.get("start_date") if isinstance(row.get("start_date"), dict) else None),
                end_date=_format_date(
                    row.get("end_date") if isinstance(row.get("end_date"), dict) else None,
                    is_current=bool(row.get("is_current")),
                ),
                employment_type=_pick_str(row.get("employment_type")) or None,
                tech_stack=tech_stack,
            )
        )
    return items


def _map_education(rows: list[Any]) -> list[EducationRecord]:
    items: list[EducationRecord] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        institution = _pick_str(row.get("school"))
        degree = _pick_str(row.get("degree_name") or row.get("degree"))
        field = _pick_str(row.get("field_of_study"))
        if not institution and not degree:
            continue
        items.append(
            EducationRecord(
                institution=institution or None,
                degree=degree or None,
                field=field or None,
                start_date=_format_date(row.get("start_date") if isinstance(row.get("start_date"), dict) else None),
                end_date=_format_date(row.get("end_date") if isinstance(row.get("end_date"), dict) else None),
            )
        )
    return items


def _map_projects(rows: list[Any]) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = _pick_str(row.get("name"))
        description = _pick_str(row.get("description"))
        if not name and not description:
            continue
        items.append(ProjectItem(name=name or None, description=description or None))
    return items


def _map_honors(rows: list[Any]) -> list[AchievementItem]:
    items: list[AchievementItem] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = _pick_str(row.get("title"))
        if not title:
            continue
        items.append(
            AchievementItem(
                title=title,
                description=_pick_str(row.get("subtitle")) or None,
            )
        )
    return items


def apify_record_to_profile(row: dict[str, Any], *, linkedin_url: str) -> ResumeProfile:
    basic = row.get("basic_info") if isinstance(row.get("basic_info"), dict) else {}
    location = basic.get("location") if isinstance(basic.get("location"), dict) else {}
    featured = row.get("featured") if isinstance(row.get("featured"), list) else []
    github, other_links = _featured_links(featured)

    profile_url = _pick_str(basic.get("profile_url")) or linkedin_url
    summary = _pick_str(basic.get("about")) or _pick_str(basic.get("headline")) or None
    skills = _collect_skills(row)

    skill_groups: list[SkillGroup] = []
    if skills:
        skill_groups.append(SkillGroup(label="Skills", items=skills))

    return ResumeProfile(
        name=_pick_str(basic.get("fullname")) or None,
        summary=summary,
        contact=ContactInfo(
            location=_pick_str(location.get("full")) or None,
            links=ContactLinks(
                linkedin=profile_url,
                github=github,
                other=other_links,
            ),
        ),
        work_experience=_map_experience(row.get("experience") or []),
        education=_map_education(row.get("education") or []),
        projects=_map_projects(row.get("projects") or []),
        achievements=[item.model_dump() for item in _map_honors(row.get("honors") or [])],
        skills=skill_groups,
    )


def merge_import_identity(
    profile: ResumeProfile,
    *,
    fallback_email: str,
    fallback_name: str,
) -> ResumeProfile:
    updates: dict[str, Any] = {}
    if not _pick_str(profile.name) and fallback_name.strip():
        updates["name"] = fallback_name.strip()

    contact = profile.contact.model_copy(deep=True)
    email = _pick_str(contact.email)
    if not email or "@" not in email:
        contact.email = fallback_email.strip() or None

    if updates:
        return profile.model_copy(update={**updates, "contact": contact})
    return profile.model_copy(update={"contact": contact})


def import_warnings(profile: ResumeProfile, *, raw_row: dict[str, Any] | None = None) -> list[str]:
    del raw_row
    warnings: list[str] = []
    if not _pick_str(profile.summary):
        warnings.append("summary_missing")
    if not profile.work_experience:
        warnings.append("experience_missing")
    elif not any(item.responsibilities for item in profile.work_experience):
        warnings.append("experience_no_bullets")
    if not profile.education:
        warnings.append("education_missing")
    if not profile.skills:
        warnings.append("skills_missing")
    return warnings
