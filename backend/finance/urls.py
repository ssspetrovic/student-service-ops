from django.urls import path

from .views import CurrentStudentWalletView

urlpatterns = [
    path("wallet/", CurrentStudentWalletView.as_view(), name="current-student-wallet"),
]
