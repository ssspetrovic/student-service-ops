from django.core.management.base import BaseCommand

from academics.seeders import seed_academics
from accounts.management.test_data_helpers import (
    get_test_professor_profiles,
    get_test_student_profiles,
)


class Command(BaseCommand):
    help = "Create or update basic local test academics data."

    def handle(self, *args, **options):
        students = get_test_student_profiles()
        professors = get_test_professor_profiles()
        result = seed_academics(students=students, professors=professors)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created test academics data: {len(result.courses)} courses."
            )
        )
