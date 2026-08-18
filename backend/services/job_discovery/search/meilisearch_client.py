"""Thin sync-SDK wrapper for Meilisearch."""
from __future__ import annotations

from typing import Any

from config import get_settings
from services.job_discovery.constants import (
    FILTERABLE_ATTRIBUTES,
    INDEX_NAME,
    RANKING_RULES,
    SEARCHABLE_ATTRIBUTES,
    SORTABLE_ATTRIBUTES,
)
from utils.async_io import run_in_thread

try:
    import meilisearch
    from meilisearch.errors import MeilisearchCommunicationError, MeilisearchTimeoutError
except Exception:  # pragma: no cover - exercised only when dependency is absent locally
    meilisearch = None

    class MeilisearchCommunicationError(Exception):
        pass

    class MeilisearchTimeoutError(Exception):
        pass


def meili_unavailable_errors() -> tuple[type[BaseException], ...]:
    return (MeilisearchCommunicationError, MeilisearchTimeoutError, TimeoutError, ConnectionError)


def get_client() -> Any:
    if meilisearch is None:
        raise MeilisearchCommunicationError("meilisearch package is not installed")
    settings = get_settings()
    return meilisearch.Client(settings.meilisearch_url, settings.meilisearch_master_key or None)


def get_index() -> Any:
    return get_client().index(INDEX_NAME)


async def ensure_index() -> None:
    def _ensure() -> None:
        client = get_client()
        try:
            client.create_index(INDEX_NAME, {"primaryKey": "id"})
        except Exception:
            pass
        index = client.index(INDEX_NAME)
        index.update_searchable_attributes(SEARCHABLE_ATTRIBUTES)
        index.update_filterable_attributes(FILTERABLE_ATTRIBUTES)
        index.update_sortable_attributes(SORTABLE_ATTRIBUTES)
        index.update_ranking_rules(RANKING_RULES)

    await run_in_thread(_ensure)


async def search(*, query: str, filter: str, sort: list[str], offset: int, limit: int) -> dict[str, Any]:
    def _search() -> dict[str, Any]:
        return get_index().search(query, {"filter": filter, "sort": sort, "offset": offset, "limit": limit})

    return await run_in_thread(_search)


async def add_documents(documents: list[dict[str, Any]]) -> None:
    if not documents:
        return
    await run_in_thread(lambda: get_index().add_documents(documents, primary_key="id"))


async def delete_documents(ids: list[str]) -> None:
    if not ids:
        return
    await run_in_thread(lambda: get_index().delete_documents(ids))


async def list_all_ids(*, page_size: int = 1000) -> set[str]:
    def _list() -> set[str]:
        index = get_index()
        ids: set[str] = set()
        offset = 0
        while True:
            result = index.get_documents({"fields": ["id"], "limit": page_size, "offset": offset})
            results = getattr(result, "results", result.get("results") if isinstance(result, dict) else [])
            batch = []
            for item in results:
                item_id = item.get("id") if isinstance(item, dict) else getattr(item, "id", None)
                if item_id:
                    batch.append(str(item_id))
            ids.update(batch)
            if len(batch) < page_size:
                break
            offset += page_size
        return ids

    return await run_in_thread(_list)

