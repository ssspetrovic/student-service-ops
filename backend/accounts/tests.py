from django.test import TestCase

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
