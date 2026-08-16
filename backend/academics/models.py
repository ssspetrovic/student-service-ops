from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models

from accounts.models import ProfessorProfile, StudentProfile

# Create your models here.

# null=False is default for char fields

school_year_validator = RegexValidator(
    regex=r"^\d{4}/\d{4}$", message="School year must use the YYYY/YYYY format."
)


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    espb = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)]
    )
    professor = models.ForeignKey(
        ProfessorProfile,
        on_delete=models.PROTECT,
        related_name="courses",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(espb__gte=1) & models.Q(espb__lte=60),
                name="course_espb_between_1_and_60",
            )
        ]

    def __str__(self):
        return f"{self.name} [{self.code}]"


class DegreeLevel(models.TextChoices):
    BACHELOR = "bachelor", "Bachelor"
    MASTER = "master", "Master"
    DOCTORAL = "doctoral", "Doctoral"


class Curriculum(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    degree_level = models.CharField(max_length=30, choices=DegreeLevel.choices)
    duration = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration__gte=1) & models.Q(duration__lte=6),
                name="curriculum_duration_between_1_and_6",
            )
        ]

    def __str__(self):
        return f"{self.name} [{self.code}]"


class CurriculumCourse(models.Model):
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="curriculum_courses",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="curriculum_courses",
    )
    semester = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["curriculum", "course"],
                name="uq_curriculum_course",
            ),
            models.CheckConstraint(
                condition=models.Q(semester__gte=1) & models.Q(semester__lte=12),
                name="curriculum_course_semester_between_1_and_12",
            ),
        ]

    def __str__(self):
        return f"{self.curriculum} - {self.course}"


class EnrollmentStatus(models.TextChoices):
    DROPPED = "dropped", "Dropped"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"


class Enrollment(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    school_year = models.CharField(max_length=9, validators=[school_year_validator])
    semester = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    status = models.CharField(
        max_length=40,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ACTIVE,
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "school_year"],
                name="uq_student_course_school_year",
            ),
            models.CheckConstraint(
                condition=models.Q(semester__gte=1) & models.Q(semester__lte=12),
                name="enrollment_semester_between_1_and_12",
            ),
        ]

    def __str__(self):
        return f"{self.student} - {self.course} ({self.school_year})"
