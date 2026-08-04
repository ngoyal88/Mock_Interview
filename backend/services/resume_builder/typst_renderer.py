from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from services.resume_builder.medium_document import MediumReadyDocument, build_medium_ready_document
from services.resume_builder.models import ResumeBuilderDraft
from services.resume_builder.render_hash import (
    RENDER_ENGINE_VERSION,
    canonical_render_payload,
    compute_render_input_hash,
)
from services.resume_builder.style_spec import StyleSpec, hydrate_style_spec
from services.resume_builder.style_tokens import StyleTokens, resolve_style_tokens
from services.resume_builder.template_catalog import get_template, templates_root

_template_fingerprint_cache: dict[str, str] = {}


def clear_template_fingerprint_cache() -> None:
    _template_fingerprint_cache.clear()


def _template_dir(template_id: str) -> Path:
    metadata = get_template(template_id)
    return templates_root() / metadata.id


def compute_template_fingerprint(template_id: str) -> str:
    cached = _template_fingerprint_cache.get(template_id)
    if cached is not None:
        return cached
    hasher = hashlib.sha256()
    hasher.update(RENDER_ENGINE_VERSION.encode("utf-8"))
    template_path = _template_dir(template_id) / "template.typ"
    hasher.update(template_path.read_bytes())
    fonts_dir = templates_root() / "_fonts"
    if fonts_dir.is_dir():
        for font_path in sorted(fonts_dir.rglob("*")):
            if font_path.is_file():
                rel = font_path.relative_to(fonts_dir).as_posix()
                hasher.update(rel.encode("utf-8"))
                hasher.update(font_path.read_bytes())
    digest = hasher.hexdigest()
    _template_fingerprint_cache[template_id] = digest
    return digest


def build_render_payload(draft: ResumeBuilderDraft) -> tuple[dict[str, Any], str]:
    style = hydrate_style_spec(getattr(draft, "style_spec", None))
    document = build_medium_ready_document(draft, style_spec=style)
    tokens = resolve_style_tokens(style, template_id=draft.template_id)
    template_fingerprint = compute_template_fingerprint(draft.template_id)
    payload = canonical_render_payload(
        document,
        tokens,
        template_id=draft.template_id,
        template_version=draft.template_version,
        style_spec=style,
        template_fingerprint=template_fingerprint,
    )
    return payload, compute_render_input_hash(payload)


def _read_template_source(template_id: str) -> str:
    template_path = _template_dir(template_id) / "template.typ"
    if not template_path.is_file():
        raise ValueError(f"template_typ_missing:{template_id}")
    return template_path.read_text(encoding="utf-8")


def build_typst_files(draft: ResumeBuilderDraft, payload: dict[str, Any]) -> dict[str, bytes | str]:
    template_source = _read_template_source(draft.template_id)
    files: dict[str, bytes | str] = {
        "template.typ": template_source.encode("utf-8"),
        "data.json": json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
    }
    fonts_dir = templates_root() / "_fonts"
    if fonts_dir.is_dir():
        for font_path in fonts_dir.rglob("*"):
            if font_path.is_file():
                rel = Path("_fonts") / font_path.relative_to(fonts_dir)
                files[str(rel).replace("\\", "/")] = font_path.read_bytes()
    return files


def build_typst_bundle_with_bytes(draft: ResumeBuilderDraft) -> tuple[dict[str, bytes | str], dict[str, Any], str]:
    payload, render_hash = build_render_payload(draft)
    files = build_typst_files(draft, payload)
    return files, payload, render_hash
