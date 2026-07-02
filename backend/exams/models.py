from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from academics.models import Course
from accounts.models import ProfessorProfile, StudentProfile

# Create your models here.


class Exam(models.Model):
    # id will get autocreated
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="exams",
    )
    professor = models.ForeignKey(
        ProfessorProfile,
        on_delete=models.PROTECT,
        related_name="exams",
    )
    date = models.DateTimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.course.code} - {self.date:%d-%m-%Y %H:%M} [{self.room}]"


class ExamRegistrationStatus(models.TextChoices):
    CANCELED = "canceled", "Canceled"
    GRADED = "graded", "Graded"
    ACTIVE = "active", "Active"


class ExamRegistration(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.PROTECT,
        related_name="exam_registrations",
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.PROTECT,
        related_name="registrations",
    )
    grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(5), MaxValueValidator(10)],
    )
    status = models.CharField(
        max_length=20,
        choices=ExamRegistrationStatus.choices,
        default=ExamRegistrationStatus.ACTIVE,
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(grade__gte=5) & models.Q(grade__lte=10))
                | models.Q(grade__isnull=True),
                name="exam_registration_grade_between_5_and_10_or_null",
            )
        ]

    def __str__(self):
        return f"{self.exam.course.code} - {self.student} [{self.registered_at}]"
