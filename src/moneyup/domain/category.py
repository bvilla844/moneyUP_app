from dataclasses import dataclass
from enum import StrEnum


class CategoryKind(StrEnum):
    """What a category is used for.

    StrEnum members behave like strings (CategoryKind.EXPENSE == "expense"),
    which makes them easy to save in a database later.
    """

    INCOME = "income"  # money you receive: salary, freelance, gifts...
    EXPENSE = "expense"  # money you spend: food, rent, transport...
    SAVING = "saving"  # money you put aside: emergency fund, vacation...
    DEBT = "debt"  # money that goes to paying debts


@dataclass(frozen=True)
class Category:
    """A bucket where part of your income goes.

    frozen=True makes the object immutable: once created, it can't be changed.
    That prevents bugs where some code changes a category by accident.
    """

    name: str
    kind: CategoryKind

    def __post_init__(self) -> None:
        # __post_init__ runs right after the dataclass __init__.
        # It's the place to validate the data.
        cleaned = self.name.strip()
        if not cleaned:
            raise ValueError("Category name cannot be empty")
        # On a frozen dataclass you can't do self.name = ..., so we use
        # object.__setattr__ to store the cleaned-up name.
        object.__setattr__(self, "name", cleaned)
