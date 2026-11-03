"""Domain layer: the core objects and rules of moneyUP.

Rule for this package: pure Python only. No database, no web, no file I/O.
"""

from moneyup.domain.category import Category, CategoryKind
from moneyup.domain.debt import (
    Debt,
    DebtPayment,
    is_paid_off,
    remaining_balance,
    remaining_installments,
    total_paid,
)
from moneyup.domain.expense import Expense, total_spent
from moneyup.domain.income import Income, total_received
from moneyup.domain.saving import (
    Saving,
    SavingDeposit,
    is_goal_reached,
    progress_percent,
    remaining_to_goal,
    total_saved,
)

# Note: debt.py and saving.py both have a remaining_installments function.
# Only the debt one is exported here; import the saving one directly from
# moneyup.domain.saving.
__all__ = [
    "Category",
    "CategoryKind",
    "Debt",
    "DebtPayment",
    "Expense",
    "Income",
    "Saving",
    "SavingDeposit",
    "is_goal_reached",
    "is_paid_off",
    "progress_percent",
    "remaining_balance",
    "remaining_installments",
    "remaining_to_goal",
    "total_paid",
    "total_received",
    "total_saved",
    "total_spent",
]
