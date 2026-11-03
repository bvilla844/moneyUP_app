from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from moneyup.domain.category import Category, CategoryKind


@dataclass(frozen=True)
class Income:
    """Money you received: salary, freelance work, gifts..."""

    amount: Decimal
    category: Category
    received_on: date
    note: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError(
                f"amount must be a Decimal, got {type(self.amount).__name__}"
            )
        if self.amount <= 0:
            raise ValueError("Income amount must be greater than zero")
        if self.amount != self.amount.quantize(Decimal("0.01")):
            raise ValueError("Income amount cannot have more than 2 decimals")
        if self.category.kind is not CategoryKind.INCOME:
            raise ValueError(
                f"Category '{self.category.name}' is a {self.category.kind} "
                "category, not an income category"
            )


# Module-level function (not indented inside the class), like total_spent.
def total_received(
    incomes: Iterable[Income],
    start: date | None = None,
    end: date | None = None,
    category: Category | None = None,
) -> Decimal:
    """Add up incomes received between start and end (both included).

    Leave start/end as None for no limit on that side. If a category is
    given, only count incomes from that category.
    """
    if start is not None and end is not None and start > end:
        raise ValueError("start date must be before or equal to end date")

    return sum(
        (
            income.amount
            for income in incomes
            if (start is None or income.received_on >= start)
            and (end is None or income.received_on <= end)
            and (category is None or income.category == category)
        ),
        start=Decimal("0"),
    )
