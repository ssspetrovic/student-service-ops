from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from accounts.models import StudentProfile
from exams.models import ExamRegistration

# Create your models here.


class TransactionCause(models.TextChoices):
    EXAM_REGISTRATION = "exam_registration", "Exam registration"
    EXAM_REFUND = "exam_refund", "Exam refuns"
    DEPOSIT = "deposit", "Deposit"


class TransactionType(models.TextChoices):
    CREDIT = "credit", "Credit"
    DEBIT = "debit", "Debit"


class Transaction(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.00"))],
    )
    cause = models.CharField(
        max_length=20,
        choices=TransactionCause.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TransactionType.choices, max_length=10)
    exam_registration = models.ForeignKey(
        ExamRegistration,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transactions",
    )

    def __str__(self):
        return f"{self.cause} - {self.amount} [{self.created_at}]"


class Wallet(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(
        default=Decimal("0.00"),
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    updated_at = models.DateTimeField(auto_now=True)
