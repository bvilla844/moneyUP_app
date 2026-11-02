"""Domain layer: the core objects and rules of moneyUP.

Rule for this package: pure Python only. No database, no web, no file I/O.
"""

from moneyup.domain.category import Category, CategoryKind
from moneyup.domain.expense import Expense, total_spent

__all__ = ["Category", "CategoryKind", "Expense", "total_spent"]
