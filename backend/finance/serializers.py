from rest_framework import serializers

from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    student_index_no = serializers.CharField(source="student.index_no")

    class Meta:
        model = Wallet
        fields = ["student_index_no", "balance", "updated_at"]
