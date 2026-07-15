from django.core.management.base import BaseCommand

from accounts.seeders import seed_accounts


class Command(BaseCommand):
    help = "Create or update basic local test users."

    def handle(self, *args, **options):
        result = seed_accounts()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created test accounts: "
                f"{len(result.students)} students, "
                f"{len(result.professors)} professors."
            )
        )
