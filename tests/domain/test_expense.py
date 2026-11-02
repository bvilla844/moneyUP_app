from datetime import date
from decimal import Decimal

import pytest

from moneyup.domain import Category, CategoryKind, Expense, total_spent

FOOD = Category("Food", CategoryKind.EXPENSE)
TRANSPORT = Category("Transport", CategoryKind.EXPENSE)
TODAY = date(2026, 11, 2)


def test_create_expense():
    expense = Expense(Decimal("45.90"), FOOD, TODAY, note="Groceries")

    assert expense.amount == Decimal("45.90")
    assert expense.category == FOOD
    assert expense.note == "Groceries"


def test_float_amount_is_rejected():
    with pytest.raises(TypeError):
        Expense(45.90, FOOD, TODAY)


@pytest.mark.parametrize("amount", ["0", "-10.00"])
def test_amount_must_be_positive(amount):
    with pytest.raises(ValueError):
        Expense(Decimal(amount), FOOD, TODAY)


def test_more_than_two_decimals_is_rejected():
    with pytest.raises(ValueError):
        Expense(Decimal("10.999"), FOOD, TODAY)


@pytest.mark.parametrize(
    "category",
    [
        Category("Emergency fund", CategoryKind.SAVING),
        Category("Salary", CategoryKind.INCOME),
    ],
)
def test_category_must_be_an_expense_category(category):
    with pytest.raises(ValueError):
        Expense(Decimal("100.00"), category, TODAY)


def test_total_spent_adds_all_expenses():
    expenses = [
        Expense(Decimal("0.10"), FOOD, TODAY),
        Expense(Decimal("0.20"), FOOD, TODAY),
        Expense(Decimal("5.00"), TRANSPORT, TODAY),
    ]
    # With floats, 0.10 + 0.20 would be 0.30000000000000004
    assert total_spent(expenses) == Decimal("5.30")


def test_total_spent_by_category():
    expenses = [
        Expense(Decimal("20.00"), FOOD, TODAY),
        Expense(Decimal("15.50"), FOOD, TODAY),
        Expense(Decimal("5.00"), TRANSPORT, TODAY),
    ]
    assert total_spent(expenses, FOOD) == Decimal("35.50")
    assert total_spent(expenses, TRANSPORT) == Decimal("5.00")


def test_total_spent_with_no_expenses_is_zero():
    assert total_spent([]) == Decimal("0")
