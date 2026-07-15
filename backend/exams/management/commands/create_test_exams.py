from django.core.management.base import BaseCommand, CommandError

from academics.management.test_data import TEST_COURSES
from academics.models import Course
from accounts.management.test_data_helpers import (
    get_test_student_profiles,
)
from exams.seeders import seed_exams


class Command(BaseCommand):
    help = "Create or update basic local test exams data."

    def handle(self, *args, **options):
        students = get_test_student_profiles()
        courses = self.get_test_courses()
        result = seed_exams(courses=courses, students=students)

        self.stdout.write(
            self.style.SUCCESS(f"Created test exams data: {len(result.exams)} exams.")
        )

    def get_test_courses(self):
        course_codes = [course["code"] for course in TEST_COURSES]
        courses = Course.objects.select_related("professor").filter(code__in=course_codes)
        courses_by_code = {course.code: course for course in courses}

        missing_codes = set(course_codes) - set(courses_by_code)
        if missing_codes:
            raise CommandError(
                "Run `python manage.py create_test_academics` before this command."
            )

        return [courses_by_code[code] for code in course_codes]
