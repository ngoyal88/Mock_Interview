"""One-off Job Discovery backfill entrypoint."""
from __future__ import annotations

import argparse
import asyncio

from config import get_settings
from services.job_discovery.ingest.ingest_service import run_backfill_ingest


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-frame", default="7d")
    parser.add_argument("--geography", default="India")
    parser.add_argument("--credit-budget", type=int, default=get_settings().job_discovery_credit_budget)
    args = parser.parse_args()
    params = {"location": args.geography} if args.geography else {}
    await run_backfill_ingest(
        time_frame=args.time_frame,
        credit_budget=args.credit_budget,
        **params,
    )


if __name__ == "__main__":
    asyncio.run(main())

