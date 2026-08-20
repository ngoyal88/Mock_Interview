"""Neutral helpers for reading question text from session question blobs."""
from __future__ import annotations

import json
from typing import Dict, Union


def extract_question_text(q_entry: Union[str, Dict]) -> str:
    """Return human-readable question text from an entry that may be a string or dict."""
    if isinstance(q_entry, str):
        return q_entry
    if isinstance(q_entry, dict):
        q = q_entry.get("question") if "question" in q_entry else q_entry
        if isinstance(q, dict):
            return q.get("question") or q.get("title") or json.dumps(q)
        if isinstance(q, str):
            return q
    return str(q_entry)
