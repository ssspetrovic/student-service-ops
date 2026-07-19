from academics.models import Curriculum, DegreeLevel

from .models import StudentProfile


def create_student_profile(*, user, curriculum=None, **extra_fields):
    if curriculum is None:
        curriculum, _ = Curriculum.objects.get_or_create(
            code="TEST-CURRICULUM",
            defaults={
                "name": "Test Curriculum",
                "degree_level": DegreeLevel.BACHELOR,
                "duration": 4,
            },
        )
    return StudentProfile.objects.create(
        user=user,
        curriculum=curriculum,
        **extra_fields,
    )
