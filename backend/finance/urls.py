from django.urls import path

from .views import (
    CurrentStudentDepositView,
    CurrentStudentTransactionListView,
    CurrentStudentWalletView,
)

urlpatterns = [
    path("wallet/", CurrentStudentWalletView.as_view(), name="current-student-wallet"),
    path(
        "transactions/",
        CurrentStudentTransactionListView.as_view(),
        name="current-student-transactions",
    ),
    path("deposit/", CurrentStudentDepositView.as_view(), name="current-student-deposit"),
]
