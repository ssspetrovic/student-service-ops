from decimal import Decimal
from typing import Optional

from django.db import transaction

from accounts.models import StudentProfile
from exams.models import ExamRegistration

from .models import (
    Transaction,
    TransactionCause,
    Wallet,
)

CREDIT_TRANSACTION_CAUSES = {
    TransactionCause.DEPOSIT,
    TransactionCause.EXAM_REFUND,
}
DEBIT_TRANSACTION_CAUSES = {
    TransactionCause.EXAM_REGISTRATION,
}


class InsufficientFundsError(ValueError):
    pass


class InvalidTransactionAmountError(ValueError):
    pass


class InvalidTransactionCauseError(ValueError):
    pass


def _validate_amount(amount: Decimal) -> None:
    if amount < Decimal("1.00"):
        raise InvalidTransactionAmountError("Transaction amount must be at least 1.00.")


def _validate_credit_cause(cause: TransactionCause) -> None:
    if cause not in CREDIT_TRANSACTION_CAUSES:
        raise InvalidTransactionCauseError("Invalid credit transaction cause.")


def _validate_debit_cause(cause: TransactionCause) -> None:
    if cause not in DEBIT_TRANSACTION_CAUSES:
        raise InvalidTransactionCauseError("Invalid debit transaction cause.")


def get_wallet_balance(student: StudentProfile) -> Decimal:
    wallet, _ = Wallet.objects.get_or_create(student=student)
    return wallet.balance


@transaction.atomic
def credit_wallet(
    student: StudentProfile,
    amount: Decimal,
    cause: TransactionCause,
    exam_registration: Optional[ExamRegistration] = None,
) -> Transaction:
    _validate_amount(amount)
    _validate_credit_cause(cause)

    wallet, _ = Wallet.objects.select_for_update().get_or_create(student=student)

    wallet.balance += amount
    wallet.full_clean()
    wallet.save(update_fields=["balance", "updated_at"])

    transaction_record = Transaction(
        student=student,
        amount=amount,
        cause=cause,
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
    _validate_debit_cause(cause)

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
        exam_registration=exam_registration,
    )
    transaction_record.full_clean()
    transaction_record.save()

    return transaction_record
