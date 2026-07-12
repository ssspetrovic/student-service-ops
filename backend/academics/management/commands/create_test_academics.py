from django.core.management.base import BaseCommand, CommandError

from academics.models import Course, Curriculum, CurriculumCourse, DegreeLevel, Enrollment
from accounts.management.test_data import PROFESSOR_EMAIL, STUDENT_EMAIL
from accounts.models import ProfessorProfile, StudentProfile


class Command(BaseCommand):
    help = "Create or update basic local test academics data."

    def handle(self, *args, **options):
        student = self.get_student_profile()
        professor = self.get_professor_profile()

        course = self.create_or_update_course(
            code="TEST01",
            name="Test Course",
            espb=5,
            professor=professor,
        )
        curriculum = self.create_or_update_curriculum(
            code="IE-BSC",
            name="Information Engineering",
            degree_level=DegreeLevel.BACHELOR,
            duration=4,
        )

        CurriculumCourse.objects.update_or_create(
            curriculum=curriculum,
            course=course,
            school_year="2020/2021",
            defaults={"semester": 1, "is_mandatory": True},
        )

        Enrollment.objects.update_or_create(
            student=student,
            course=course,
            school_year="2020/2021",
            defaults={"semester": 1},
        )

        self.stdout.write(self.style.SUCCESS("Created test academics data."))

    def get_student_profile(self):
        try:
            return StudentProfile.objects.get(user__email=STUDENT_EMAIL)
        except StudentProfile.DoesNotExist as e:
            raise CommandError(
                "Run 'create_test_accounts.py' command before this one."
            ) from e

    def get_professor_profile(self):
        try:
            return ProfessorProfile.objects.get(user__email=PROFESSOR_EMAIL)
        except ProfessorProfile.DoesNotExist as e:
            raise CommandError(
                "Run 'create_test_accounts.py' command before this one."
            ) from e

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
