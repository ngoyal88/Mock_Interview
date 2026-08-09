"""Domain-local models for Job Discovery."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from utils.domain_errors import DomainError

JobStatus = Literal["active", "expired"]
FeedSort = Literal["fit_then_fresh", "fresh_then_fit", "fresh_only"]


class JobDiscoveryDisabledError(DomainError):
    def __init__(self) -> None:
        super().__init__("job_discovery_disabled", "Job Discovery is temporarily unavailable")


class SearchBackendUnavailableError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            "job_discovery.search_unavailable",
            "Search is temporarily unavailable. Try again in a minute.",
        )


class JobNotFoundError(DomainError):
    def __init__(self, job_id: str) -> None:
        super().__init__("job_not_found", "Job not found", context={"job_id": job_id})


class LocationEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location_id: str
    country: str
    country_code: str
    region: Optional[str] = None
    city: Optional[str] = None
    catch_all: bool = False
    aliases: list[str] = Field(default_factory=list)
    fantastic_jobs_query: Optional[str] = None


class JobDocument(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    organization_name: str
    organization_slug: Optional[str] = None
    url: str
    date_posted: datetime
    date_created: Optional[datetime] = None
    location_ids: list[str] = Field(default_factory=list)
    locations_derived: list[str] = Field(default_factory=list)
    ai_work_arrangement: Optional[str] = None
    ai_experience_level: Optional[str] = None
    ai_employment_type: Optional[str] = None
    ai_salary_min: Optional[int] = None
    ai_salary_max: Optional[int] = None
    salary_raw: Optional[str] = None
    salary_is_estimated: bool = True
    ai_key_skills: list[str] = Field(default_factory=list)
    ai_core_responsibilities: Optional[str] = None
    ai_requirements_summary: Optional[str] = None
    ai_visa_sponsorship: Optional[str] = None
    organization_industry: Optional[str] = None
    organization_size: Optional[str] = None
    org_logo_permalink: Optional[str] = None
    description_text: Optional[str] = None
    status: JobStatus = "active"
    source: str = ""
    ingested_at: datetime
    last_seen_at: datetime
    expired_at: Optional[datetime] = None

    def to_firestore(self) -> dict[str, Any]:
        return self.model_dump(mode="python")

    def to_search_document(self) -> dict[str, Any]:
        from services.job_discovery.location_catalog import country_codes_from_location_ids

        return {
            "id": self.id,
            "title": self.title,
            "organization_name": self.organization_name,
            "organization_slug": self.organization_slug,
            "location_ids": self.location_ids,
            "country_codes": country_codes_from_location_ids(self.location_ids),
            "ai_work_arrangement": self.ai_work_arrangement,
            "ai_experience_level": self.ai_experience_level,
            "ai_employment_type": self.ai_employment_type,
            "salary_min": self.ai_salary_min,
            "salary_max": self.ai_salary_max,
            "salary_is_estimated": self.salary_is_estimated,
            "organization_industry": self.organization_industry,
            "organization_size": self.organization_size,
            "ai_visa_sponsorship": self.ai_visa_sponsorship,
            "ai_key_skills": self.ai_key_skills,
            "date_posted_ts": int(self.date_posted.timestamp()),
            "org_logo_permalink": self.org_logo_permalink,
            "status": self.status,
        }


class JobCard(BaseModel):
    id: str
    title: str
    organization_name: str
    organization_slug: Optional[str] = None
    org_logo_permalink: Optional[str] = None
    location_ids: list[str] = Field(default_factory=list)
    ai_work_arrangement: Optional[str] = None
    ai_experience_level: Optional[str] = None
    ai_employment_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_is_estimated: bool = True
    date_posted_ts: Optional[int] = None
    status: JobStatus = "active"


class JobDetail(JobDocument):
    saved: bool = False


class SearchFilters(BaseModel):
    q: str = ""
    location_ids: list[str] = Field(default_factory=list)
    country_codes: list[str] = Field(default_factory=list)
    work_arrangements: list[str] = Field(default_factory=list)
    experience_levels: list[str] = Field(default_factory=list)
    employment_types: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    organization_sizes: list[str] = Field(default_factory=list)
    organization_slugs: list[str] = Field(default_factory=list)
    visa_sponsorship: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    has_salary_only: bool = False
    posted_within_days: Optional[int] = None
    sort: Literal["fresh", "salary"] = "fresh"


class SearchResult(BaseModel):
    cards: list[JobCard]
    total: int
    page: int
    page_size: int


class SavedJob(BaseModel):
    job_id: str
    saved_at: datetime
    applied_at: Optional[datetime] = None
    fit_snapshot_id: Optional[str] = None
    job: Optional[JobDetail] = None


class SavedJobsResponse(BaseModel):
    saved_jobs: list[SavedJob]


class SaveJobRequest(BaseModel):
    fit_snapshot_id: Optional[str] = None
    applied_at: Optional[datetime] = None


class SaveJobResponse(BaseModel):
    job_id: str
    saved: bool


class DiscoverySettings(BaseModel):
    feed_sort: FeedSort = "fresh_then_fit"
    min_fit_score: Optional[int] = Field(default=None, ge=0, le=100)
    default_fit_resume_id: Optional[str] = None
    freshness_window_days: int = Field(default=14, ge=1, le=30)
    last_feed_visit_at: Optional[datetime] = None


class DiscoverySettingsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feed_sort: Optional[FeedSort] = None
    min_fit_score: Optional[int] = Field(default=None, ge=0, le=100)
    default_fit_resume_id: Optional[str] = None
    freshness_window_days: Optional[int] = Field(default=None, ge=1, le=30)
    last_feed_visit_at: Optional[datetime] = None


class IngestPage(BaseModel):
    jobs: list[dict[str, Any]] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    credits_consumed: int = 0


class IngestRunResult(BaseModel):
    run_id: str
    status: Literal["completed", "partial_budget_exhausted", "failed"]
    pages_completed: int = 0
    jobs_upserted: int = 0
    jobs_expired: int = 0
    credits_consumed: int = 0
    unresolved_location_count: int = 0
    error: Optional[str] = None


class ReconciliationResult(BaseModel):
    missing_in_meili: set[str] = Field(default_factory=set)
    extra_in_meili: set[str] = Field(default_factory=set)
    upserted: int = 0
    deleted: int = 0

