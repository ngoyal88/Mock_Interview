from __future__ import annotations

from typing import Any, Dict, Optional

from models.interview import InterviewType
from services.application_fit.extract.text import clean_optional_text
from services.application_fit.persist.repository import get_snapshot_for_user
from services.interview.modes.base import InterviewModeStrategy, ModeStartResult
from services.interview.catalog.start_request import ModeStartConfig, RoleTargetedStartConfig
from utils.logger import get_logger

logger = get_logger(__name__)


async def hydrate_role_targeted_start(
    uid: str,
    config: RoleTargetedStartConfig,
) -> tuple[RoleTargetedStartConfig, Optional[Dict[str, Any]]]:
    """Merge Application Fit snapshot fields into start config when snapshot id is set."""
    snapshot_id = (config.jd_fit_snapshot_id or "").strip() or None
    if not snapshot_id:
        return config, None

    snapshot_data = await get_snapshot_for_user(uid, snapshot_id)
    if not snapshot_data:
        logger.warning("jd_fit_snapshot_id not found for uid=%s id=%s", uid, snapshot_id)
        return config, None

    updates: Dict[str, Any] = {}
    if not (config.target_role or "").strip() and snapshot_data.get("target_role"):
        updates["target_role"] = clean_optional_text(str(snapshot_data["target_role"]), max_len=160)
    stored_jd = snapshot_data.get("job_description")
    if not (config.job_description or "").strip() and isinstance(stored_jd, str) and stored_jd.strip():
        updates["job_description"] = clean_optional_text(stored_jd, max_len=8000)
    stored_company = snapshot_data.get("target_company")
    if not (config.target_company or "").strip() and isinstance(stored_company, str) and stored_company.strip():
        updates["target_company"] = clean_optional_text(stored_company, max_len=120)

    if updates:
        config = config.model_copy(update=updates)
    return config, snapshot_data


class RoleTargetedModeStrategy(InterviewModeStrategy):
    mode = InterviewType.ROLE_TARGETED

    async def prepare_start(
        self,
        *,
        interview_service: Any,
        difficulty,
        resume_data: Dict[str, Any],
        years_experience: Optional[int],
        config: ModeStartConfig,
    ) -> ModeStartResult:
        if not isinstance(config, RoleTargetedStartConfig):
            raise TypeError("RoleTargetedModeStrategy requires RoleTargetedStartConfig")

        target_company = clean_optional_text(config.target_company, max_len=120)
        target_role = clean_optional_text(config.target_role, max_len=160)
        job_description = clean_optional_text(config.job_description, max_len=8000)
        interview_focus = config.interview_focus

        jd_fit_context = await interview_service.build_jd_fit_context(
            target_company=target_company,
            target_role=target_role or "",
            job_description=job_description or "",
            interview_focus=interview_focus,
            resume_data=resume_data,
            years_experience=years_experience,
        )
        target_context = {
            "target_company": target_company,
            "target_role": target_role,
            "job_description": job_description,
            "interview_focus": interview_focus,
            "jd_fit_context": jd_fit_context,
        }
        return ModeStartResult(
            target_context=target_context,
            jd_fit_context=jd_fit_context,
            resume_probe_context={},
            seeded_questions=[],
        )
