from decimal import Decimal
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import ProfessorProfile, StudentProfile
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


class ExamGradingError(ValueError):
    """Base exception for expected exam grading failures."""


class ExamGradingOwnershipError(ExamGradingError):
    pass


class ExamNotFinishedError(ExamGradingError):
    pass


class ExamRegistrationNotGradableError(ExamGradingError):
    pass


class InvalidExamGradeError(ExamGradingError):
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

    try:
        payment_transaction = Transaction.objects.get(
            student=student,
            exam_registration=registration,
            cause=TransactionCause.EXAM_REGISTRATION,
        )
    except Transaction.DoesNotExist as e:
        raise ExamRegistrationRefundError(
            "The original exam registration payment could not be found."
        ) from e
    except Transaction.MultipleObjectsReturned as e:
        raise ExamRegistrationRefundError(
            "Multiple exam registration payments were found."
        ) from e

    registration.status = ExamRegistrationStatus.CANCELED
    registration.save(update_fields=["status"])

    credit_wallet(
        student=student,
        amount=payment_transaction.amount,
        cause=TransactionCause.EXAM_REFUND,
        exam_registration=registration,
    )

    return registration


@transaction.atomic
def grade_exam_registration(
    professor: ProfessorProfile,
    registration: ExamRegistration,
    grade: int,
) -> ExamRegistration:
    registration = (
        ExamRegistration.objects.select_for_update()
        .select_related("exam__course", "student__user")
        .get(pk=registration.pk)
    )

    if registration.exam.professor_id != professor.pk:
        raise ExamGradingOwnershipError("Professor is not responsible for this exam.")

    if registration.exam.date >= timezone.now():
        raise ExamNotFinishedError("The exam has not finished yet.")

    if registration.status == ExamRegistrationStatus.CANCELED:
        raise ExamRegistrationNotGradableError("Canceled registrations cannot be graded.")

    if not 5 <= grade <= 10:
        raise InvalidExamGradeError("Grade must be between 5 and 10.")

    registration.grade = grade
    registration.status = ExamRegistrationStatus.GRADED
    registration.save(update_fields=["grade", "status"])

    return registration
