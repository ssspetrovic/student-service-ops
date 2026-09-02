from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserRole
from accounts.test_helpers import create_student_profile
from .models import Wallet


class StudentFinanceApiTestCase(TestCase):
    def test_deposit_updates_wallet(self):
        client = APIClient()
        user = User.objects.create_user(
            email="student@example.com",
            password="StrongPassword123!",
            role=UserRole.STUDENT,
        )
        student = create_student_profile(user=user, index_no="FIN-001")
        wallet = Wallet.objects.create(student=student)
        client.force_authenticate(user=user)

        response = client.post(
            reverse("current-student-deposit"), {"amount": "125.50"}, format="json"
        )

        wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(wallet.balance, Decimal("125.50"))
