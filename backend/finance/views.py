from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView

from accounts.permissions import IsStudent

from .models import Wallet
from .serializers import WalletSerializer

# Create your views here.


class CurrentStudentWalletView(RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return get_object_or_404(Wallet, student__user=self.request.user)
