from django.core.management.base import CommandError

from accounts.management.test_data import TEST_PROFESSORS, TEST_STUDENTS
from accounts.models import ProfessorProfile, StudentProfile


def get_test_student_profile():
    try:
        return StudentProfile.objects.get(user__email=TEST_STUDENTS[0]["email"])
    except StudentProfile.DoesNotExist as exc:
        raise CommandError(
            "Run `python manage.py create_test_accounts` before this command."
        ) from exc


def get_test_student_profiles():
    emails = [student["email"] for student in TEST_STUDENTS]
    student_queryset = StudentProfile.objects.select_related("user").filter(user__email__in=emails)
    students_by_email = {student.user.email: student for student in student_queryset}
    if len(students_by_email) != len(emails):
        raise CommandError("Run `python manage.py create_test_accounts` before this command.")
    return [students_by_email[email] for email in emails]


def get_test_professor_profile():
    try:
        return ProfessorProfile.objects.get(user__email=TEST_PROFESSORS[0]["email"])
    except ProfessorProfile.DoesNotExist as exc:
        raise CommandError(
            "Run `python manage.py create_test_accounts` before this command."
        ) from exc


def get_test_professor_profiles():
    emails = [professor["email"] for professor in TEST_PROFESSORS]
    professor_queryset = ProfessorProfile.objects.select_related("user").filter(
        user__email__in=emails
    )
    professors_by_email = {professor.user.email: professor for professor in professor_queryset}
    if len(professors_by_email) != len(emails):
        raise CommandError("Run `python manage.py create_test_accounts` before this command.")
    return [professors_by_email[email] for email in emails]
