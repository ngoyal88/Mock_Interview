"""Career preferences API — GET/PATCH users/{uid}.career_preferences."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from services.user.career_preferences.models import CareerPreferencesPatch, CareerPreferencesResponse
from services.user.career_preferences.service import get_preferences, patch_preferences
from utils.auth import verify_firebase_token
from utils.rate_limit import check_rate_limit

router = APIRouter(prefix="/career-preferences", tags=["CareerPreferences"])


@router.get("", response_model=CareerPreferencesResponse)
async def career_preferences_get(uid: str = Depends(verify_firebase_token)) -> CareerPreferencesResponse:
    await check_rate_limit(uid, "career_preferences_read", limit=120, window_seconds=60)
    return await get_preferences(uid)


@router.patch("", response_model=CareerPreferencesResponse)
async def career_preferences_patch(
    body: CareerPreferencesPatch,
    uid: str = Depends(verify_firebase_token),
) -> CareerPreferencesResponse:
    await check_rate_limit(uid, "career_preferences_write", limit=30, window_seconds=60)
    return await patch_preferences(uid, body)
