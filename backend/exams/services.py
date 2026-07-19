from decimal import Decimal
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import StudentProfile
from academics.models import Enrollment, EnrollmentStatus
from exams.models import Exam, ExamRegistration, ExamRegistrationStatus
from finance.models import Transaction, TransactionCause
from finance.services import credit_wallet, debit_wallet, InsufficientFundsError

EXAM_REGISTRATION_FEE = Decimal("200.00")
REGISTRATION_OPENS_BEFORE_DAYS = 14
REGISTRATION_CLOSES_BEFORE_DAYS = 2
CANCELLATION_CLOSES_BEFORE_HOURS = 48


class ExamRegistrationError(ValueError):
    """Base exception for expected exam registration failures."""


class StudentNotEnrolledError(ExamRegistrationError):
    pass


class RegistrationPeriodClosedError(ExamRegistrationError):
    pass


class AlreadyRegisteredError(ExamRegistrationError):
    pass


class ExamRegistrationPaymentError(ExamRegistrationError):
    pass


class ExamRegistrationCancellationClosedError(ExamRegistrationError):
    pass


class ExamRegistrationNotActiveError(ExamRegistrationError):
    pass


class ExamRegistrationOwnershipError(ExamRegistrationError):
    pass


class ExamRegistrationRefundError(ExamRegistrationError):
    pass


def is_registration_open(exam: Exam) -> bool:
    registration_opens = exam.date - timedelta(days=REGISTRATION_OPENS_BEFORE_DAYS)
    registration_closes = exam.date - timedelta(days=REGISTRATION_CLOSES_BEFORE_DAYS)

    if registration_opens >= registration_closes:
        raise ValueError("Registration opening must be before its closing.")

    return registration_opens <= timezone.now() < registration_closes


def can_cancel_registration(registration: ExamRegistration) -> bool:
    cancellation_deadline = registration.exam.date - timedelta(
        hours=CANCELLATION_CLOSES_BEFORE_HOURS
    )
    return timezone.now() <= cancellation_deadline


@transaction.atomic
def register_student_for_exam(
    student: StudentProfile,
    exam: Exam,
) -> ExamRegistration:
    is_enrolled = Enrollment.objects.filter(
        student=student,
        course=exam.course,
        status=EnrollmentStatus.ACTIVE,
    ).exists()

    if not is_enrolled:
        raise StudentNotEnrolledError(f"Student is not enrolled in course '{exam.course.name}'.")

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

    try:
        debit_wallet(
            student=student,
            amount=EXAM_REGISTRATION_FEE,
            cause=TransactionCause.EXAM_REGISTRATION,
            exam_registration=registration,
        )
    except InsufficientFundsError as e:
        raise ExamRegistrationPaymentError(str(e)) from e

    return registration


@transaction.atomic
def cancel_exam_registration(
    student: StudentProfile, registration: ExamRegistration
) -> ExamRegistration:
    registration = (
        ExamRegistration.objects.select_for_update().select_related("exam").get(pk=registration.pk)
    )

    if registration.student_id != student.pk:
        raise ExamRegistrationOwnershipError("Registration does not belong to this student.")

    if registration.status != ExamRegistrationStatus.ACTIVE:
        raise ExamRegistrationNotActiveError("Only active registrations can be canceled.")

    if not can_cancel_registration(registration):
        raise ExamRegistrationCancellationClosedError("Registration can no longer be canceled.")

    payment_transaction = Transaction.objects.filter(
        student=student,
        exam_registration=registration,
        cause=TransactionCause.EXAM_REGISTRATION,
    ).first()

    if payment_transaction is None:
        raise ExamRegistrationRefundError(
            "The original exam registration payment could not be found."
        )

    registration.status = ExamRegistrationStatus.CANCELED
    registration.save(update_fields=["status"])

    credit_wallet(
        student=student,
        amount=payment_transaction.amount,
        cause=TransactionCause.EXAM_REFUND,
        exam_registration=registration,
    )

    return registration
