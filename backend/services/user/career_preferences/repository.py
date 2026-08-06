"""Firestore I/O for users/{uid}.career_preferences."""
from __future__ import annotations

import asyncio
from typing import Any, Optional

from firebase_admin import firestore

from firebase_config import db


def _user_ref(uid: str):
    return db.collection("users").document(uid)


def _read_preferences_sync(uid: str) -> Optional[dict[str, Any]]:
    snap = _user_ref(uid).get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    raw = data.get("career_preferences")
    return raw if isinstance(raw, dict) else None


def _write_preferences_sync(uid: str, preferences: dict[str, Any]) -> None:
    _user_ref(uid).set(
        {
            "career_preferences": preferences,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


async def read_preferences_raw(uid: str) -> Optional[dict[str, Any]]:
    return await asyncio.to_thread(_read_preferences_sync, uid)


async def write_preferences(uid: str, preferences: dict[str, Any]) -> None:
    await asyncio.to_thread(_write_preferences_sync, uid, preferences)
