from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from academics.management.test_data import COURSE_CODE
from academics.models import Course
from accounts.management.test_data_helpers import (
    get_test_professor_profile,
    get_test_student_profile,
)
from exams.models import Exam, ExamRegistration, ExamRegistrationStatus

TEST_EXAM_DATE = timezone.make_aware(datetime(2026, 9, 1, 10, 0))
TEST_EXAM_ROOM = "A1"


class Command(BaseCommand):
    help = "Create or update basic local test exams data."

    def handle(self, *args, **options):
        student = get_test_student_profile()
        professor = get_test_professor_profile()
        course = self.get_test_course()

        exam = self.create_or_update_exam(
            course=course,
            professor=professor,
            date=TEST_EXAM_DATE,
            room=TEST_EXAM_ROOM,
        )

        ExamRegistration.objects.update_or_create(
            student=student,
            exam=exam,
            defaults={
                "grade": None,
                "status": ExamRegistrationStatus.ACTIVE,
            },
        )

        self.stdout.write(self.style.SUCCESS("Created test exams data."))

    def get_test_course(self):
        try:
            return Course.objects.get(code=COURSE_CODE)
        except Course.DoesNotExist as exc:
            raise CommandError(
                "Run `python manage.py create_test_academics` before this command."
            ) from exc

    def create_or_update_exam(self, course, professor, date, room):
        exam, _created = Exam.objects.update_or_create(
            course=course,
            professor=professor,
            date=date,
            defaults={
                "room": room,
            },
        )
        return exam
