from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User, UserRole
from accounts.test_helpers import create_student_profile
from .models import Transaction, TransactionCause, Wallet

# Create your tests here.


class TransactionAmountTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = create_student_profile(user=self.student_user)

    def test_transaction_rejects_amount_below_min(self):
        transaction = Transaction(
            student=self.student,
            amount=Decimal("0.00"),
            cause=TransactionCause.DEPOSIT,
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
        self.student = create_student_profile(user=self.student_user)

    def test_wallet_rejects_negative_balance(self):
        wallet = Wallet(
            student=self.student,
            balance=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            wallet.full_clean()
