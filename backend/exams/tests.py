from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from academics.models import Course, Enrollment, EnrollmentStatus
from accounts.models import ProfessorProfile, User, UserRole
from accounts.test_helpers import create_student_profile
from finance.models import Transaction, TransactionCause, Wallet

from .models import Exam, ExamRegistration, ExamRegistrationStatus
from .services import cancel_exam_registration


class ExamApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor_user = User.objects.create_user(
            email="professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="PROF-001",
        )
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="student123",
            role=UserRole.STUDENT,
            first_name="Test",
            last_name="Student",
        )
        self.student = create_student_profile(
            user=self.student_user,
            index_no="STUDENT-001",
        )
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
        self.wallet = Wallet.objects.create(
            student=self.student,
            balance=Decimal("500.00"),
        )

    def create_exam(self, days_from_now=10):
        return Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=days_from_now),
        )

    def create_paid_registration(self):
        exam = self.create_exam()
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=exam,
        )
        Transaction.objects.create(
            student=self.student,
            amount=Decimal("200.00"),
            cause=TransactionCause.EXAM_REGISTRATION,
            exam_registration=registration,
        )
        self.wallet.balance = Decimal("300.00")
        self.wallet.save(update_fields=["balance"])
        return registration

    def test_student_can_register_for_exam(self):
        exam = self.create_exam()
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(reverse("exam-registration", kwargs={"exam_id": exam.id}))

        self.wallet.refresh_from_db()
        registration = ExamRegistration.objects.get(student=self.student, exam=exam)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
        self.assertTrue(
            Transaction.objects.filter(
                cause=TransactionCause.EXAM_REGISTRATION,
                exam_registration=registration,
            ).exists()
        )

    def test_registration_with_insufficient_funds_changes_nothing(self):
        exam = self.create_exam()
        self.wallet.balance = Decimal("100.00")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(reverse("exam-registration", kwargs={"exam_id": exam.id}))

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.wallet.balance, Decimal("100.00"))
        self.assertFalse(ExamRegistration.objects.filter(exam=exam).exists())
        self.assertFalse(Transaction.objects.exists())

    def test_student_can_cancel_registration_and_receive_refund(self):
        registration = self.create_paid_registration()
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(
            reverse(
                "exam-registration-cancel",
                kwargs={"registration_id": registration.id},
            )
        )

        registration.refresh_from_db()
        self.wallet.refresh_from_db()
        refund = Transaction.objects.get(cause=TransactionCause.EXAM_REFUND)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(registration.status, ExamRegistrationStatus.CANCELED)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))
        self.assertEqual(refund.amount, Decimal("200.00"))

    def test_student_can_reregister_after_canceling_and_cancel_again(self):
        exam = self.create_exam()
        self.client.force_authenticate(user=self.student_user)

        first_registration = self.client.post(
            reverse("exam-registration", kwargs={"exam_id": exam.id})
        )
        first_cancellation = self.client.post(
            reverse(
                "exam-registration-cancel",
                kwargs={"registration_id": first_registration.data["id"]},
            )
        )
        available_exams = self.client.get(reverse("available-exams"))
        second_registration = self.client.post(
            reverse("exam-registration", kwargs={"exam_id": exam.id})
        )
        second_cancellation = self.client.post(
            reverse(
                "exam-registration-cancel",
                kwargs={"registration_id": second_registration.data["id"]},
            )
        )

        self.wallet.refresh_from_db()
        self.assertEqual(first_registration.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first_cancellation.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in available_exams.data], [exam.id])
        self.assertEqual(second_registration.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_cancellation.status_code, status.HTTP_200_OK)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))
        self.assertNotEqual(first_registration.data["id"], second_registration.data["id"])
        for registration_id in (
            first_registration.data["id"],
            second_registration.data["id"],
        ):
            self.assertEqual(
                Transaction.objects.filter(
                    exam_registration_id=registration_id,
                    cause=TransactionCause.EXAM_REGISTRATION,
                ).count(),
                1,
            )
            self.assertEqual(
                Transaction.objects.filter(
                    exam_registration_id=registration_id,
                    cause=TransactionCause.EXAM_REFUND,
                ).count(),
                1,
            )

    def test_cancellation_rolls_back_when_refund_fails(self):
        registration = self.create_paid_registration()

        with patch(
            "exams.services.credit_wallet",
            side_effect=ValueError("Refund failed."),
        ):
            with self.assertRaises(ValueError):
                cancel_exam_registration(
                    student=self.student,
                    registration=registration,
                )

        registration.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
        self.assertFalse(Transaction.objects.filter(cause=TransactionCause.EXAM_REFUND).exists())

    def test_professor_can_list_exam_registrations(self):
        exam = self.create_exam()
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=exam,
        )
        ExamRegistration.objects.create(
            student=self.student,
            exam=exam,
            status=ExamRegistrationStatus.CANCELED,
        )
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.get(
            reverse("professor-exam-registrations", kwargs={"exam_id": exam.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [registration.id])
        self.assertEqual(response.data[0]["student_index_no"], self.student.index_no)

    def test_professor_can_grade_and_correct_registration(self):
        exam = self.create_exam(days_from_now=-1)
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=exam,
        )
        url = reverse(
            "exam-registration-grade",
            kwargs={"registration_id": registration.id},
        )
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(url, {"grade": 8}, format="json")
        correction_response = self.client.patch(url, {"grade": 9}, format="json")

        registration.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(correction_response.status_code, status.HTTP_200_OK)
        self.assertEqual(registration.grade, 9)
        self.assertEqual(registration.status, ExamRegistrationStatus.GRADED)

    def test_professor_cannot_grade_unfinished_exam(self):
        exam = self.create_exam()
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=exam,
        )
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(
            reverse(
                "exam-registration-grade",
                kwargs={"registration_id": registration.id},
            ),
            {"grade": 8},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_professor_cannot_grade_another_professors_exam(self):
        other_user = User.objects.create_user(
            email="other-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        other_professor = ProfessorProfile.objects.create(
            user=other_user,
            employee_no="PROF-002",
        )
        other_course = Course.objects.create(
            code="COURSE-002",
            name="Other Course",
            espb=6,
            professor=other_professor,
        )
        exam = Exam.objects.create(
            course=other_course,
            professor=other_professor,
            date=timezone.now() - timedelta(days=1),
        )
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=exam,
        )
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(
            reverse(
                "exam-registration-grade",
                kwargs={"registration_id": registration.id},
            ),
            {"grade": 8},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_professor_can_create_exam(self):
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.post(
            reverse("exams"),
            {
                "course_code": self.course.code,
                "date": (timezone.now() + timedelta(days=30)).isoformat(),
                "room": "S1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exam = Exam.objects.get(pk=response.data["id"])
        self.assertEqual(exam.course, self.course)
        self.assertEqual(exam.professor, self.professor)

    def test_student_exam_overview(self):
        now = timezone.now()
        available_exam = self.create_exam(days_from_now=7)
        cancellable_exam = self.create_exam(days_from_now=8)
        cancellable = ExamRegistration.objects.create(
            student=self.student,
            exam=cancellable_exam,
        )
        failed = ExamRegistration.objects.create(
            student=self.student,
            exam=Exam.objects.create(
                course=self.course,
                professor=self.professor,
                date=now - timedelta(days=20),
            ),
            grade=5,
            status=ExamRegistrationStatus.GRADED,
        )
        passed = ExamRegistration.objects.create(
            student=self.student,
            exam=Exam.objects.create(
                course=self.course,
                professor=self.professor,
                date=now - timedelta(days=10),
            ),
            grade=9,
            status=ExamRegistrationStatus.GRADED,
        )
        self.wallet.balance = Decimal("100.00")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user=self.student_user)

        available_response = self.client.get(reverse("available-exams"))
        cancellable_response = self.client.get(reverse("cancellable-exam-registrations"))
        results_response = self.client.get(reverse("current-student-results"))
        history_response = self.client.get(reverse("current-student-exam-registrations"))

        self.assertEqual(
            [item["id"] for item in available_response.data],
            [available_exam.id],
        )
        self.assertFalse(available_response.data[0]["can_afford"])
        self.assertEqual(
            [item["id"] for item in cancellable_response.data],
            [cancellable.id],
        )
        self.assertEqual(results_response.data["average"], "9.00")
        self.assertEqual(
            [item["id"] for item in history_response.data],
            [cancellable.id, passed.id, failed.id],
        )
