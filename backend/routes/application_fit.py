"""Application Fit API routes."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, UploadFile

from services.application_fit.models import (
    ComputeRequest,
    ComputeResponse,
    ExtractJdTextResponse,
    HistoryResponse,
)
from services.application_fit.service import ApplicationFitService
from services.application_fit.extract.text import JD_EXTRACT_MAX_BYTES, extract_jd_text_from_bytes
from utils.auth import verify_firebase_token
from utils.rate_limit import check_rate_limit

router = APIRouter(prefix="/application-fit", tags=["ApplicationFit"])
_service = ApplicationFitService()


@router.post("/compute", response_model=ComputeResponse)
async def application_fit_compute(
    request: ComputeRequest,
    uid: str = Depends(verify_firebase_token),
) -> ComputeResponse:
    await check_rate_limit(uid, "application_fit_compute", limit=30, window_seconds=3600)
    return await _service.compute_fit(
        uid=uid,
        target_role=request.target_role,
        target_company=request.target_company,
        job_description=request.job_description,
        resume_id=request.resume_id,
        version_id=request.version_id,
        first_seen=request.first_seen,
    )


@router.get("/history", response_model=HistoryResponse)
async def application_fit_history(
    target_role: str,
    job_description: str = "",
    limit: int = 20,
    uid: str = Depends(verify_firebase_token),
) -> HistoryResponse:
    await check_rate_limit(uid, "application_fit_history", limit=120, window_seconds=60)
    return await _service.get_history(
        uid=uid,
        target_role=target_role,
        job_description=job_description,
        limit=limit,
    )


@router.get("/snapshots/{snapshot_id}", response_model=ComputeResponse)
async def application_fit_get_snapshot(
    snapshot_id: str,
    uid: str = Depends(verify_firebase_token),
) -> ComputeResponse:
    await check_rate_limit(uid, "application_fit_history", limit=120, window_seconds=60)
    return await _service.get_snapshot_response(uid, snapshot_id)


@router.post("/extract-text", response_model=ExtractJdTextResponse)
async def application_fit_extract_text(
    file: UploadFile = File(...),
    uid: str = Depends(verify_firebase_token),
) -> ExtractJdTextResponse:
    await check_rate_limit(uid, "application_fit_extract_text", limit=60, window_seconds=3600)

    blob = await file.read(JD_EXTRACT_MAX_BYTES + 1)
    text, warnings = await asyncio.to_thread(
        extract_jd_text_from_bytes,
        blob,
        file.filename or "jd.txt",
    )
    return ExtractJdTextResponse(text=text, char_count=len(text), warnings=warnings)
