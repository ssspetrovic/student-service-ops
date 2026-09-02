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

    def test_student_registers_and_cancels_exam(self):
        exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.client.force_authenticate(user=self.student_user)

        registration_response = self.client.post(
            reverse("exam-registration", kwargs={"exam_id": exam.id})
        )
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
        cancellation_response = self.client.post(
            reverse(
                "exam-registration-cancel",
                kwargs={"registration_id": registration_response.data["id"]},
            )
        )
        self.wallet.refresh_from_db()

        self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cancellation_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

    def test_insufficient_funds_rejects_registration(self):
        exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.wallet.balance = Decimal("100.00")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(reverse("exam-registration", kwargs={"exam_id": exam.id}))

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.wallet.balance, Decimal("100.00"))

    def test_student_can_reregister_after_cancellation(self):
        exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.client.force_authenticate(user=self.student_user)

        first_registration = self.client.post(
            reverse("exam-registration", kwargs={"exam_id": exam.id})
        )
        cancellation = self.client.post(
            reverse(
                "exam-registration-cancel",
                kwargs={"registration_id": first_registration.data["id"]},
            )
        )
        second_registration = self.client.post(
            reverse("exam-registration", kwargs={"exam_id": exam.id})
        )

        self.assertEqual(first_registration.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cancellation.status_code, status.HTTP_200_OK)
        self.assertEqual(second_registration.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(first_registration.data["id"], second_registration.data["id"])

    def test_professor_creates_exam_and_grades_registration(self):
        self.client.force_authenticate(user=self.professor_user)
        create_response = self.client.post(
            reverse("exams"),
            {
                "course_code": self.course.code,
                "date": (timezone.now() + timedelta(days=30)).isoformat(),
                "room": "S1",
            },
            format="json",
        )
        completed_exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() - timedelta(days=1),
        )
        registration = ExamRegistration.objects.create(student=self.student, exam=completed_exam)

        grade_response = self.client.patch(
            reverse("exam-registration-grade", kwargs={"registration_id": registration.id}),
            {"grade": 8},
            format="json",
        )

        registration.refresh_from_db()
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Exam.objects.filter(pk=create_response.data["id"]).exists())
        self.assertEqual(grade_response.status_code, status.HTTP_200_OK)
        self.assertEqual(registration.status, ExamRegistrationStatus.GRADED)

    def test_professor_cannot_grade_unfinished_exam(self):
        exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        registration = ExamRegistration.objects.create(student=self.student, exam=exam)
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(
            reverse("exam-registration-grade", kwargs={"registration_id": registration.id}),
            {"grade": 8},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
