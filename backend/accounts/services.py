from django.db import transaction

from academics.academic_year import current_school_year
from academics.models import Curriculum, Enrollment
from finance.models import Wallet

from .models import StudentProfile, User


def ensure_current_mandatory_enrollments(student: StudentProfile) -> None:
    first_semester = student.current_year_of_study * 2 - 1
    curriculum_courses = student.curriculum.curriculum_courses.filter(
        semester__in=(first_semester, first_semester + 1),
        is_mandatory=True,
    )
    school_year = current_school_year()

    for curriculum_course in curriculum_courses:
        Enrollment.objects.update_or_create(
            student=student,
            course=curriculum_course.course,
            school_year=school_year,
            defaults={"semester": curriculum_course.semester},
        )


@transaction.atomic
def provision_student_profile(
    *,
    user: User,
    index_no: str,
    current_year_of_study: int,
    curriculum: Curriculum,
) -> StudentProfile:
    student = StudentProfile.objects.create(
        user=user,
        index_no=index_no,
        current_year_of_study=current_year_of_study,
        curriculum=curriculum,
    )
    Wallet.objects.create(student=student)
    ensure_current_mandatory_enrollments(student)
    return student


@transaction.atomic
def update_student_profile(
    student: StudentProfile,
    *,
    index_no: str | None = None,
    current_year_of_study: int | None = None,
    curriculum: Curriculum | None = None,
) -> StudentProfile:
    changed_fields = []
    enrollment_context_changed = False

    if index_no is not None:
        student.index_no = index_no
        changed_fields.append("index_no")
    if current_year_of_study is not None:
        student.current_year_of_study = current_year_of_study
        changed_fields.append("current_year_of_study")
        enrollment_context_changed = True
    if curriculum is not None:
        student.curriculum = curriculum
        changed_fields.append("curriculum")
        enrollment_context_changed = True

    if changed_fields:
        student.full_clean()
        student.save(update_fields=changed_fields)
    if enrollment_context_changed:
        ensure_current_mandatory_enrollments(student)

    return student
