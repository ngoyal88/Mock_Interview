"""Credit budget guard for Fantastic.jobs backfills."""
from __future__ import annotations

from dataclasses import dataclass


class CreditBudgetExceeded(Exception):
    def __init__(self, credits_consumed: int) -> None:
        super().__init__("Job Discovery credit budget exceeded")
        self.credits_consumed = credits_consumed


@dataclass
class CreditBudget:
    limit: int
    consumed: int = 0

    def reserve_page(self, credits_used_this_page: int) -> None:
        if self.consumed + max(0, credits_used_this_page) > self.limit:
            raise CreditBudgetExceeded(self.consumed)
        self.consumed += max(0, credits_used_this_page)


def check_budget(consumed: int, credits_used_this_page: int, budget: int) -> None:
    if consumed + max(0, credits_used_this_page) > budget:
        raise CreditBudgetExceeded(consumed)

