"""Shared money helpers used by every domain model."""

from decimal import Decimal

CENT = Decimal("0.01")


def check_money(value: object, field: str) -> None:
    """Validate a money value: Decimal, positive, max 2 decimals."""
    if not isinstance(value, Decimal):
        raise TypeError(f"{field} must be a Decimal, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{field} must be greater than zero")
    if value != value.quantize(CENT):
        raise ValueError(f"{field} cannot have more than 2 decimals")


def check_positive_int(value: object, field: str) -> None:
    """Validate a count: int (not bool), greater than zero."""
    # bool is a subclass of int in Python (True == 1), so exclude it.
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{field} must be an int, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{field} must be greater than zero")
