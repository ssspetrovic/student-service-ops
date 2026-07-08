from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from academics.models import Course
from accounts.models import ProfessorProfile, StudentProfile, User, UserRole
from .models import Exam, ExamRegistration, ExamRegistrationStatus

# Create your tests here.


class ExamRegistrationGradeAndStatusTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(user=self.student_user)

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
        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now(),
        )

    def test_exam_registration_defaults_to_active_status(self):
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )

        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)

    def test_exam_registration_allows_empty_grade(self):
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
            grade=None,
        )

        self.assertIsNone(registration.grade)

    def test_exam_registration_rejects_grade_below_min(self):
        with self.assertRaises(IntegrityError):
            ExamRegistration.objects.create(
                student=self.student,
                exam=self.exam,
                grade=4,
            )

    def test_exam_registration_rejects_grade_above_max(self):
        with self.assertRaises(IntegrityError):
            ExamRegistration.objects.create(
                student=self.student,
                exam=self.exam,
                grade=11,
            )
