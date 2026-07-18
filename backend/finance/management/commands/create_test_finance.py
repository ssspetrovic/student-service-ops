from django.core.management.base import BaseCommand

from accounts.management.test_data_helpers import get_test_student_profiles
from finance.seeders import seed_finance


class Command(BaseCommand):
    help = "Create or update basic local test finance data."

    def handle(self, *args, **options):
        students = get_test_student_profiles()
        result = seed_finance(students=students)

        self.stdout.write(
            self.style.SUCCESS(f"Created test finance data: {len(result.wallets)} wallets.")
        )
