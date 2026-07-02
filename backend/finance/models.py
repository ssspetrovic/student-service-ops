from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from accounts.models import StudentProfile

# Create your models here.


class TransactionCause(models.TextChoices):
    EXAM_REGISTRATION = "exam_registration", "Exam registration"
    EXAM_REFUND = "exam_refund", "Exam refuns"
    DEPOSIT = "deposit", "Deposit"


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

    def __str__(self):
        return f"{self.cause} - {self.amount} [{self.created_at}]"
