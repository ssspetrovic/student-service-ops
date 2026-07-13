from django.core.management.base import CommandError

from accounts.management.test_data import PROFESSOR_EMAIL, STUDENT_EMAIL
from accounts.models import ProfessorProfile, StudentProfile


def get_test_student_profile():
    try:
        return StudentProfile.objects.get(user__email=STUDENT_EMAIL)
    except StudentProfile.DoesNotExist as exc:
        raise CommandError(
            "Run `python manage.py create_test_accounts` before this command."
        ) from exc


def get_test_professor_profile():
    try:
        return ProfessorProfile.objects.get(user__email=PROFESSOR_EMAIL)
    except ProfessorProfile.DoesNotExist as exc:
        raise CommandError(
            "Run `python manage.py create_test_accounts` before this command."
        ) from exc
