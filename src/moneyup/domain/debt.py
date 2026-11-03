from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_CEILING, Decimal

from moneyup.domain.category import Category, CategoryKind
from moneyup.domain.money import check_money, check_positive_int


@dataclass(frozen=True)
class Debt:
    """Money you owe and pay back in fixed installments.

    Only facts that never change are stored here. What you still owe is
    calculated from the DebtPayment records (see remaining_balance).
    """

    name: str
    original_amount: Decimal
    category: Category
    start_date: date
    installment_count: int
    installment_payment: Decimal
    note: str = ""

    def __post_init__(self) -> None:
        cleaned = self.name.strip()
        if not cleaned:
            raise ValueError("Debt name cannot be empty")
        object.__setattr__(self, "name", cleaned)

        check_money(self.original_amount, "original_amount")
        check_money(self.installment_payment, "installment_payment")
        check_positive_int(self.installment_count, "installment_count")

        if self.total_to_pay < self.original_amount:
            raise ValueError(
                "installment_payment x installment_count must cover the "
                "original_amount"
            )

        if self.category.kind is not CategoryKind.DEBT:
            raise ValueError(
                f"Category '{self.category.name}' is a {self.category.kind} "
                "category, not a debt category"
            )

    @property
    def total_to_pay(self) -> Decimal:
        """Everything you will pay if you pay all installments."""
        return self.installment_payment * self.installment_count

    @property
    def interest_cost(self) -> Decimal:
        """What the debt costs you on top of what you borrowed."""
        return self.total_to_pay - self.original_amount


@dataclass(frozen=True)
class DebtPayment:
    """One payment you made towards a debt."""

    debt: Debt
    amount: Decimal
    paid_on: date
    note: str = ""

    def __post_init__(self) -> None:
        check_money(self.amount, "amount")
        if self.paid_on < self.debt.start_date:
            raise ValueError("A payment cannot be before the debt start_date")


def total_paid(debt: Debt, payments: Iterable[DebtPayment]) -> Decimal:
    """Add up the payments made to this debt (other debts are ignored)."""
    return sum(
        (p.amount for p in payments if p.debt == debt),
        start=Decimal("0"),
    )


def remaining_balance(debt: Debt, payments: Iterable[DebtPayment]) -> Decimal:
    """How much you still have to pay. Never below zero.

    If you paid more than total_to_pay, the balance is 0 (not negative):
    the debt is simply paid off.
    """
    return max(debt.total_to_pay - total_paid(debt, payments), Decimal("0"))


def remaining_installments(debt: Debt, payments: Iterable[DebtPayment]) -> int:
    """How many installments are left, based on the money still owed.

    Partial payments count: if you owe 1.5 installments, 2 are left
    (rounded up, because half an installment is still one more payment).
    """
    balance = remaining_balance(debt, payments)
    installments = (balance / debt.installment_payment).to_integral_value(
        rounding=ROUND_CEILING
    )
    return int(installments)


def is_paid_off(debt: Debt, payments: Iterable[DebtPayment]) -> bool:
    return remaining_balance(debt, payments) == 0
