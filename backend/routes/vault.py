from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from routes.vault_validators import (
    MAX_RESUME_SIZE_BYTES,
    allowed_file,
    clean_optional_string,
    clean_required_string,
    normalize_tags_or_400,
    parse_entry_update_payload,
)
from services.vault.vault_analyze_service import analyze_vault_version
from services.vault.vault_compare_flow_service import compare_vault_versions
from services.vault.vault_file_download_service import load_version_file_bytes
from services.vault.vault_upload_service import upload_resume_to_vault
from services.vault import (
    delete_resume_entry,
    get_vault_entry,
    get_vault_meta,
    get_version_by_id,
    list_vault_entries,
    list_versions,
    restore_version,
    set_active_resume,
    update_entry,
)
from utils.auth import verify_firebase_token
from utils.domain_errors import DomainError
from utils.domain_error_registry import resolve_value_error_code
from utils.http_errors import raise_service_error
from utils.logger import get_logger
from utils.rate_limit import check_rate_limit

router = APIRouter(tags=["Vault"])
logger = get_logger(__name__)


@router.get("/vault")
async def list_vault(uid: str = Depends(verify_firebase_token)):
    meta = await get_vault_meta(uid)
    entries = await list_vault_entries(uid)
    return {"entries": entries, "meta": meta}


@router.post("/vault/upload")
async def upload_to_vault(
    file: UploadFile = File(...),
    name: str = Form(...),
    tags: str | None = Form(None),
    resume_id: str | None = Form(None),
    user_note: str | None = Form(None),
    role: str | None = Form(None),
    uid: str = Depends(verify_firebase_token),
):
    await check_rate_limit(uid, "vault_upload", limit=10, window_seconds=60)
    if not allowed_file(file.filename, file.content_type):
        raise HTTPException(400, "Unsupported file type. Allowed: PDF, DOCX, TXT.")
    try:
        return await upload_resume_to_vault(
            uid=uid,
            file=file,
            name=clean_required_string(name, "name"),
            tags_list=normalize_tags_or_400(
                tags,
                allow_string=True,
                error_message="tags must be a comma-separated string or JSON array of strings",
            ),
            resume_id=clean_optional_string(resume_id, "resume_id"),
            user_note=(user_note or "").strip(),
            role=clean_optional_string(role, "role"),
            max_size_bytes=MAX_RESUME_SIZE_BYTES,
        )
    except DomainError:
        raise
    except Exception as exc:
        raise_service_error(
            logger,
            exc,
            message="Resume upload failed. Please try again.",
            log_event=f"Vault upload failed uid={uid}",
        )


@router.get("/vault/{resume_id}")
async def get_vault_item(resume_id: str, uid: str = Depends(verify_firebase_token)):
    entry = await get_vault_entry(uid, resume_id)
    if not entry:
        raise HTTPException(404, "Resume entry not found")
    return entry


@router.patch("/vault/{resume_id}")
async def update_vault_item(
    resume_id: str,
    payload: Dict[str, Any],
    uid: str = Depends(verify_firebase_token),
):
    if not isinstance(payload, dict):
        raise HTTPException(400, "Invalid request body")
    name, tags = parse_entry_update_payload(payload)
    try:
        return await update_entry(uid, resume_id, name, tags)
    except ValueError as exc:
        raise resolve_value_error_code(str(exc), context="update") from exc


@router.delete("/vault/{resume_id}")
async def delete_vault_item(resume_id: str, uid: str = Depends(verify_firebase_token)):
    entry = await get_vault_entry(uid, resume_id)
    if not entry:
        raise HTTPException(404, "Resume entry not found")
    await delete_resume_entry(uid, resume_id)
    meta = await get_vault_meta(uid)
    return {
        "status": "deleted",
        "active_resume_id": meta.get("active_resume_id"),
        "resume_count": meta.get("resume_count", 0),
    }


@router.put("/vault/{resume_id}/set-active")
async def set_active(resume_id: str, uid: str = Depends(verify_firebase_token)):
    entry = await get_vault_entry(uid, resume_id)
    if not entry:
        raise HTTPException(404, "Resume entry not found")
    await set_active_resume(uid, resume_id)
    return {"status": "ok"}


