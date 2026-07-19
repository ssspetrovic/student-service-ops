from django.contrib import admin
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from academics.models import Curriculum, DegreeLevel

from .admin import CustomUserAdmin
from .forms import ManagedUserCreationForm
from .models import User, UserRole


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

    def test_user_default_student_role(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="user123",
        )

        self.assertEqual(user.role, UserRole.STUDENT)

    def test_create_user_valid_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="user123")

    def test_user_username_defaults_to_email(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="user123",
        )

        self.assertEqual(user.username, user.email)


class SuperuserCreationTestCase(TestCase):
    def test_create_superuser_admin_role(self):
        superuser = User.objects.create_superuser(
            email="superuser@example.com",
            password="superuser123",
        )

        self.assertEqual(superuser.role, UserRole.ADMIN)

    def test_create_superuser_flags(self):
        superuser = User.objects.create_superuser(
            email="superuser@example.com",
            password="superuser123",
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_create_superuser_rejects_no_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superuser@example.com",
                password="superuser123",
                is_staff=False,
            )

    def test_create_superuser_rejects_no_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superuser@example.com",
                password="superuser123",
                is_superuser=False,
            )


class ManagedUserAdminTestCase(TestCase):
    def test_admin_form_creates_professor_without_offering_admin_role(self):
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
            "current_year_of_study": 1,
            "curriculum_code": self.curriculum.code,
        }

    def test_public_registration_creates_complete_student_account(self):
        payload = {
            **self.payload,
            "role": UserRole.ADMIN,
            "is_staff": True,
            "balance": "999.00",
        }
        response = self.client.post(reverse("student-registration"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "New")
        self.assertEqual(response.data["curriculum_code"], self.curriculum.code)
        user = User.objects.get(email=self.payload["email"])
        self.assertEqual(user.role, UserRole.STUDENT)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.student_profile.wallet.balance, 0)
        self.client.force_authenticate(user=user)

        profile_response = self.client.get(reverse("student-profile"))

        self.assertEqual(profile_response.data["last_name"], "Student")
        self.assertEqual(profile_response.data["curriculum_name"], self.curriculum.name)
