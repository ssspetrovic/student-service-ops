from decimal import Decimal
from typing import Optional

from django.db import transaction

from accounts.models import StudentProfile
from exams.models import ExamRegistration

from .models import (
    Transaction,
    TransactionCause,
    TransactionType,
    Wallet,
)


class InsufficientFundsError(ValueError):
    pass


class InvalidTransactionAmountError(ValueError):
    pass


def _validate_amount(amount: Decimal) -> None:
    if amount <= Decimal("0"):
        raise InvalidTransactionAmountError("Transaction amount must be greater than zero.")


@transaction.atomic
def credit_wallet(
    student: StudentProfile,
    amount: Decimal,
    cause: TransactionCause,
    exam_registration: Optional[ExamRegistration] = None,
) -> Transaction:
    _validate_amount(amount)

    wallet, _ = Wallet.objects.select_for_update().get_or_create(student=student)

    wallet.balance += amount
    wallet.full_clean()
    wallet.save(update_fields=["balance", "updated_at"])

    transaction_record = Transaction(
        student=student,
        amount=amount,
        cause=cause,
        type=TransactionType.CREDIT,
        exam_registration=exam_registration,
    )
    transaction_record.full_clean()
    transaction_record.save()

    return transaction_record


@transaction.atomic
def debit_wallet(
    student: StudentProfile,
    amount: Decimal,
    cause: TransactionCause,
    exam_registration: Optional[ExamRegistration] = None,
) -> Transaction:
    _validate_amount(amount)

    wallet, _ = Wallet.objects.select_for_update().get_or_create(student=student)

    if amount > wallet.balance:
        raise InsufficientFundsError(
            f"Insufficient funds: available balance is {wallet.balance}, but {amount} is required."
        )

    wallet.balance -= amount
    wallet.full_clean()
    wallet.save(update_fields=["balance", "updated_at"])

    transaction_record = Transaction(
        student=student,
        amount=amount,
        cause=cause,
        type=TransactionType.DEBIT,
        exam_registration=exam_registration,
    )
    transaction_record.full_clean()
    transaction_record.save()

    return transaction_record
