from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User, UserRole, ProfessorProfile
from .models import Course, Curriculum, CurriculumCourse, DegreeLevel


# Create your tests here.
class CourseEspbTestCase(TestCase):
    def setUp(self):
        self.professor_user = User.objects.create_user(
            email="professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(user=self.professor_user)

    def test_create_course_rejects_espb_belpw_min(self):
        with self.assertRaises(IntegrityError):
            Course.objects.create(
                code="TCOURSE",
                name="Test Course",
                espb=0,
                professor=self.professor,
            )

    def test_create_course_rejects_espb_above_max(self):
        with self.assertRaises(IntegrityError):
            Course.objects.create(
                code="TCOURSE",
                name="Test Course",
                espb=61,
                professor=self.professor,
            )


class CurriculumCourseUniqueTestCase(TestCase):
    def setUp(self):
        self.professor_user = User.objects.create_user(
            email="professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(user=self.professor_user)

        self.course = Course.objects.create(
            code="TCOURSE",
            name="Test Course",
            espb=60,
            professor=self.professor,
        )

        self.curriculum = Curriculum.objects.create(
            code="TCURR",
            name="Test Curriculum",
            degree_level=DegreeLevel.MASTER,
            duration=3,
        )

    def test_curriculum_course_uniqueness(self):
        CurriculumCourse.objects.create(
            curriculum=self.curriculum,
            course=self.course,
            semester=1,
            school_year="2020/2021",
        )

        with self.assertRaises(IntegrityError):
            CurriculumCourse.objects.create(
                curriculum=self.curriculum,
                course=self.course,
                semester=3,
                school_year="2020/2021",
            )

    def test_curriculum_course_reject_semester_below_min(self):
        with self.assertRaises(IntegrityError):
            CurriculumCourse.objects.create(
                curriculum=self.curriculum,
                course=self.course,
                semester=0,
                school_year="2020/2021",
            )

    def test_curriculum_course_reject_semester_above_max(self):
        with self.assertRaises(IntegrityError):
            CurriculumCourse.objects.create(
                curriculum=self.curriculum,
                course=self.course,
                semester=5,
                school_year="2020/2021",
            )
