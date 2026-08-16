from django.contrib import admin
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from academics.models import Course, Curriculum, CurriculumCourse, DegreeLevel, Enrollment

from .admin import CustomUserAdmin
from .forms import ManagedUserCreationForm
from .models import ProfessorProfile, StudentProfile, User, UserRole


# Create your tests here.
class UserCreationTestCase(TestCase):
    def test_user_password_bcrypt(self):

        user = User.objects.create_user(
            email="user@example.com",
            password="user123",
        )

        self.assertNotEqual(user.password, "user123")
        self.assertTrue(user.check_password("user123"))
        self.assertFalse(user.check_password("bad-password"))
        self.assertTrue(user.password.startswith("bcrypt_sha256$"))


class ManagedUserAdminTestCase(TestCase):
    def test_admin_creates_professor(self):
        self.assertNotIn(
            UserRole.ADMIN,
            dict(ManagedUserCreationForm.base_fields["role"].choices),
        )
        form = ManagedUserCreationForm(
            data={
                "email": "admin-form-professor@example.com",
                "first_name": "Admin",
                "last_name": "Created",
                "role": UserRole.PROFESSOR,
                "password1": "StrongAccountPass123!",
                "password2": "StrongAccountPass123!",
                "employee_no": "ADMIN-FORM-P01",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        model_admin = CustomUserAdmin(User, admin.site)

        model_admin.save_model(None, form.save(commit=False), form, change=False)

        user = User.objects.get(email="admin-form-professor@example.com")
        self.assertEqual(user.role, UserRole.PROFESSOR)
        self.assertEqual(user.professor_profile.employee_no, "ADMIN-FORM-P01")


class CurrentUserApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_student_identity(self):
        user = User.objects.create_user(
            email="student@example.com",
            password="StrongPassword123!",
            first_name="Student",
            last_name="Example",
            role=UserRole.STUDENT,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": UserRole.STUDENT,
            },
        )

    def test_professor_identity(self):
        user = User.objects.create_user(
            email="professor@example.com",
            password="StrongPassword123!",
            first_name="Professor",
            last_name="Example",
            role=UserRole.PROFESSOR,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": UserRole.PROFESSOR,
            },
        )

    def test_admin_identity(self):
        user = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            first_name="Admin",
            last_name="Example",
            role=UserRole.ADMIN,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": UserRole.ADMIN,
            },
        )

    def test_unauthenticated_user_is_rejected(self):
        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentRegistrationApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.curriculum = Curriculum.objects.create(
            code="REG-BSC",
            name="Registration Curriculum",
            degree_level=DegreeLevel.BACHELOR,
            duration=4,
        )
        self.payload = {
            "email": "new-student@example.com",
            "password": "StrongRegistrationPass123!",
            "first_name": "New",
            "last_name": "Student",
            "index_no": "REG-001",
            "curriculum_code": self.curriculum.code,
        }

        professor = User.objects.create_user(
            email="registration-professor@example.com",
            password="StrongPassword123!",
            role=UserRole.PROFESSOR,
        )
        self.course = Course.objects.create(
            code="REG101",
            name="Registration Course",
            espb=6,
            professor=ProfessorProfile.objects.create(user=professor, employee_no="REG-P01"),
        )
        CurriculumCourse.objects.create(
            curriculum=self.curriculum,
            course=self.course,
            semester=1,
            is_mandatory=True,
        )

    def test_student_registration(self):
        payload = {
            **self.payload,
            "role": UserRole.ADMIN,
            "is_staff": True,
            "balance": "999.00",
            "current_year_of_study": 8,
        }
        response = self.client.post(reverse("student-registration"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "New")
        self.assertEqual(response.data["curriculum_code"], self.curriculum.code)
        user = User.objects.get(email=self.payload["email"])
        self.assertEqual(user.role, UserRole.STUDENT)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.student_profile.wallet.balance, 0)
        self.assertEqual(user.student_profile.current_year_of_study, 1)
        self.assertTrue(
            Enrollment.objects.filter(
                student=user.student_profile,
                course=self.course,
            ).exists()
        )
        self.client.force_authenticate(user=user)

        profile_response = self.client.get(reverse("student-profile"))

        self.assertEqual(profile_response.data["last_name"], "Student")
        self.assertEqual(profile_response.data["curriculum_name"], self.curriculum.name)


class AdministratorApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com", password="StrongPassword123!", role=UserRole.ADMIN
        )
        self.curriculum = Curriculum.objects.create(
            code="ADMIN-BSC", name="Admin Curriculum", degree_level=DegreeLevel.BACHELOR, duration=4
        )

    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)

    def test_non_admin_is_rejected(self):
        student = User.objects.create_user(
            email="student@example.com", password="StrongPassword123!", role=UserRole.STUDENT
        )
        self.client.force_authenticate(user=student)
        self.assertEqual(
            self.client.get(reverse("admin-users")).status_code, status.HTTP_403_FORBIDDEN
        )

    def test_admin_manages_users_curricula_and_courses(self):
        self.authenticate_admin()
        student_response = self.client.post(
            reverse("admin-users"),
            {
                "email": "new-student@example.com",
                "password": "StrongPassword123!",
                "first_name": "New",
                "last_name": "Student",
                "role": UserRole.STUDENT,
                "index_no": "ADMIN-001",
                "curriculum_code": self.curriculum.code,
                "current_year_of_study": 2,
            },
            format="json",
        )
        professor_response = self.client.post(
            reverse("admin-users"),
            {
                "email": "new-professor@example.com",
                "password": "StrongPassword123!",
                "first_name": "New",
                "last_name": "Professor",
                "role": UserRole.PROFESSOR,
                "employee_no": "ADMIN-P01",
            },
            format="json",
        )

        self.assertEqual(student_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(professor_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            StudentProfile.objects.get(index_no="ADMIN-001").curriculum, self.curriculum
        )
        self.assertEqual(
            ProfessorProfile.objects.get(employee_no="ADMIN-P01").user.role, UserRole.PROFESSOR
        )

        student = User.objects.get(email="new-student@example.com")

        update = self.client.patch(
            reverse("admin-user", kwargs={"pk": student.pk}),
            {
                "email": "updated@example.com",
                "first_name": "Updated",
                "current_year_of_study": 3,
            },
            format="json",
        )
        deactivate = self.client.post(
            reverse("admin-user-deactivate", kwargs={"pk": student.pk})
        )
        repeated_deactivate = self.client.post(
            reverse("admin-user-deactivate", kwargs={"pk": student.pk})
        )

        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(update.data["email"], "updated@example.com")
        self.assertEqual(update.data["first_name"], "Updated")
        self.assertEqual(update.data["current_year_of_study"], 3)
        self.assertEqual(deactivate.status_code, status.HTTP_200_OK)
        self.assertEqual(repeated_deactivate.status_code, status.HTTP_400_BAD_REQUEST)
        student.refresh_from_db()
        self.assertFalse(student.is_active)

        first_professor = ProfessorProfile.objects.get(employee_no="ADMIN-P01")
        course = Course.objects.create(
            code="ADMIN101",
            name="Administration",
            espb=6,
            professor=first_professor,
        )
        replacement_user = User.objects.create_user(
            email="replacement@example.com",
            password="StrongPassword123!",
            role=UserRole.PROFESSOR,
        )
        replacement_professor = ProfessorProfile.objects.create(
            user=replacement_user,
            employee_no="ADMIN-P03",
        )

        program_response = self.client.post(
            reverse("admin-programs"),
            {
                "code": "ADMIN-MSC",
                "name": "Admin Master",
                "degree_level": DegreeLevel.MASTER,
                "duration": 1,
            },
            format="json",
        )
        course_response = self.client.patch(
            reverse("admin-course", kwargs={"pk": course.pk}),
            {"professor_id": replacement_professor.pk},
            format="json",
        )

        self.assertEqual(program_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(course_response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.professor, replacement_professor)
