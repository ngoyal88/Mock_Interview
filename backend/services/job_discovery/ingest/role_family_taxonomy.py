"""Curated role-family taxonomy for demand-driven Fantastic.jobs title filters.

Ingest-only — not a product prefs catalog. Maps free-text titles → family keys
and builds provider title expressions.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class RoleFamily:
    key: str
    label: str
    title_terms: tuple[str, ...]


ROLE_FAMILIES: dict[str, RoleFamily] = {
    "sde": RoleFamily(
        key="sde",
        label="Software Engineering",
        title_terms=(
            "software engineer",
            "software developer",
            "backend engineer",
            "frontend engineer",
            "full stack engineer",
            "fullstack engineer",
            "full stack developer",
            "sde",
            "swe",
        ),
    ),
    "data_ml": RoleFamily(
        key="data_ml",
        label="Data / ML",
        title_terms=(
            "data scientist",
            "machine learning",
            "ml engineer",
            "ai engineer",
            "data engineer",
            "analytics engineer",
            "research scientist",
        ),
    ),
    "product": RoleFamily(
        key="product",
        label="Product",
        title_terms=(
            "product manager",
            "product management",
            "product owner",
            "associate product manager",
            "technical product manager",
        ),
    ),
    "design": RoleFamily(
        key="design",
        label="Design",
        title_terms=(
            "product designer",
            "ux designer",
            "ui designer",
            "design engineer",
            "graphic designer",
        ),
    ),
    "devops_sre": RoleFamily(
        key="devops_sre",
        label="DevOps / SRE",
        title_terms=(
            "devops",
            "site reliability",
            "sre",
            "platform engineer",
            "infrastructure engineer",
            "cloud engineer",
        ),
    ),
    "qa": RoleFamily(
        key="qa",
        label="QA",
        title_terms=(
            "qa engineer",
            "quality assurance",
            "sdet",
            "test engineer",
            "automation engineer",
        ),
    ),
    "security": RoleFamily(
        key="security",
        label="Security",
        title_terms=(
            "security engineer",
            "cybersecurity",
            "application security",
            "infosec",
            "security analyst",
        ),
    ),
}

ROLE_FAMILY_KEYS = frozenset(ROLE_FAMILIES)


def _phrase_pattern(term: str) -> re.Pattern[str]:
    parts = [re.escape(part) for part in term.casefold().split() if part]
    if not parts:
        return re.compile(r"(?!)")
    body = r"\s+".join(parts)
    return re.compile(rf"(?<![\w]){body}(?![\w])", re.IGNORECASE)


_TERM_PATTERNS: dict[str, tuple[tuple[re.Pattern[str], str], ...]] = {
    key: tuple((_phrase_pattern(term), term) for term in family.title_terms)
    for key, family in ROLE_FAMILIES.items()
}


def family_title_terms(family_key: str) -> tuple[str, ...]:
    family = ROLE_FAMILIES.get(family_key)
    if family is None:
        raise KeyError(f"Unknown role family for ingest: {family_key}")
    return family.title_terms


def classify_titles_to_families(titles: Iterable[str]) -> set[str]:
    matched: set[str] = set()
    for raw in titles:
        if not isinstance(raw, str) or not raw.strip():
            continue
        text = raw.strip()
        for family_key, patterns in _TERM_PATTERNS.items():
            if family_key in matched:
                continue
            if any(pattern.search(text) for pattern, _ in patterns):
                matched.add(family_key)
    return matched


def _term_expression(term: str) -> str:
    cleaned = " ".join(term.strip().split())
    if " " in cleaned:
        return f"'{cleaned}'"
    return cleaned


def family_title_expression(family_key: str) -> str:
    parts = [_term_expression(term) for term in family_title_terms(family_key)]
    if len(parts) == 1:
        return parts[0]
    return "(" + " | ".join(parts) + ")"
