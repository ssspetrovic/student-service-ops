from django.core.management.base import BaseCommand
from django.db import transaction

from academics.seeders import seed_academics
from accounts.seeders import clear_demo, seed_accounts
from exams.seeders import seed_exams
from finance.seeders import seed_finance


class Command(BaseCommand):
    help = "Refresh all local demo data, discarding manual activity for demo accounts."

    @transaction.atomic
    def handle(self, *args, **options):
        clear_demo()
        accounts = seed_accounts()
        academics = seed_academics(
            students=accounts.students,
            professors=accounts.professors,
        )
        finance = seed_finance(students=accounts.students)
        exams = seed_exams(courses=academics.courses, students=accounts.students)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created all test data: "
                f"{len(accounts.students)} students, "
                f"{len(accounts.professors)} professors, "
                f"{len(academics.courses)} courses, "
                f"{len(exams.exams)} exams, "
                f"{len(exams.registrations)} registrations, "
                f"{len(finance.wallets)} wallets."
            )
        )
