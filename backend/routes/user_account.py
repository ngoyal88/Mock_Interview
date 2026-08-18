"""User account API — DELETE account purge."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from models.account import PurgeAccountRequest
from services.user.account.purge_service import purge_user_account
from utils.auth import verify_recent_firebase_token
from utils.http_errors import raise_service_error
from utils.logger import get_logger
from utils.rate_limit import check_rate_limit

router = APIRouter(prefix="/user", tags=["UserAccount"])
logger = get_logger("UserAccountRoutes")


@router.delete("/account")
async def delete_user_account(
    body: PurgeAccountRequest,
    uid: str = Depends(verify_recent_firebase_token),
) -> dict[str, str]:
    """Delete all user data and remove the Firebase Auth record."""
    if body.confirmation != "DELETE":
        raise HTTPException(status_code=403, detail="Confirmation required")

    try:
        await check_rate_limit(uid, "account_purge", limit=3, window_seconds=3600)
        return await purge_user_account(uid)
    except HTTPException:
        raise
    except Exception as exc:
        raise_service_error(
            logger,
            exc,
            message="Failed to purge account",
            log_event="Error purging account data",
        )
