from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User, UserRole, ProfessorProfile
from .models import Course

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
