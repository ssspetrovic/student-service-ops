from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class UserRole(models.TextChoices):
    STUDENT = "student", _("Student")
    PROFESSOR = "professor", _("Professor")
    ADMIN = "admin", _("Admin")


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email address must be specified.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True set.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True set.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="student_profile",
    )
    index_no = models.CharField(max_length=30, unique=True)
    current_year_of_study = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
    )
    curriculum = models.ForeignKey(
        "academics.Curriculum",
        on_delete=models.PROTECT,
        related_name="students",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(current_year_of_study__gte=1)
                & models.Q(current_year_of_study__lte=8),
                name="student_current_year_of_study_between_1_and_8",
            )
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} [{self.index_no}]"


class ProfessorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="professor_profile",
    )

    employee_no = models.CharField(
        max_length=20,
        unique=True,
    )

    def __str__(self):
        return f"{self.user.get_full_name()} [{self.employee_no}]"
