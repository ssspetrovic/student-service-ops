from decimal import Decimal

from rest_framework import serializers

from .models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    student_index_no = serializers.CharField(source="student.index_no")

    class Meta:
        model = Wallet
        fields = ["student_index_no", "balance", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    exam_registration_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = ["id", "amount", "cause", "created_at", "exam_registration_id"]


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("1.00"))
