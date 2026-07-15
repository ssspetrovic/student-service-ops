from django.core.management.base import BaseCommand
from django.db import transaction

from academics.seeders import seed_academics
from accounts.seeders import seed_accounts
from exams.seeders import seed_exams


class Command(BaseCommand):
    help = "Create or update all local test data."

    @transaction.atomic
    def handle(self, *args, **options):
        accounts = seed_accounts()
        academics = seed_academics(
            students=accounts.students,
            professors=accounts.professors,
        )
        exams = seed_exams(
            courses=academics.courses,
            students=accounts.students,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created all test data: "
                f"{len(accounts.students)} students, "
                f"{len(accounts.professors)} professors, "
                f"{len(academics.courses)} courses, "
                f"{len(exams.exams)} exams."
            )
        )
