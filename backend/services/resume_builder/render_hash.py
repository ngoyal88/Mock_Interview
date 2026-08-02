from __future__ import annotations

import hashlib
import json
from typing import Any

from services.resume_builder.medium_document import MediumReadyDocument
from services.resume_builder.style_spec import StyleSpec
from services.resume_builder.style_tokens import StyleTokens

RENDER_ENGINE_VERSION = "typst-1"


def canonical_render_payload(
    document: MediumReadyDocument,
    tokens: StyleTokens,
    *,
    template_id: str,
    template_version: str,
    style_spec: StyleSpec,
    template_fingerprint: str,
) -> dict[str, Any]:
    return {
        "document": document.model_dump(mode="json"),
        "tokens": tokens.model_dump(mode="json"),
        "template_id": template_id,
        "template_version": template_version,
        "template_fingerprint": template_fingerprint,
        "render_engine_version": RENDER_ENGINE_VERSION,
        "style_spec": style_spec.model_dump(mode="json"),
    }


def compute_render_input_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
