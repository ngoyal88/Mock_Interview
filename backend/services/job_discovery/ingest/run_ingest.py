"""Hourly Job Discovery ingest entrypoint."""
from __future__ import annotations

import asyncio

from services.job_discovery.ingest.ingest_service import run_expiry_sweep, run_incremental_ingest, run_staleness_sweep


async def main() -> None:
    await run_incremental_ingest(time_frame="1h")
    await run_expiry_sweep(time_frame="1h")
    await run_staleness_sweep()


if __name__ == "__main__":
    asyncio.run(main())

