"""Daily demand snapshot for Job Discovery segmented ingest."""
from __future__ import annotations

import asyncio

from services.job_discovery.ingest.demand_scope import store_demand_snapshot
from services.job_discovery.ingest.role_family_taxonomy import classify_titles_to_families
from services.user.career_preferences.aggregate import compute_demand_snapshot
from utils.logger import get_logger

logger = get_logger(__name__)


async def main() -> None:
    snapshot = await compute_demand_snapshot(role_family_matcher=classify_titles_to_families)
    await store_demand_snapshot(snapshot)
    logger.info(
        "Job Discovery demand snapshot stored sample_size=%s segments=%s unmapped=%s",
        snapshot.sample_size,
        len(snapshot.segment_weights),
        len(snapshot.unmapped_title_samples),
    )


if __name__ == "__main__":
    asyncio.run(main())
