from datetime import date
from decimal import Decimal

import pytest

from moneyup.domain import (
    Category,
    CategoryKind,
    Saving,
    SavingDeposit,
    is_goal_reached,
    progress_percent,
    remaining_to_goal,
    total_saved,
)
from moneyup.domain.saving import remaining_installments

EMERGENCY = Category("Emergency fund", CategoryKind.SAVING)
START = date(2026, 1, 1)


def make_saving(**changes) -> Saving:
    """Build a valid saving; pass keyword arguments to change any field."""
    fields = dict(
        name="Emergency fund",
        goal_amount=Decimal("1000.00"),
        category=EMERGENCY,
        start_date=START,
        installment_count=10,
        installment_payment=Decimal("100.00"),
    )
    fields.update(changes)
    return Saving(**fields)


def deposit(
    saving: Saving, amount: str, deposited_on: date = date(2026, 2, 1)
) -> SavingDeposit:
    return SavingDeposit(saving, Decimal(amount), deposited_on)


# --- Saving -----------------------------------------------------------------


def test_create_saving():
    saving = make_saving(note="3 months of rent")

    assert saving.name == "Emergency fund"
    assert saving.goal_amount == Decimal("1000.00")
    assert saving.total_to_save == Decimal("1000.00")
    assert saving.note == "3 months of rent"


def test_name_is_trimmed():
    assert make_saving(name="  Vacation ").name == "Vacation"


def test_empty_name_is_rejected():
    with pytest.raises(ValueError, match="name cannot be empty"):
        make_saving(name="  ")


@pytest.mark.parametrize("field", ["goal_amount", "installment_payment"])
def test_money_fields_reject_floats(field):
    with pytest.raises(TypeError, match=f"{field} must be a Decimal"):
        make_saving(**{field: 100.0})


@pytest.mark.parametrize("field", ["goal_amount", "installment_payment"])
@pytest.mark.parametrize("value", ["0", "-5.00"])
def test_money_fields_must_be_positive(field, value):
    with pytest.raises(ValueError, match=f"{field} must be greater than zero"):
        make_saving(**{field: Decimal(value)})


@pytest.mark.parametrize("bad_count", [10.0, "10", True])
def test_installment_count_must_be_int(bad_count):
    with pytest.raises(TypeError, match="installment_count must be an int"):
        make_saving(installment_count=bad_count)


def test_installment_count_must_be_positive():
    with pytest.raises(ValueError, match="installment_count must be greater than zero"):
        make_saving(installment_count=0)


def test_plan_must_reach_the_goal():
    # 5 x 100 = 500 never reaches 1000
    with pytest.raises(ValueError, match="must cover the goal_amount"):
        make_saving(installment_count=5)


def test_category_must_be_a_saving_category():
    with pytest.raises(ValueError, match="not a saving category"):
        make_saving(category=Category("Loans", CategoryKind.DEBT))


# --- SavingDeposit ----------------------------------------------------------


def test_deposit_amount_must_be_positive():
    with pytest.raises(ValueError, match="amount must be greater than zero"):
        deposit(make_saving(), "0")


def test_deposit_cannot_be_before_saving_start():
    with pytest.raises(ValueError, match="before the saving start_date"):
        deposit(make_saving(), "100.00", deposited_on=date(2025, 12, 31))


# --- calculations -----------------------------------------------------------


def test_new_saving_has_nothing_saved():
    saving = make_saving()

    assert total_saved(saving, []) == Decimal("0")
    assert remaining_to_goal(saving, []) == Decimal("1000.00")
    assert remaining_installments(saving, []) == 10
    assert progress_percent(saving, []) == Decimal("0.00")
    assert not is_goal_reached(saving, [])


def test_after_some_deposits():
    saving = make_saving()
    deposits = [deposit(saving, "100.00"), deposit(saving, "150.00")]

    assert total_saved(saving, deposits) == Decimal("250.00")
    assert remaining_to_goal(saving, deposits) == Decimal("750.00")
    assert remaining_installments(saving, deposits) == 8  # 7.5 rounded up
    assert progress_percent(saving, deposits) == Decimal("25.00")


def test_progress_percent_has_two_decimals():
    saving = make_saving(goal_amount=Decimal("300.00"), installment_count=3)
    deposits = [deposit(saving, "100.00")]

    assert progress_percent(saving, deposits) == Decimal("33.33")


def test_deposits_to_other_savings_are_ignored():
    emergency = make_saving()
    vacation = make_saving(name="Vacation")
    deposits = [deposit(emergency, "100.00"), deposit(vacation, "400.00")]

    assert total_saved(emergency, deposits) == Decimal("100.00")
    assert total_saved(vacation, deposits) == Decimal("400.00")


def test_goal_reached():
    saving = make_saving()
    deposits = [deposit(saving, "100.00") for _ in range(10)]

    assert remaining_to_goal(saving, deposits) == Decimal("0")
    assert remaining_installments(saving, deposits) == 0
    assert progress_percent(saving, deposits) == Decimal("100.00")
    assert is_goal_reached(saving, deposits)


def test_saving_more_than_goal_is_capped():
    saving = make_saving()
    deposits = [deposit(saving, "1500.00")]

    assert total_saved(saving, deposits) == Decimal("1500.00")  # real total kept
    assert remaining_to_goal(saving, deposits) == Decimal("0")
    assert progress_percent(saving, deposits) == Decimal("100.00")
    assert is_goal_reached(saving, deposits)
