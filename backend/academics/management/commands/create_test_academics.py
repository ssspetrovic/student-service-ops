from django.core.management.base import BaseCommand

from academics.management.test_data import (
    COURSE_CODE,
    COURSE_ESPB,
    COURSE_NAME,
    CURRICULUM_CODE,
    CURRICULUM_DURATION,
    CURRICULUM_NAME,
    SCHOOL_YEAR,
    SEMESTER,
)
from academics.models import Course, Curriculum, CurriculumCourse, DegreeLevel, Enrollment
from accounts.management.test_data_helpers import (
    get_test_professor_profile,
    get_test_student_profile,
)


class Command(BaseCommand):
    help = "Create or update basic local test academics data."

    def handle(self, *args, **options):
        student = get_test_student_profile()
        professor = get_test_professor_profile()

        course = self.create_or_update_course(
            code=COURSE_CODE,
            name=COURSE_NAME,
            espb=COURSE_ESPB,
            professor=professor,
        )
        curriculum = self.create_or_update_curriculum(
            code=CURRICULUM_CODE,
            name=CURRICULUM_NAME,
            degree_level=DegreeLevel.BACHELOR,
            duration=CURRICULUM_DURATION,
        )

        CurriculumCourse.objects.update_or_create(
            curriculum=curriculum,
            course=course,
            school_year=SCHOOL_YEAR,
            defaults={"semester": SEMESTER, "is_mandatory": True},
        )

        Enrollment.objects.update_or_create(
            student=student,
            course=course,
            school_year=SCHOOL_YEAR,
            defaults={"semester": SEMESTER},
        )

        self.stdout.write(self.style.SUCCESS("Created test academics data."))

    def create_or_update_course(self, code, name, espb, professor):
        course, _created = Course.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "espb": espb,
                "professor": professor,
            },
        )

        return course

    def create_or_update_curriculum(self, code, name, degree_level, duration):
        curriculum, _created = Curriculum.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "degree_level": degree_level,
                "duration": duration,
            },
        )

        return curriculum
