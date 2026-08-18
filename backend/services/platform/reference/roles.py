"""Supported role labels for interview / setup pickers (product catalog).

Not Fantastic.jobs ingest taxonomy — that stays in job_discovery/ingest.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SupportedRole:
    id: str
    label: str
    aliases: tuple[str, ...] = ()


SUPPORTED_ROLES: Final[tuple[SupportedRole, ...]] = (
    SupportedRole(id="software_engineer", label="Software Engineer", aliases=("SWE", "SDE")),
    SupportedRole(id="frontend_engineer", label="Frontend Engineer"),
    SupportedRole(id="backend_engineer", label="Backend Engineer"),
    SupportedRole(id="full_stack_engineer", label="Full Stack Engineer"),
    SupportedRole(id="mobile_engineer", label="Mobile Engineer"),
    SupportedRole(id="android_engineer", label="Android Engineer"),
    SupportedRole(id="ios_engineer", label="iOS Engineer"),
    SupportedRole(id="devops_engineer", label="DevOps Engineer"),
    SupportedRole(id="site_reliability_engineer", label="Site Reliability Engineer", aliases=("SRE",)),
    SupportedRole(id="cloud_engineer", label="Cloud Engineer"),
    SupportedRole(id="platform_engineer", label="Platform Engineer"),
    SupportedRole(id="data_engineer", label="Data Engineer"),
    SupportedRole(id="machine_learning_engineer", label="Machine Learning Engineer", aliases=("ML Engineer",)),
    SupportedRole(id="ai_engineer", label="AI Engineer"),
    SupportedRole(id="data_scientist", label="Data Scientist"),
    SupportedRole(id="data_analyst", label="Data Analyst"),
    SupportedRole(id="product_engineer", label="Product Engineer"),
    SupportedRole(id="qa_engineer", label="QA Engineer"),
    SupportedRole(id="security_engineer", label="Security Engineer"),
    SupportedRole(id="system_design_architecture", label="System Design / Architecture"),
    SupportedRole(id="engineering_manager", label="Engineering Manager"),
    SupportedRole(id="product_manager", label="Product Manager", aliases=("PM",)),
    SupportedRole(id="technical_program_manager", label="Technical Program Manager", aliases=("TPM",)),
    SupportedRole(id="business_analyst", label="Business Analyst"),
)

ROLE_LABELS: Final[tuple[str, ...]] = tuple(role.label for role in SUPPORTED_ROLES)
ROLE_LABEL_SET: Final[frozenset[str]] = frozenset(ROLE_LABELS)
