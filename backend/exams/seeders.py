from dataclasses import dataclass

from academics.models import Course
from accounts.models import ProfessorProfile, StudentProfile
from exams.management.test_data import TEST_EXAMS
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
    exams = []
    registrations = []

    for exam_data in TEST_EXAMS:
        course = courses_by_code[exam_data["course_code"]]
        exam = create_or_update_exam(
            course=course,
            professor=course.professor,
            date=exam_data["date"],
            room=exam_data["room"],
        )
        exams.append(exam)

    for student, exam in zip(students, exams, strict=True):
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


def create_or_update_exam(course: Course, professor: ProfessorProfile, date, room: str) -> Exam:
    exam, _ = Exam.objects.update_or_create(
        course=course,
        professor=professor,
        date=date,
        defaults={
            "room": room,
        },
    )
    return exam
