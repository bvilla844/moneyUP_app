from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_CEILING, Decimal

from moneyup.domain.category import Category, CategoryKind
from moneyup.domain.money import check_money, check_positive_int


@dataclass(frozen=True)
class Saving:
    """A savings plan: reach goal_amount by depositing a fixed amount
    installment_count times (for a project, an emergency fund, an investment).

    Only the plan is stored here. How much you have saved is calculated
    from the SavingDeposit records (see total_saved).
    """

    name: str
    goal_amount: Decimal
    category: Category
    start_date: date
    installment_count: int
    installment_payment: Decimal
    note: str = ""

    def __post_init__(self) -> None:
        cleaned = self.name.strip()
        if not cleaned:
            raise ValueError("Saving name cannot be empty")
        object.__setattr__(self, "name", cleaned)

        check_money(self.goal_amount, "goal_amount")
        check_money(self.installment_payment, "installment_payment")
        check_positive_int(self.installment_count, "installment_count")

        if self.total_to_save < self.goal_amount:
            raise ValueError(
                "installment_payment x installment_count must cover the "
                "goal_amount"
            )

        if self.category.kind is not CategoryKind.SAVING:
            raise ValueError(
                f"Category '{self.category.name}' is a {self.category.kind} "
                "category, not a saving category"
            )

    @property
    def total_to_save(self) -> Decimal:
        """Everything you will save if you make all planned deposits."""
        return self.installment_payment * self.installment_count


@dataclass(frozen=True)
class SavingDeposit:
    """One deposit you made into a savings plan."""

    saving: Saving
    amount: Decimal
    deposited_on: date
    note: str = ""

    def __post_init__(self) -> None:
        check_money(self.amount, "amount")
        if self.deposited_on < self.saving.start_date:
            raise ValueError("A deposit cannot be before the saving start_date")


def total_saved(saving: Saving, deposits: Iterable[SavingDeposit]) -> Decimal:
    """Add up the deposits made to this saving (other savings are ignored)."""
    return sum(
        (d.amount for d in deposits if d.saving == saving),
        start=Decimal("0"),
    )


def remaining_to_goal(saving: Saving, deposits: Iterable[SavingDeposit]) -> Decimal:
    """How much is still missing to reach the goal. Never below zero."""
    return max(saving.goal_amount - total_saved(saving, deposits), Decimal("0"))


def remaining_installments(saving: Saving, deposits: Iterable[SavingDeposit]) -> int:
    """How many deposits of installment_payment are still needed (rounded up)."""
    missing = remaining_to_goal(saving, deposits)
    installments = (missing / saving.installment_payment).to_integral_value(
        rounding=ROUND_CEILING
    )
    return int(installments)


def progress_percent(saving: Saving, deposits: Iterable[SavingDeposit]) -> Decimal:
    """How close you are to the goal, from 0 to 100 (2 decimals, capped at 100)."""
    percent = total_saved(saving, deposits) / saving.goal_amount * 100
    return min(percent, Decimal("100")).quantize(Decimal("0.01"))


def is_goal_reached(saving: Saving, deposits: Iterable[SavingDeposit]) -> bool:
    return remaining_to_goal(saving, deposits) == 0
