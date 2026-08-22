"""Thin bridge from Job Discovery detail to Application Fit."""
from __future__ import annotations

from services.application_fit.persist.repository import annotate_snapshot_source
from services.application_fit.service import ApplicationFitService
from services.job_discovery import detail_service, discovery_settings_service


async def compute_fit_for_job(uid: str, job_id: str):
    job = await detail_service.get_job_detail(job_id, uid=uid)
    settings = await discovery_settings_service.get(uid)
    response = await ApplicationFitService().compute_fit(
        uid=uid,
        target_role=job.title,
        target_company=job.organization_name,
        job_description=job.description_text or "",
        resume_id=settings.default_fit_resume_id,
        first_seen=job.date_posted.isoformat() if job.date_posted else None,
    )
    await annotate_snapshot_source(
        uid,
        response.snapshot_id,
        source="job_discovery",
        source_job_id=job_id,
        source_job_title=job.title,
        source_company=job.organization_name,
    )
    return response

