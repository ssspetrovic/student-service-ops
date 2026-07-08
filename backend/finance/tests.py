from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import StudentProfile, User, UserRole
from .models import Transaction, TransactionCause

# Create your tests here.


class TransactionAmountAndCauseTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(user=self.student_user)

    def test_transaction_stores_positive_amount_and_cause(self):
        transaction = Transaction.objects.create(
            student=self.student,
            amount=Decimal("100.00"),
            cause=TransactionCause.DEPOSIT,
        )

        self.assertEqual(transaction.amount, Decimal("100.00"))
        self.assertEqual(transaction.cause, TransactionCause.DEPOSIT)

    def test_transaction_rejects_amount_below_min(self):
        transaction = Transaction(
            student=self.student,
            amount=Decimal("0.00"),
            cause=TransactionCause.DEPOSIT,
        )

        with self.assertRaises(ValidationError):
            transaction.full_clean()
