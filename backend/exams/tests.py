from datetime import timedelta
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

    def test_student_can_reregister_after_cancellation(self):
        self.client.force_authenticate(user=self.student_user)
        url = reverse("exam-registration", kwargs={"exam_id": self.exam.id})

        first = self.client.post(url)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("300.00"))

        cancellation = self.client.post(
            reverse("exam-registration-cancel", kwargs={"registration_id": first.data["id"]})
        )
        self.assertEqual(cancellation.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

        second = self.client.post(url)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(first.data["id"], second.data["id"])
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("300.00"))

    def test_professor_cannot_grade_unfinished_exam(self):
        registration = ExamRegistration.objects.create(student=self.student, exam=self.exam)
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(
            reverse("exam-registration-grade", kwargs={"registration_id": registration.id}),
            {"grade": 8},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        registration.refresh_from_db()
        self.assertIsNone(registration.grade)
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)