@router.get("/versions")
async def get_versions(resume_id: str, uid: str = Depends(verify_firebase_token)):
    if not resume_id:
        raise HTTPException(400, "resume_id is required")
    entry = await get_vault_entry(uid, resume_id)
    if not entry:
        raise HTTPException(404, "Resume entry not found")
    versions = await list_versions(uid, resume_id)
    return {"versions": versions}


@router.get("/versions/{version_id}")
async def get_version(version_id: str, uid: str = Depends(verify_firebase_token)):
    version = await get_version_by_id(uid, version_id)
    if not version:
        raise HTTPException(404, "Version not found")
    return version


@router.get("/vault/files/{version_id}")
async def download_version_file(version_id: str, uid: str = Depends(verify_firebase_token)):
    await check_rate_limit(uid, "vault_file", limit=120, window_seconds=60)
    try:
        blob, media_type, source_filename = await load_version_file_bytes(uid, version_id)
    except FileNotFoundError:
        raise HTTPException(404, "Stored file not found") from None

    headers = {}
    if source_filename:
        safe_filename = source_filename.replace('"', "").replace("\r", "").replace("\n", "")
        headers["Content-Disposition"] = f'inline; filename="{safe_filename}"'
    return Response(content=blob, media_type=media_type, headers=headers)


@router.post("/restore/{version_id}")
async def restore(version_id: str, payload: Dict[str, Any], uid: str = Depends(verify_firebase_token)):
    await check_rate_limit(uid, "vault_restore", limit=30, window_seconds=60)
    if not isinstance(payload, dict):
        raise HTTPException(400, "Invalid request body")
    try:
        return await restore_version(uid, version_id, role=clean_optional_string(payload.get("role"), "role"))
    except ValueError as exc:
        logger.warning("Vault restore rejected for uid=%s version_id=%s error=%s", uid, version_id, exc)
        raise resolve_value_error_code(str(exc), context="restore") from exc
    except Exception as exc:
        logger.exception("Vault restore failed for uid=%s version_id=%s", uid, version_id)
        raise HTTPException(500, "Resume restore failed. Please try again.") from exc


@router.post("/analyze")
async def analyze(payload: Dict[str, Any], uid: str = Depends(verify_firebase_token)):
    await check_rate_limit(uid, "vault_analyze", limit=20, window_seconds=60)
    if not isinstance(payload, dict):
        raise HTTPException(400, "Invalid request body")
    try:
        return await analyze_vault_version(
            uid,
            resume_id=clean_required_string(payload.get("resume_id"), "resume_id"),
            version_id=clean_optional_string(payload.get("version_id"), "version_id"),
            role=clean_optional_string(payload.get("role"), "role"),
        )
    except DomainError:
        raise
    except Exception as exc:
        logger.exception("Vault analyze failed for uid=%s", uid)
        raise HTTPException(500, "Resume analysis failed. Please try again.") from exc


@router.post("/compare")
async def compare(payload: Dict[str, Any], uid: str = Depends(verify_firebase_token)):
    await check_rate_limit(uid, "vault_compare", limit=10, window_seconds=60)
    if not isinstance(payload, dict):
        raise HTTPException(400, "Invalid request body")
    try:
        return await compare_vault_versions(
            uid,
            resume_a_id=clean_required_string(payload.get("resume_a_id"), "resume_a_id"),
            resume_b_id=clean_required_string(payload.get("resume_b_id"), "resume_b_id"),
            version_a_id=clean_optional_string(payload.get("version_a_id"), "version_a_id"),
            version_b_id=clean_optional_string(payload.get("version_b_id"), "version_b_id"),
            role=clean_optional_string(payload.get("role"), "role"),
        )
    except DomainError:
        raise
    except Exception as exc:
        logger.exception("Vault compare failed for uid=%s", uid)
        raise HTTPException(500, "Resume comparison failed. Please try again.") from exc
