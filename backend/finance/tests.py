from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import StudentProfile, User, UserRole
from .models import Transaction, TransactionCause, TransactionType, Wallet

# Create your tests here.


class TransactionAmountAndCauseTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(user=self.student_user)

    def test_transaction_stores_positive_amount_cause_and_type(self):
        transaction = Transaction.objects.create(
            student=self.student,
            amount=Decimal("100.00"),
            cause=TransactionCause.DEPOSIT,
            type=TransactionType.CREDIT,
        )

        self.assertEqual(transaction.amount, Decimal("100.00"))
        self.assertEqual(transaction.cause, TransactionCause.DEPOSIT)
        self.assertEqual(transaction.type, TransactionType.CREDIT)

    def test_transaction_rejects_amount_below_min(self):
        transaction = Transaction(
            student=self.student,
            amount=Decimal("0.00"),
            cause=TransactionCause.DEPOSIT,
            type=TransactionType.CREDIT,
        )

        with self.assertRaises(ValidationError):
            transaction.full_clean()


class WalletTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            email="wallet-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(user=self.student_user)

    def test_wallet_defaults_to_zero_balance(self):
        wallet = Wallet.objects.create(student=self.student)

        self.assertEqual(wallet.balance, Decimal("0.00"))

    def test_wallet_rejects_negative_balance(self):
        wallet = Wallet(
            student=self.student,
            balance=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            wallet.full_clean()
