from datetime import datetime, timedelta, timezone as datetime_timezone
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from academics.models import Course, Enrollment, EnrollmentStatus
from accounts.models import ProfessorProfile, User, UserRole
from accounts.test_helpers import create_student_profile
from finance.models import Wallet

from .models import Exam, ExamRegistration, ExamRegistrationStatus


class ExamApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor_user = User.objects.create_user(
            email="professor@example.com",
            password="StrongPassword123!",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="PROF-001",
        )
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="StrongPassword123!",
            role=UserRole.STUDENT,
        )
        self.student = create_student_profile(user=self.student_user, index_no="STUDENT-001")
        self.course = Course.objects.create(
            code="COURSE-001",
            name="Test Course",
            espb=6,
            professor=self.professor,
        )
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            school_year="2026/2027",
            semester=1,
            status=EnrollmentStatus.ACTIVE,
        )
        self.wallet = Wallet.objects.create(student=self.student, balance=Decimal("500.00"))

        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )

    def test_insufficient_funds_rejects_registration(self):
        self.wallet.balance = Decimal("100.00")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(reverse("exam-registration", kwargs={"exam_id": self.exam.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("100.00"))
        self.assertFalse(ExamRegistration.objects.filter(student=self.student).exists())

    def test_grading_end_time_boundary(self):
        self.exam.date = datetime(2026, 9, 10, 9, tzinfo=datetime_timezone.utc)
        self.exam.save(update_fields=["date"])
        end = datetime(2026, 9, 10, 12, tzinfo=datetime_timezone.utc)
        self.assertEqual(self.exam.ends_at, end)
        registration = ExamRegistration.objects.create(student=self.student, exam=self.exam)
        self.client.force_authenticate(user=self.professor_user)
        url = reverse("exam-registration-grade", kwargs={"registration_id": registration.id})

        with patch("exams.services.timezone.now", return_value=end - timedelta(microseconds=1)):
            response = self.client.patch(url, {"grade": 8}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        registration.refresh_from_db()
        self.assertIsNone(registration.grade)
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)

        with patch("exams.services.timezone.now", return_value=end):
            response = self.client.patch(url, {"grade": 8}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        registration.refresh_from_db()
        self.assertEqual(registration.grade, 8)
        self.assertEqual(registration.status, ExamRegistrationStatus.GRADED)

        with patch("exams.services.timezone.now", return_value=end + timedelta(seconds=1)):
            response = self.client.patch(url, {"grade": 9}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        registration.refresh_from_db()
        self.assertEqual(registration.grade, 9)
        self.assertEqual(registration.status, ExamRegistrationStatus.GRADED)

    def test_professor_cannot_grade_unfinished_exam(self):
        now = datetime(2026, 9, 10, 10, tzinfo=datetime_timezone.utc)
        self.exam.date = now - timedelta(hours=1)
        self.exam.save(update_fields=["date"])
        registration = ExamRegistration.objects.create(student=self.student, exam=self.exam)
        self.client.force_authenticate(user=self.professor_user)

        with patch("exams.services.timezone.now", return_value=now):
            response = self.client.patch(
                reverse("exam-registration-grade", kwargs={"registration_id": registration.id}),
                {"grade": 8},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        registration.refresh_from_db()
        self.assertIsNone(registration.grade)
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)
