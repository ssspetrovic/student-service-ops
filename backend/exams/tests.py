from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from academics.models import Course, Enrollment, EnrollmentStatus
from accounts.models import ProfessorProfile, StudentProfile, User, UserRole
from finance.models import Transaction, TransactionCause, Wallet
from .models import Exam, ExamRegistration, ExamRegistrationStatus
from .services import (
    AlreadyRegisteredError,
    ExamRegistrationCancellationClosedError,
    ExamRegistrationNotActiveError,
    ExamRegistrationPaymentError,
    ExamRegistrationRefundError,
    RegistrationPeriodClosedError,
    StudentNotEnrolledError,
    cancel_exam_registration,
    register_student_for_exam,
)

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
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="PROF-001",
        )

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

    def test_exam_registration_rejects_grade_below_min(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExamRegistration.objects.create(
                    student=self.student,
                    exam=self.exam,
                    grade=4,
                )

    def test_exam_registration_rejects_duplicate_student_exam(self):
        ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExamRegistration.objects.create(
                    student=self.student,
                    exam=self.exam,
                )


class ExamProfessorValidationTestCase(TestCase):
    def setUp(self):
        self.professor_user = User.objects.create_user(
            email="professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="PROF-003",
        )
        self.other_professor_user = User.objects.create_user(
            email="other-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.other_professor = ProfessorProfile.objects.create(
            user=self.other_professor_user,
            employee_no="PROF-002",
        )
        self.course = Course.objects.create(
            code="TCOURSE",
            name="Test Course",
            espb=60,
            professor=self.professor,
        )

    def test_exam_rejects_professor_not_responsible_for_course(self):
        exam = Exam(
            course=self.course,
            professor=self.other_professor,
            date=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            exam.full_clean()


class ExamRegistrationServiceTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            email="registration-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            index_no="REG-001",
        )

        self.professor_user = User.objects.create_user(
            email="registration-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="REG-PROF-001",
        )

        self.course = Course.objects.create(
            code="REG-COURSE",
            name="Registration Course",
            espb=6,
            professor=self.professor,
        )
        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.wallet = Wallet.objects.create(
            student=self.student,
            balance=Decimal("500.00"),
        )

    def enroll_student(self, status=EnrollmentStatus.ACTIVE):
        return Enrollment.objects.create(
            student=self.student,
            course=self.course,
            school_year="2026/2027",
            semester=1,
            status=status,
        )

    def assert_no_registration_or_payment(self):
        self.assertFalse(
            ExamRegistration.objects.filter(
                student=self.student,
                exam=self.exam,
            ).exists()
        )
        self.assertFalse(
            Transaction.objects.filter(
                student=self.student,
                cause=TransactionCause.EXAM_REGISTRATION,
            ).exists()
        )

    def test_register_student_for_exam_creates_registration_and_debits_wallet(self):
        self.enroll_student()

        registration = register_student_for_exam(
            student=self.student,
            exam=self.exam,
        )

        registration.refresh_from_db()
        self.wallet.refresh_from_db()
        transaction_record = Transaction.objects.get(
            student=self.student,
            cause=TransactionCause.EXAM_REGISTRATION,
            exam_registration=registration,
        )

        self.assertEqual(registration.student, self.student)
        self.assertEqual(registration.exam, self.exam)
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)
        self.assertIsNone(registration.grade)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
        self.assertEqual(transaction_record.student, self.student)
        self.assertEqual(transaction_record.amount, Decimal("200.00"))
        self.assertEqual(transaction_record.cause, TransactionCause.EXAM_REGISTRATION)
        self.assertEqual(transaction_record.exam_registration, registration)

    def test_register_student_for_exam_rejects_duplicate_without_debiting_wallet(self):
        self.enroll_student()
        ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )

        with self.assertRaises(AlreadyRegisteredError):
            register_student_for_exam(
                student=self.student,
                exam=self.exam,
            )

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("500.00"))
        self.assertFalse(
            Transaction.objects.filter(
                student=self.student,
                cause=TransactionCause.EXAM_REGISTRATION,
            ).exists()
        )

    def test_register_student_for_exam_rejects_student_not_enrolled(self):
        with self.assertRaises(StudentNotEnrolledError):
            register_student_for_exam(
                student=self.student,
                exam=self.exam,
            )

        self.wallet.refresh_from_db()
        self.assert_no_registration_or_payment()
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

    def test_register_student_for_exam_rejects_before_opening_window(self):
        self.enroll_student()
        self.exam.date = timezone.now() + timedelta(days=45)
        self.exam.save(update_fields=["date"])

        with self.assertRaises(RegistrationPeriodClosedError):
            register_student_for_exam(
                student=self.student,
                exam=self.exam,
            )

        self.wallet.refresh_from_db()
        self.assert_no_registration_or_payment()
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

    def test_register_student_for_exam_rejects_inside_final_lock_window(self):
        self.enroll_student()
        self.exam.date = timezone.now() + timedelta(days=1)
        self.exam.save(update_fields=["date"])

        with self.assertRaises(RegistrationPeriodClosedError):
            register_student_for_exam(
                student=self.student,
                exam=self.exam,
            )

        self.wallet.refresh_from_db()
        self.assert_no_registration_or_payment()
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

    def test_register_student_for_exam_rolls_back_when_student_has_insufficient_funds(self):
        self.enroll_student()
        self.wallet.balance = Decimal("100.00")
        self.wallet.save(update_fields=["balance"])

        with self.assertRaises(ExamRegistrationPaymentError):
            register_student_for_exam(
                student=self.student,
                exam=self.exam,
            )

        self.wallet.refresh_from_db()
        self.assert_no_registration_or_payment()
        self.assertEqual(self.wallet.balance, Decimal("100.00"))


class ExamRegistrationCancellationServiceTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            email="cancel-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            index_no="CANCEL-001",
        )
        self.professor_user = User.objects.create_user(
            email="cancel-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="CANCEL-PROF-001",
        )
        self.course = Course.objects.create(
            code="CANCEL-COURSE",
            name="Cancellation Course",
            espb=6,
            professor=self.professor,
        )
        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.wallet = Wallet.objects.create(
            student=self.student,
            balance=Decimal("300.00"),
        )

    def create_paid_registration(self, status=ExamRegistrationStatus.ACTIVE):
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
            status=status,
        )
        payment_transaction = Transaction.objects.create(
            student=self.student,
            amount=Decimal("200.00"),
            cause=TransactionCause.EXAM_REGISTRATION,
            exam_registration=registration,
        )
        return registration, payment_transaction

    def assert_no_refund_was_created(self):
        self.assertFalse(
            Transaction.objects.filter(
                student=self.student,
                cause=TransactionCause.EXAM_REFUND,
            ).exists()
        )

    def test_cancel_exam_registration_refunds_original_payment_amount(self):
        registration, payment_transaction = self.create_paid_registration()

        canceled_registration = cancel_exam_registration(
            student=self.student,
            registration=registration,
        )

        canceled_registration.refresh_from_db()
        self.wallet.refresh_from_db()
        payment_transaction.refresh_from_db()
        refund_transaction = Transaction.objects.get(
            student=self.student,
            cause=TransactionCause.EXAM_REFUND,
            exam_registration=registration,
        )

        self.assertEqual(canceled_registration.status, ExamRegistrationStatus.CANCELED)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))
        self.assertEqual(refund_transaction.amount, payment_transaction.amount)
        self.assertEqual(payment_transaction.cause, TransactionCause.EXAM_REGISTRATION)

    def test_cancel_exam_registration_rejects_inside_final_lock_window(self):
        registration, _ = self.create_paid_registration()
        self.exam.date = timezone.now() + timedelta(days=1)
        self.exam.save(update_fields=["date"])

        with self.assertRaises(ExamRegistrationCancellationClosedError):
            cancel_exam_registration(
                student=self.student,
                registration=registration,
            )

        registration.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
        self.assert_no_refund_was_created()

    def test_cancel_exam_registration_rejects_missing_original_payment(self):
        registration = ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )

        with self.assertRaises(ExamRegistrationRefundError):
            cancel_exam_registration(
                student=self.student,
                registration=registration,
            )

        registration.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
        self.assert_no_refund_was_created()

    def test_cancel_exam_registration_rejects_multiple_original_payments(self):
        registration, _ = self.create_paid_registration()
        Transaction.objects.create(
            student=self.student,
            amount=Decimal("250.00"),
            cause=TransactionCause.EXAM_REGISTRATION,
            exam_registration=registration,
        )

        with self.assertRaises(ExamRegistrationRefundError):
            cancel_exam_registration(
                student=self.student,
                registration=registration,
            )

        registration.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(registration.status, ExamRegistrationStatus.ACTIVE)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
        self.assert_no_refund_was_created()

    def test_cancel_exam_registration_rolls_back_status_when_refund_fails(self):
        registration, _ = self.create_paid_registration()

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
        self.assert_no_refund_was_created()

    def test_cancel_exam_registration_does_not_refund_twice(self):
        registration, _ = self.create_paid_registration()

        cancel_exam_registration(
            student=self.student,
            registration=registration,
        )

        with self.assertRaises(ExamRegistrationNotActiveError):
            cancel_exam_registration(
                student=self.student,
                registration=registration,
            )

        registration.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(registration.status, ExamRegistrationStatus.CANCELED)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))
        self.assertEqual(
            Transaction.objects.filter(
                student=self.student,
                cause=TransactionCause.EXAM_REFUND,
                exam_registration=registration,
            ).count(),
            1,
        )


class ExamRegistrationApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(
            email="api-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            index_no="API-001",
        )
        self.professor_user = User.objects.create_user(
            email="api-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="API-PROF-001",
        )
        self.course = Course.objects.create(
            code="API-COURSE",
            name="API Course",
            espb=6,
            professor=self.professor,
        )
        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.wallet = Wallet.objects.create(
            student=self.student,
            balance=Decimal("500.00"),
        )
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            school_year="2026/2027",
            semester=1,
            status=EnrollmentStatus.ACTIVE,
        )

    def register_url(self):
        return reverse("exam-registration", kwargs={"exam_id": self.exam.id})

    def test_student_can_register_for_exam(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(self.register_url())

        self.wallet.refresh_from_db()
        registration = ExamRegistration.objects.get(
            student=self.student,
            exam=self.exam,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], registration.id)
        self.assertEqual(response.data["exam_id"], self.exam.id)
        self.assertEqual(self.wallet.balance, Decimal("300.00"))

    def test_duplicate_registration_returns_bad_request(self):
        ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(self.register_url())

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Student is already registered for this exam.",
        )

    def test_insufficient_funds_returns_bad_request(self):
        self.wallet.balance = Decimal("100.00")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(self.register_url())

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Student does not have enough funds to register for this exam.",
        )

    def test_professor_cannot_register_for_exam(self):
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.post(self.register_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ExamRegistrationCancellationApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(
            email="cancel-api-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            index_no="CANCEL-API-001",
        )
        self.other_student_user = User.objects.create_user(
            email="cancel-api-other-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.other_student = StudentProfile.objects.create(
            user=self.other_student_user,
            index_no="CANCEL-API-002",
        )
        self.professor_user = User.objects.create_user(
            email="cancel-api-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="CANCEL-API-PROF-001",
        )
        self.course = Course.objects.create(
            code="CANCEL-API-COURSE",
            name="Cancellation API Course",
            espb=6,
            professor=self.professor,
        )
        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.wallet = Wallet.objects.create(
            student=self.student,
            balance=Decimal("300.00"),
        )
        self.registration = ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )
        Transaction.objects.create(
            student=self.student,
            amount=Decimal("200.00"),
            cause=TransactionCause.EXAM_REGISTRATION,
            exam_registration=self.registration,
        )

    def cancel_url(self, registration=None):
        registration = registration or self.registration
        return reverse(
            "exam-registration-cancel",
            kwargs={"registration_id": registration.id},
        )

    def test_student_can_cancel_own_registration(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(self.cancel_url())

        self.registration.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.registration.id)
        self.assertEqual(response.data["status"], ExamRegistrationStatus.CANCELED)
        self.assertEqual(self.registration.status, ExamRegistrationStatus.CANCELED)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

    def test_professor_cannot_cancel_registration(self):
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.post(self.cancel_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_another_student_cannot_cancel_registration(self):
        self.client.force_authenticate(user=self.other_student_user)

        response = self.client.post(self.cancel_url())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_expected_cancellation_error_returns_bad_request(self):
        self.registration.status = ExamRegistrationStatus.CANCELED
        self.registration.save(update_fields=["status"])
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(self.cancel_url())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Only active registrations can be canceled.")


class ProfessorExamRegistrationListApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor_user = User.objects.create_user(
            email="list-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="LIST-PROF-001",
        )
        self.other_professor_user = User.objects.create_user(
            email="other-list-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.other_professor = ProfessorProfile.objects.create(
            user=self.other_professor_user,
            employee_no="LIST-PROF-002",
        )
        self.student_user = User.objects.create_user(
            email="list-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
            first_name="List",
            last_name="Student",
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            index_no="LIST-001",
        )
        self.course = Course.objects.create(
            code="LIST-COURSE",
            name="List Course",
            espb=6,
            professor=self.professor,
        )
        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() + timedelta(days=10),
        )
        self.registration = ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )

    def registrations_url(self, exam=None):
        exam = exam or self.exam
        return reverse(
            "professor-exam-registrations",
            kwargs={"exam_id": exam.id},
        )

    def test_professor_can_list_registrations_for_own_exam(self):
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.get(self.registrations_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.registration.id)
        self.assertEqual(response.data[0]["student_index_no"], self.student.index_no)
        self.assertEqual(response.data[0]["student_name"], "List Student")

    def test_professor_cannot_list_registrations_for_another_professors_exam(self):
        self.client.force_authenticate(user=self.other_professor_user)

        response = self.client.get(self.registrations_url())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_list_professor_exam_registrations(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.get(self.registrations_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ExamRegistrationGradeApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor_user = User.objects.create_user(
            email="grade-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="GRADE-PROF-001",
        )
        self.other_professor_user = User.objects.create_user(
            email="other-grade-professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        ProfessorProfile.objects.create(
            user=self.other_professor_user,
            employee_no="GRADE-PROF-002",
        )
        self.student_user = User.objects.create_user(
            email="grade-student@example.com",
            password="student123",
            role=UserRole.STUDENT,
            first_name="Grade",
            last_name="Student",
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            index_no="GRADE-001",
        )
        self.course = Course.objects.create(
            code="GRADE-COURSE",
            name="Grading Course",
            espb=6,
            professor=self.professor,
        )
        self.exam = Exam.objects.create(
            course=self.course,
            professor=self.professor,
            date=timezone.now() - timedelta(days=1),
        )
        self.registration = ExamRegistration.objects.create(
            student=self.student,
            exam=self.exam,
        )

    def grade_url(self):
        return reverse(
            "exam-registration-grade",
            kwargs={"registration_id": self.registration.id},
        )

    def test_professor_can_grade_and_correct_registration(self):
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(self.grade_url(), {"grade": 8}, format="json")

        self.registration.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["grade"], 8)
        self.assertEqual(response.data["status"], ExamRegistrationStatus.GRADED)
        self.assertEqual(self.registration.grade, 8)
        self.assertEqual(self.registration.status, ExamRegistrationStatus.GRADED)

        correction_response = self.client.patch(
            self.grade_url(),
            {"grade": 9},
            format="json",
        )

        self.registration.refresh_from_db()
        self.assertEqual(correction_response.status_code, status.HTTP_200_OK)
        self.assertEqual(correction_response.data["grade"], 9)
        self.assertEqual(correction_response.data["status"], ExamRegistrationStatus.GRADED)
        self.assertEqual(correction_response.data["student_name"], "Grade Student")
        self.assertEqual(self.registration.grade, 9)
        self.assertEqual(self.registration.status, ExamRegistrationStatus.GRADED)

    def test_professor_cannot_grade_unfinished_exam(self):
        self.exam.date = timezone.now() + timedelta(days=1)
        self.exam.save(update_fields=["date"])
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(self.grade_url(), {"grade": 8}, format="json")

        self.registration.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "The exam has not finished yet.")
        self.assertIsNone(self.registration.grade)
        self.assertEqual(self.registration.status, ExamRegistrationStatus.ACTIVE)

    def test_professor_cannot_grade_canceled_registration(self):
        self.registration.status = ExamRegistrationStatus.CANCELED
        self.registration.save(update_fields=["status"])
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(self.grade_url(), {"grade": 8}, format="json")

        self.registration.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Canceled registrations cannot be graded.")
        self.assertIsNone(self.registration.grade)
        self.assertEqual(self.registration.status, ExamRegistrationStatus.CANCELED)

    def test_grade_must_be_in_valid_range(self):
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.patch(self.grade_url(), {"grade": 11}, format="json")

        self.registration.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(self.registration.grade)

    def test_another_professor_cannot_grade_registration(self):
        self.client.force_authenticate(user=self.other_professor_user)

        response = self.client.patch(self.grade_url(), {"grade": 8}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_grade_registration(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.patch(self.grade_url(), {"grade": 8}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
