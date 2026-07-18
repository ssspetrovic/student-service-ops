from dataclasses import dataclass

from accounts.models import StudentProfile
from finance.management.test_data import TEST_WALLETS
from finance.models import Wallet


@dataclass
class FinanceSeedData:
    wallets: list[Wallet]


def seed_finance(students: list[StudentProfile]) -> FinanceSeedData:
    students_by_email = {student.user.email: student for student in students}
    wallets = []

    for wallet_data in TEST_WALLETS:
        student = students_by_email[wallet_data["student_email"]]
        wallet, _ = Wallet.objects.update_or_create(
            student=student,
            defaults={
                "balance": wallet_data["balance"],
            },
        )
        wallets.append(wallet)

    return FinanceSeedData(wallets=wallets)
