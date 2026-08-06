"""Pydantic models for career preferences API."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LocationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: str
    city: Optional[str] = None
    region: Optional[str] = None


class CareerPreferencesDoc(BaseModel):
    """Stored shape on users/{uid}.career_preferences."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    target_titles: list[str] = Field(default_factory=list)
    exclude_titles: list[str] = Field(default_factory=list)
    experience_levels: list[str] = Field(default_factory=list)
    years_experience: Optional[int] = None
    locations: list[LocationRecord] = Field(default_factory=list)
    exclude_locations: list[LocationRecord] = Field(default_factory=list)
    work_arrangements: list[str] = Field(default_factory=list)
    willing_to_relocate: Optional[bool] = None
    employment_types: list[str] = Field(default_factory=list)
    visa_sponsorship_required: Optional[bool] = None
    language: str = "en"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    company_size_buckets: list[str] = Field(default_factory=list)
    target_company_slugs: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    exclude_staffing_agencies: bool = True
    taxonomies_primary: list[str] = Field(default_factory=lambda: ["Technology", "Software"])


class CareerPreferencesPatch(BaseModel):
    """Partial PATCH — all fields optional; sent keys replace entire arrays."""

    model_config = ConfigDict(extra="forbid")

    target_titles: Optional[list[str]] = None
    exclude_titles: Optional[list[str]] = None
    experience_levels: Optional[list[str]] = None
    years_experience: Optional[int] = None
    locations: Optional[list[LocationRecord]] = None
    exclude_locations: Optional[list[LocationRecord]] = None
    work_arrangements: Optional[list[str]] = None
    willing_to_relocate: Optional[bool] = None
    employment_types: Optional[list[str]] = None
    visa_sponsorship_required: Optional[bool] = None
    language: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    company_size_buckets: Optional[list[str]] = None
    target_company_slugs: Optional[list[str]] = None
    target_industries: Optional[list[str]] = None
    exclude_staffing_agencies: Optional[bool] = None


class CompletenessMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_complete: bool
    missing: list[str] = Field(default_factory=list)
    message: str = ""


class CareerPreferencesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferences: CareerPreferencesDoc
    completeness: CompletenessMeta
