from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from academics.models import Course
from accounts.models import ProfessorProfile, StudentProfile
from exams.management.test_data import TEST_EXAM_REGISTRATIONS, TEST_EXAMS
from exams.models import Exam, ExamRegistration, ExamRegistrationStatus


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
        exam = create_or_update_exam(
            course=course,
            professor=course.professor,
            date=get_seed_exam_date(
                days_until_exam=exam_data["days_until_exam"],
                hour=exam_data["hour"],
                minute=exam_data["minute"],
            ),
            room=exam_data["room"],
        )
        exams.append(exam)

    exams_by_course_code = {exam.course.code: exam for exam in exams}

    for registration_data in TEST_EXAM_REGISTRATIONS:
        student = students_by_email[registration_data["student_email"]]
        exam = exams_by_course_code[registration_data["course_code"]]
        registration, _ = ExamRegistration.objects.update_or_create(
            student=student,
            exam=exam,
            defaults={
                "grade": None,
                "status": ExamRegistrationStatus.ACTIVE,
            },
        )
        registrations.append(registration)

    return ExamSeedData(exams=exams, registrations=registrations)


def get_seed_exam_date(days_until_exam: int, hour: int, minute: int):
    exam_date = timezone.now() + timedelta(days=days_until_exam)
    return exam_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def create_or_update_exam(course: Course, professor: ProfessorProfile, date, room: str) -> Exam:
    exam = Exam.objects.filter(course=course).order_by("id").first()

    if exam is None:
        exam = Exam(course=course)

    exam.professor = professor
    exam.date = date
    exam.room = room
    exam.full_clean()
    exam.save()

    return exam
