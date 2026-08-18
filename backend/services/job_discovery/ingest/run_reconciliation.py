"""Daily Job Discovery search-index reconciliation entrypoint."""
from __future__ import annotations

import asyncio

from services.job_discovery.search.reconciliation_service import run_reconciliation


async def main() -> None:
    await run_reconciliation()


if __name__ == "__main__":
    asyncio.run(main())

