from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from moneyup.domain.category import Category, CategoryKind


@dataclass(frozen=True)
class Expense:
    """Money you spent on something."""

    amount: Decimal
    category: Category
    spent_on: date
    note: str = ""

    def __post_init__(self) -> None:
        # Floats can't represent money exactly (0.1 + 0.2 != 0.3), so we
        # refuse them. Use Decimal("12.50") instead of 12.50.
        if not isinstance(self.amount, Decimal):
            raise TypeError(
                f"amount must be a Decimal, got {type(self.amount).__name__}"
            )
        if self.amount <= 0:
            raise ValueError("Expense amount must be greater than zero")
        if self.amount != self.amount.quantize(Decimal("0.01")):
            raise ValueError("Expense amount cannot have more than 2 decimals")
        if self.category.kind is not CategoryKind.EXPENSE:
            raise ValueError(
                f"Category '{self.category.name}' is a {self.category.kind} "
                "category, not an expense category"
            )


def total_spent(
    expenses: Iterable[Expense], category: Category | None = None
) -> Decimal:
    """Add up expenses. If a category is given, only count that category."""
    return sum(
        (e.amount for e in expenses if category is None or e.category == category),
        start=Decimal("0"),
    )
