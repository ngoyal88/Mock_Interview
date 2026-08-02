from __future__ import annotations

import base64
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PyPDF2 import PdfReader

from config import get_settings


class CompileError(RuntimeError):
    pass


class CompileTimeoutError(TimeoutError):
    pass


def _resolve_typst_bin() -> str:
    settings = get_settings()
    configured = (settings.typst_bin or "typst").strip()
    if configured != "typst" and Path(configured).is_file():
        return configured
    if sys.platform == "win32":
        bundled = Path(__file__).resolve().parents[2] / "bin" / "typst.exe"
        if bundled.is_file():
            return str(bundled)
    return configured


def _compile_env() -> dict[str, str]:
    return os.environ.copy()


def _read_page_count(pdf_bytes: bytes) -> int:
    return len(PdfReader(io.BytesIO(pdf_bytes)).pages)


def compile_typst_to_pdf(
    files: dict[str, str | bytes],
    *,
    entry: str = "template.typ",
    timeout_s: int | None = None,
    max_pdf_bytes: int | None = None,
) -> tuple[bytes, int]:
    settings = get_settings()
    timeout = timeout_s or settings.resume_builder_compile_timeout_s
    max_bytes = max_pdf_bytes or settings.resume_builder_max_pdf_bytes
    typst_bin = _resolve_typst_bin()

    try:
        with tempfile.TemporaryDirectory(prefix="resume-builder-typst-") as workdir:
            work_path = Path(workdir)
            for rel_path, content in files.items():
                target = work_path / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, bytes):
                    target.write_bytes(content)
                else:
                    target.write_text(content, encoding="utf-8")

            pdf_path = work_path / "output.pdf"
            try:
                result = subprocess.run(
                    [typst_bin, "compile", entry, str(pdf_path)],
                    cwd=str(work_path),
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=_compile_env(),
                )
            except subprocess.TimeoutExpired as exc:
                raise CompileTimeoutError("compile_timeout") from exc
            if result.returncode != 0:
                raise CompileError(result.stderr.strip() or result.stdout.strip() or "compile_failed")

            if not pdf_path.exists():
                raise CompileError("compile_failed")
            pdf_bytes = pdf_path.read_bytes()
            if len(pdf_bytes) > max_bytes:
                raise CompileError("pdf_too_large")
            return pdf_bytes, _read_page_count(pdf_bytes)
    except (CompileError, CompileTimeoutError):
        raise
    except FileNotFoundError as exc:
        raise CompileError("typst_not_found") from exc


def compile_typst_bundle_b64(
    files_b64: dict[str, str],
    *,
    entry: str = "template.typ",
    timeout_s: int | None = None,
    max_pdf_bytes: int | None = None,
) -> tuple[bytes, int]:
    decoded: dict[str, bytes] = {}
    for name, payload in files_b64.items():
        decoded[name] = base64.b64decode(payload.encode("ascii"))
    return compile_typst_to_pdf(decoded, entry=entry, timeout_s=timeout_s, max_pdf_bytes=max_pdf_bytes)

