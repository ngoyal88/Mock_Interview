from __future__ import annotations

import asyncio
import secrets
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from config import get_settings
from services.resume_builder.compile_runner import (
    CompileError,
    CompileTimeoutError,
    compile_typst_bundle_b64,
)
from utils.logger import get_logger

log = get_logger(__name__)
settings = get_settings()

MAX_COMPILE_FILES = 64
MAX_COMPILE_B64_BYTES = 8_388_608  # ~6 MiB decoded PDF bundle budget

app = FastAPI(title="Vetta Resume Builder Compile Service", version="2.0.0")


class CompileTypstRequest(BaseModel):
    files: dict[str, str] = Field(min_length=1)
    entry: str = "template.typ"
    timeout_s: int | None = Field(default=None, ge=1, le=60)
    max_pdf_bytes: int | None = Field(default=None, ge=1_024, le=10_485_760)


def _verify_internal_token(token: str | None) -> None:
    expected = (settings.compile_service_token or "").strip()
    provided = (token or "").strip()
    if not expected or not secrets.compare_digest(expected, provided):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
async def health() -> dict[str, object]:
    from services.resume_builder.compile_runner import _resolve_typst_bin
    import shutil

    typst_bin = _resolve_typst_bin()
    typst_ok = shutil.which(typst_bin) is not None or Path(typst_bin).is_file()
    return {
        "status": "ok" if typst_ok else "degraded",
        "engine": "typst",
        "typst_bin": typst_bin,
        "typst_available": typst_ok,
        "token_configured": bool((settings.compile_service_token or "").strip()),
    }


@app.post("/internal/compile")
async def compile_resume(
    request: CompileTypstRequest,
    x_internal_token: str | None = Header(default=None),
) -> Response:
    _verify_internal_token(x_internal_token)
    if len(request.files) > MAX_COMPILE_FILES:
        raise HTTPException(status_code=413, detail="compile_bundle_too_many_files")
    total_b64 = sum(len(content) for content in request.files.values())
    if total_b64 > MAX_COMPILE_B64_BYTES:
        raise HTTPException(status_code=413, detail="compile_bundle_too_large")
    try:
        pdf_bytes, page_count = await asyncio.to_thread(
            compile_typst_bundle_b64,
            request.files,
            entry=request.entry,
            timeout_s=request.timeout_s,
            max_pdf_bytes=request.max_pdf_bytes,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"X-Page-Count": str(page_count)},
        )
    except CompileTimeoutError:
        raise HTTPException(status_code=504, detail="compile_timeout") from None
    except CompileError as exc:
        log.warning("Resume compile failed: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        log.error("Unexpected compile failure", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "compile_unavailable"})
