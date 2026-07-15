from dataclasses import dataclass

from academics.management.test_data import (
    CURRICULUM_CODE,
    CURRICULUM_DURATION,
    CURRICULUM_NAME,
    SCHOOL_YEAR,
    TEST_COURSES,
)
from academics.models import Course, Curriculum, CurriculumCourse, DegreeLevel, Enrollment
from accounts.models import ProfessorProfile, StudentProfile


@dataclass
class AcademicSeedData:
    curriculum: Curriculum
    courses: list[Course]


def seed_academics(
    students: list[StudentProfile],
    professors: list[ProfessorProfile],
) -> AcademicSeedData:
    professors_by_email = {professor.user.email: professor for professor in professors}
    curriculum = create_or_update_curriculum(
        code=CURRICULUM_CODE,
        name=CURRICULUM_NAME,
        degree_level=DegreeLevel.BACHELOR,
        duration=CURRICULUM_DURATION,
    )
    courses = []

    for course_data in TEST_COURSES:
        course = create_or_update_course(
            code=course_data["code"],
            name=course_data["name"],
            espb=course_data["espb"],
            professor=professors_by_email[course_data["professor_email"]],
        )
        courses.append(course)

        CurriculumCourse.objects.update_or_create(
            curriculum=curriculum,
            course=course,
            school_year=SCHOOL_YEAR,
            defaults={
                "semester": course_data["semester"],
                "is_mandatory": course_data["is_mandatory"],
            },
        )

        for student in students:
            Enrollment.objects.update_or_create(
                student=student,
                course=course,
                school_year=SCHOOL_YEAR,
                defaults={"semester": course_data["semester"]},
            )

    return AcademicSeedData(curriculum=curriculum, courses=courses)


def create_or_update_course(
    code: str,
    name: str,
    espb: int,
    professor: ProfessorProfile,
) -> Course:
    course, _ = Course.objects.update_or_create(
        code=code,
        defaults={
            "name": name,
            "espb": espb,
            "professor": professor,
        },
    )
    return course


def create_or_update_curriculum(
    code: str,
    name: str,
    degree_level: DegreeLevel,
    duration: int,
) -> Curriculum:
    curriculum, _ = Curriculum.objects.update_or_create(
        code=code,
        defaults={
            "name": name,
            "degree_level": degree_level,
            "duration": duration,
        },
    )
    return curriculum
