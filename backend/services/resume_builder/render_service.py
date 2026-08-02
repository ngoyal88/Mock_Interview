from __future__ import annotations

import base64
from collections import OrderedDict
from typing import Any

from services.resume_builder.compile_client import compile_typst_bundle
from services.resume_builder.models import ResumeBuilderDraft
from services.resume_builder.typst_renderer import build_render_payload, build_typst_files

_RENDER_CACHE_MAX = 32
_render_cache: OrderedDict[str, tuple[bytes, int]] = OrderedDict()


def clear_render_cache() -> None:
    _render_cache.clear()


def _cache_put(render_hash: str, pdf_bytes: bytes, page_count: int) -> None:
    _render_cache[render_hash] = (pdf_bytes, page_count)
    _render_cache.move_to_end(render_hash)
    while len(_render_cache) > _RENDER_CACHE_MAX:
        _render_cache.popitem(last=False)


async def render_draft_pdf(
    draft: ResumeBuilderDraft,
    *,
    use_cache: bool = True,
) -> tuple[bytes, int, str, dict[str, Any]]:
    payload, render_hash = build_render_payload(draft)
    if use_cache and render_hash in _render_cache:
        _render_cache.move_to_end(render_hash)
        pdf_bytes, page_count = _render_cache[render_hash]
        return pdf_bytes, page_count, render_hash, payload

    files = build_typst_files(draft, payload)
    encoded_files = {
        name: base64.b64encode(content if isinstance(content, bytes) else content.encode("utf-8")).decode("ascii")
        for name, content in files.items()
    }
    pdf_bytes, page_count = await compile_typst_bundle(encoded_files)
    if use_cache:
        _cache_put(render_hash, pdf_bytes, page_count)
    return pdf_bytes, page_count, render_hash, payload
