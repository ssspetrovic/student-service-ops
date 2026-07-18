from decimal import Decimal
from datetime import timedelta

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
    ExamRegistrationPaymentError,
    RegistrationPeriodClosedError,
    StudentNotEnrolledError,
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
        self.assertEqual(self.wallet.balance, Decimal("500.00"))

    def test_insufficient_funds_returns_bad_request_and_rolls_back(self):
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
        self.assertFalse(
            ExamRegistration.objects.filter(
                student=self.student,
                exam=self.exam,
            ).exists()
        )
        self.assertEqual(self.wallet.balance, Decimal("100.00"))

    def test_professor_cannot_register_for_exam(self):
        self.client.force_authenticate(user=self.professor_user)

        response = self.client.post(self.register_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
