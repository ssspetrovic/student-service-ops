from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import StudentProfile
from accounts.permissions import IsStudent

from .models import Transaction, TransactionCause, Wallet
from .serializers import DepositSerializer, TransactionSerializer, WalletSerializer
from .services import credit_wallet

# Create your views here.


class CurrentStudentWalletView(RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return get_object_or_404(Wallet, student__user=self.request.user)


class CurrentStudentTransactionListView(ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Transaction.objects.filter(student__user=self.request.user).order_by(
            "-created_at", "-pk"
        )


class CurrentStudentDepositView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = get_object_or_404(StudentProfile, user=request.user)
        transaction = credit_wallet(
            student=student,
            amount=serializer.validated_data["amount"],
            cause=TransactionCause.DEPOSIT,
        )
        wallet = Wallet.objects.get(student=student)
        return Response(
            {
                "transaction": TransactionSerializer(transaction).data,
                "balance": str(wallet.balance),
            },
            status=status.HTTP_201_CREATED,
        )
