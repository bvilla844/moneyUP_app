from datetime import date
from decimal import Decimal

import pytest

from moneyup.domain import Category, CategoryKind, Income, total_received

SALARY = Category("Salary", CategoryKind.INCOME)
FREELANCE = Category("Freelance", CategoryKind.INCOME)
TODAY = date(2026, 11, 2)


def test_create_income():
    income = Income(Decimal("3500000.55"), SALARY, TODAY, note="job payment")

    assert income.amount == Decimal("3500000.55")
    assert income.category == SALARY
    assert income.received_on == TODAY
    assert income.note == "job payment"


def test_float_amount_is_rejected():
    with pytest.raises(TypeError):
        Income(45.44, SALARY, TODAY)


@pytest.mark.parametrize("amount", ["0", "-10.00"])
def test_amount_must_be_positive(amount):
    with pytest.raises(ValueError, match="greater than zero"):
        Income(Decimal(amount), SALARY, TODAY)


def test_more_than_two_decimals_is_rejected():
    with pytest.raises(ValueError, match="2 decimals"):
        Income(Decimal("10.999"), SALARY, TODAY)


@pytest.mark.parametrize("kind", [CategoryKind.EXPENSE, CategoryKind.SAVING, CategoryKind.DEBT])
def test_category_must_be_an_income_category(kind):
    with pytest.raises(ValueError, match="not an income category"):
        Income(Decimal("100.00"), Category("Food", kind), TODAY)


# --- total_received ---------------------------------------------------------

INCOMES = [
    Income(Decimal("1000.00"), SALARY, date(2026, 10, 15)),
    Income(Decimal("1000.00"), SALARY, date(2026, 10, 30)),
    Income(Decimal("1000.00"), SALARY, date(2026, 11, 15)),
    Income(Decimal("250.50"), FREELANCE, date(2026, 11, 20)),
]


def test_total_received_without_filters_adds_everything():
    assert total_received(INCOMES) == Decimal("3250.50")


def test_total_received_in_a_month():
    november = total_received(INCOMES, date(2026, 11, 1), date(2026, 11, 30))
    assert november == Decimal("1250.50")


def test_start_and_end_dates_are_included():
    # Both incomes are exactly on the limits, so both must count.
    total = total_received(INCOMES, date(2026, 10, 15), date(2026, 10, 30))
    assert total == Decimal("2000.00")


def test_total_received_by_category_and_period():
    total = total_received(
        INCOMES, date(2026, 11, 1), date(2026, 11, 30), category=SALARY
    )
    assert total == Decimal("1000.00")


def test_total_received_with_no_incomes_is_zero():
    assert total_received([]) == Decimal("0")


def test_start_after_end_is_rejected():
    with pytest.raises(ValueError):
        total_received(INCOMES, date(2026, 12, 1), date(2026, 11, 1))
