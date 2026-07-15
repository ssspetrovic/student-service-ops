from dataclasses import dataclass

from accounts.management.test_data import TEST_PROFESSORS, TEST_STUDENTS
from accounts.models import ProfessorProfile, StudentProfile, User, UserRole


@dataclass
class AccountSeedData:
    students: list[StudentProfile]
    professors: list[ProfessorProfile]


def seed_accounts() -> AccountSeedData:
    students = []
    professors = []

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
