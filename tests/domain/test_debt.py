from datetime import date
from decimal import Decimal

import pytest

from moneyup.domain import (
    Category,
    CategoryKind,
    Debt,
    DebtPayment,
    is_paid_off,
    remaining_balance,
    remaining_installments,
    total_paid,
)

LOANS = Category("Loans", CategoryKind.DEBT)
START = date(2026, 1, 1)


def make_debt(**changes) -> Debt:
    """Build a valid debt; pass keyword arguments to change any field."""
    fields = dict(
        name="Motorcycle loan",
        original_amount=Decimal("1000.00"),
        category=LOANS,
        start_date=START,
        installment_count=12,
        installment_payment=Decimal("100.00"),
    )
    fields.update(changes)
    return Debt(**fields)


def pay(debt: Debt, amount: str, paid_on: date = date(2026, 2, 1)) -> DebtPayment:
    return DebtPayment(debt, Decimal(amount), paid_on)


# --- Debt -------------------------------------------------------------------


def test_create_debt():
    debt = make_debt(note="Bank X")

    assert debt.name == "Motorcycle loan"
    assert debt.original_amount == Decimal("1000.00")
    assert debt.installment_count == 12
    assert debt.note == "Bank X"


def test_total_to_pay_and_interest_cost():
    debt = make_debt()  # 12 x 100 = 1200 to pay back 1000

    assert debt.total_to_pay == Decimal("1200.00")
    assert debt.interest_cost == Decimal("200.00")


def test_debt_without_interest():
    debt = make_debt(installment_count=10)  # 10 x 100 = 1000

    assert debt.interest_cost == Decimal("0")


def test_name_is_trimmed():
    assert make_debt(name="  Credit card ").name == "Credit card"


def test_empty_name_is_rejected():
    with pytest.raises(ValueError, match="name cannot be empty"):
        make_debt(name="   ")


@pytest.mark.parametrize("field", ["original_amount", "installment_payment"])
def test_money_fields_reject_floats(field):
    with pytest.raises(TypeError, match=f"{field} must be a Decimal"):
        make_debt(**{field: 100.0})


@pytest.mark.parametrize("field", ["original_amount", "installment_payment"])
@pytest.mark.parametrize("value", ["0", "-5.00"])
def test_money_fields_must_be_positive(field, value):
    with pytest.raises(ValueError, match=f"{field} must be greater than zero"):
        make_debt(**{field: Decimal(value)})


@pytest.mark.parametrize("field", ["original_amount", "installment_payment"])
def test_money_fields_max_two_decimals(field):
    with pytest.raises(ValueError, match=f"{field} cannot have more than 2 decimals"):
        make_debt(**{field: Decimal("100.001")})


@pytest.mark.parametrize("bad_count", [12.0, "12", True])
def test_installment_count_must_be_int(bad_count):
    with pytest.raises(TypeError, match="installment_count must be an int"):
        make_debt(installment_count=bad_count)


@pytest.mark.parametrize("bad_count", [0, -3])
def test_installment_count_must_be_positive(bad_count):
    with pytest.raises(ValueError, match="installment_count must be greater than zero"):
        make_debt(installment_count=bad_count)


def test_installments_must_cover_original_amount():
    # 5 x 100 = 500 can never pay back 1000
    with pytest.raises(ValueError, match="must cover the original_amount"):
        make_debt(installment_count=5)


def test_category_must_be_a_debt_category():
    with pytest.raises(ValueError, match="not a debt category"):
        make_debt(category=Category("Food", CategoryKind.EXPENSE))


# --- DebtPayment ------------------------------------------------------------


def test_create_payment():
    debt = make_debt()
    payment = pay(debt, "100.00")

    assert payment.debt == debt
    assert payment.amount == Decimal("100.00")


def test_payment_amount_must_be_positive():
    with pytest.raises(ValueError, match="amount must be greater than zero"):
        pay(make_debt(), "0")


def test_payment_rejects_float():
    with pytest.raises(TypeError, match="amount must be a Decimal"):
        DebtPayment(make_debt(), 100.0, date(2026, 2, 1))


def test_payment_cannot_be_before_debt_start():
    with pytest.raises(ValueError, match="before the debt start_date"):
        pay(make_debt(), "100.00", paid_on=date(2025, 12, 31))


# --- calculations -----------------------------------------------------------


def test_new_debt_has_nothing_paid():
    debt = make_debt()

    assert total_paid(debt, []) == Decimal("0")
    assert remaining_balance(debt, []) == Decimal("1200.00")
    assert remaining_installments(debt, []) == 12
    assert not is_paid_off(debt, [])


def test_after_some_payments():
    debt = make_debt()
    payments = [pay(debt, "100.00"), pay(debt, "100.00"), pay(debt, "100.00")]

    assert total_paid(debt, payments) == Decimal("300.00")
    assert remaining_balance(debt, payments) == Decimal("900.00")
    assert remaining_installments(debt, payments) == 9


def test_partial_payment_rounds_installments_up():
    debt = make_debt()
    payments = [pay(debt, "150.00")]  # 1050 left = 10.5 installments

    assert remaining_installments(debt, payments) == 11


def test_payments_to_other_debts_are_ignored():
    motorcycle = make_debt()
    credit_card = make_debt(name="Credit card")
    payments = [pay(motorcycle, "100.00"), pay(credit_card, "500.00")]

    assert total_paid(motorcycle, payments) == Decimal("100.00")
    assert total_paid(credit_card, payments) == Decimal("500.00")


def test_fully_paid_debt():
    debt = make_debt()
    payments = [pay(debt, "100.00") for _ in range(12)]

    assert remaining_balance(debt, payments) == Decimal("0")
    assert remaining_installments(debt, payments) == 0
    assert is_paid_off(debt, payments)


def test_overpaying_never_gives_negative_balance():
    debt = make_debt()
    payments = [pay(debt, "1500.00")]

    assert remaining_balance(debt, payments) == Decimal("0")
    assert remaining_installments(debt, payments) == 0
    assert is_paid_off(debt, payments)
