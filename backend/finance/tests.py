from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

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


class StudentFinanceApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(
            email="finance-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = create_student_profile(
            user=self.student_user,
            index_no="FIN-001",
        )
        Wallet.objects.create(student=self.student)

    def test_student_sees_only_own_transactions_newest_first(self):
        other_user = User.objects.create_user(
            email="other-finance-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        other_student = create_student_profile(
            user=other_user,
            index_no="FIN-002",
        )
        older = Transaction.objects.create(
            student=self.student,
            amount=Decimal("10.00"),
            cause=TransactionCause.DEPOSIT,
        )
        newer = Transaction.objects.create(
            student=self.student,
            amount=Decimal("20.00"),
            cause=TransactionCause.DEPOSIT,
        )
        Transaction.objects.create(
            student=other_student,
            amount=Decimal("30.00"),
            cause=TransactionCause.DEPOSIT,
        )
        Transaction.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        self.client.force_authenticate(user=self.student_user)

        response = self.client.get(reverse("current-student-transactions"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [newer.pk, older.pk])

    def test_valid_deposit_creates_transaction_and_updates_balance(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(
            reverse("current-student-deposit"), {"amount": "125.50"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["balance"], "125.50")
        self.assertEqual(response.data["transaction"]["amount"], "125.50")
        self.assertEqual(response.data["transaction"]["cause"], TransactionCause.DEPOSIT)
        self.student.wallet.refresh_from_db()
        self.assertEqual(self.student.wallet.balance, Decimal("125.50"))
        self.assertEqual(self.student.transactions.count(), 1)
