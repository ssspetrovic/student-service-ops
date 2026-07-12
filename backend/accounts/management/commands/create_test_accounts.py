from django.core.management.base import BaseCommand

from accounts.management.test_data import (
    PROFESSOR_EMAIL,
    PROFESSOR_EMPLOYEE_NO,
    PROFESSOR_PASSWORD,
    STUDENT_EMAIL,
    STUDENT_INDEX_NO,
    STUDENT_PASSWORD,
)
from accounts.models import ProfessorProfile, StudentProfile, User, UserRole


class Command(BaseCommand):
    help = "Create or update basic local test users."

    def handle(self, *args, **options):
        student = self.create_or_update_user(
            email=STUDENT_EMAIL,
            password=STUDENT_PASSWORD,
            role=UserRole.STUDENT,
        )
        StudentProfile.objects.update_or_create(
            user=student,
            defaults={
                "index_no": STUDENT_INDEX_NO,
                "current_year_of_study": 1,
            },
        )

        professor = self.create_or_update_user(
            email=PROFESSOR_EMAIL,
            password=PROFESSOR_PASSWORD,
            role=UserRole.PROFESSOR,
        )
        ProfessorProfile.objects.update_or_create(
            user=professor,
            defaults={"employee_no": PROFESSOR_EMPLOYEE_NO},
        )

        self.stdout.write(self.style.SUCCESS("Created test student and professor users."))

    def create_or_update_user(self, email, password, role):
        user, _created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "role": role,
            },
        )
        user.username = email
        user.role = role
        user.set_password(password)
        user.save()
        return user
