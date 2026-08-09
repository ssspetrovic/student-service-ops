from dataclasses import dataclass

from django.db.models import Q

from accounts.management.test_data import TEST_PROFESSORS, TEST_STUDENTS
from accounts.models import ProfessorProfile, StudentProfile, User, UserRole
from academics.management.test_data import (
    CURRICULUM_CODE,
    CURRICULUM_DURATION,
    CURRICULUM_NAME,
    TEST_COURSES,
)
from academics.models import Curriculum, DegreeLevel
from academics.models import Course, CurriculumCourse, Enrollment
from exams.models import Exam, ExamRegistration
from finance.models import Transaction, Wallet


@dataclass
class AccountSeedData:
    students: list[StudentProfile]
    professors: list[ProfessorProfile]


def clear_demo() -> None:
    """Remove only records owned by the local demo users or demo courses."""
    demo_emails = [student["email"] for student in TEST_STUDENTS] + [
        professor["email"] for professor in TEST_PROFESSORS
    ]
    demo_course_codes = [course["code"] for course in TEST_COURSES]
    registrations = ExamRegistration.objects.filter(
        Q(student__user__email__in=demo_emails) | Q(exam__course__code__in=demo_course_codes)
    )
    registration_ids = list(registrations.values_list("pk", flat=True))

    Transaction.objects.filter(
        Q(student__user__email__in=demo_emails) | Q(exam_registration_id__in=registration_ids)
    ).delete()
    registrations.delete()
    Wallet.objects.filter(student__user__email__in=demo_emails).delete()
    Enrollment.objects.filter(
        Q(student__user__email__in=demo_emails) | Q(course__code__in=demo_course_codes)
    ).delete()
    Exam.objects.filter(course__code__in=demo_course_codes).delete()
    CurriculumCourse.objects.filter(course__code__in=demo_course_codes).delete()
    Course.objects.filter(code__in=demo_course_codes).delete()
    User.objects.filter(email__in=demo_emails).delete()


def seed_accounts() -> AccountSeedData:
    students = []
    professors = []
    curriculum, _ = Curriculum.objects.update_or_create(
        code=CURRICULUM_CODE,
        defaults={
            "name": CURRICULUM_NAME,
            "degree_level": DegreeLevel.BACHELOR,
            "duration": CURRICULUM_DURATION,
        },
    )

    for student_data in TEST_STUDENTS:
        student_user = create_or_update_user(
            email=student_data["email"],
            password=student_data["password"],
            role=UserRole.STUDENT,
            first_name=student_data["first_name"],
            last_name=student_data["last_name"],
        )
        student, _ = StudentProfile.objects.update_or_create(
            user=student_user,
            defaults={
                "index_no": student_data["index_no"],
                "current_year_of_study": student_data["current_year_of_study"],
                "curriculum": curriculum,
            },
        )
        students.append(student)

    for professor_data in TEST_PROFESSORS:
        professor_user = create_or_update_user(
            email=professor_data["email"],
            password=professor_data["password"],
            role=UserRole.PROFESSOR,
            first_name=professor_data["first_name"],
            last_name=professor_data["last_name"],
        )
        professor, _ = ProfessorProfile.objects.update_or_create(
            user=professor_user,
            defaults={"employee_no": professor_data["employee_no"]},
        )
        professors.append(professor)

    return AccountSeedData(students=students, professors=professors)


def create_or_update_user(
    email: str,
    password: str,
    role: UserRole,
    first_name: str,
    last_name: str,
) -> User:
    user, _ = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "role": role,
        },
    )
    user.username = email
    user.role = role
    user.first_name = first_name
    user.last_name = last_name
    user.set_password(password)
    user.save()
    return user
