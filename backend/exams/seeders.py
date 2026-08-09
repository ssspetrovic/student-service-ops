from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from academics.models import Course
from accounts.models import StudentProfile
from exams.management.test_data import TEST_EXAM_REGISTRATIONS, TEST_EXAMS
from exams.models import Exam, ExamRegistration
from exams.services import (
    EXAM_REGISTRATION_FEE,
    cancel_exam_registration,
    grade_exam_registration,
    is_registration_open,
    register_student_for_exam,
)
from finance.models import TransactionCause
from finance.services import debit_wallet


@dataclass
class ExamSeedData:
    exams: list[Exam]
    registrations: list[ExamRegistration]


def seed_exams(
    courses: list[Course],
    students: list[StudentProfile],
) -> ExamSeedData:
    courses_by_code = {course.code: course for course in courses}
    students_by_email = {student.user.email: student for student in students}
    exams = []
    registrations = []

    for exam_data in TEST_EXAMS:
        course = courses_by_code[exam_data["course_code"]]
        exam = Exam(
            course=course,
            professor=course.professor,
            date=exam_date(
                days_from_now=exam_data["days_from_now"],
                hour=exam_data["hour"],
                minute=exam_data["minute"],
            ),
            room=exam_data["room"],
        )
        exam.full_clean()
        exam.save()
        exams.append(exam)

    exams_by_key = {
        exam_data["key"]: exam for exam_data, exam in zip(TEST_EXAMS, exams, strict=True)
    }

    for registration_data in TEST_EXAM_REGISTRATIONS:
        student = students_by_email[registration_data["student_email"]]
        exam = exams_by_key[registration_data["exam_key"]]
        registration = add_registration(student=student, exam=exam)
        if "grade" in registration_data:
            registration = grade_exam_registration(
                professor=exam.professor,
                registration=registration,
                grade=registration_data["grade"],
            )
        if registration_data.get("canceled"):
            registration = cancel_exam_registration(student=student, registration=registration)
        registrations.append(registration)

    return ExamSeedData(exams=exams, registrations=registrations)


def add_registration(student: StudentProfile, exam: Exam) -> ExamRegistration:
    if is_registration_open(exam):
        return register_student_for_exam(student=student, exam=exam)

    registration = ExamRegistration.objects.create(student=student, exam=exam)
    debit_wallet(
        student=student,
        amount=EXAM_REGISTRATION_FEE,
        cause=TransactionCause.EXAM_REGISTRATION,
        exam_registration=registration,
    )
    return registration


def exam_date(days_from_now: int, hour: int, minute: int):
    exam_date = timezone.now() + timedelta(days=days_from_now)
    return exam_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
