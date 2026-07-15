from decimal import Decimal
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import StudentProfile
from academics.models import Enrollment, EnrollmentStatus
from exams.models import Exam, ExamRegistration, ExamRegistrationStatus
from finance.models import TransactionCause
from finance.services import debit_wallet

EXAM_REGISTRATION_FEE = Decimal("200.00")


REGISTRATION_OPENS_BEFORE_DAYS = 14
REGISTRATION_CLOSES_BEFORE_DAYS = 2


class ExamRegistrationError(ValueError):
    """Base exception for expected exam registration failures."""


class StudentNotEnrolledError(ExamRegistrationError):
    pass


class RegistrationPeriodClosedError(ExamRegistrationError):
    pass


class AlreadyRegisteredError(ExamRegistrationError):
    pass


def is_registration_open(exam: Exam) -> bool:
    registration_opens = exam.date - timedelta(days=REGISTRATION_OPENS_BEFORE_DAYS)
    registration_closes = exam.date - timedelta(days=REGISTRATION_CLOSES_BEFORE_DAYS)

    if registration_opens >= registration_closes:
        raise ValueError("Registration opening must be before its closing.")

    return registration_opens <= timezone.now() < registration_closes


@transaction.atomic
def register_student_for_exam(student: StudentProfile, exam: Exam) -> ExamRegistration:
    is_enrolled = Enrollment.objects.filter(
        student=student, course=exam.course, status=EnrollmentStatus.ACTIVE
    ).exists()

    if not is_enrolled:
        raise StudentNotEnrolledError(
            f"Student is not enrolled in course '{exam.course.name}'."
        )

    if not is_registration_open(exam):
        raise RegistrationPeriodClosedError("Registration period is not active.")

    registration, was_created = ExamRegistration.objects.get_or_create(
        student=student,
        exam=exam,
        defaults={
            "grade": None,
            "status": ExamRegistrationStatus.ACTIVE,
        },
    )

    if not was_created:
        raise AlreadyRegisteredError("Student is already registered for this exam.")

    debit_wallet(
        student=student,
        amount=EXAM_REGISTRATION_FEE,
        cause=TransactionCause.EXAM_REGISTRATION,
        exam_registration=registration,
    )

    return registration
