from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from academics.models import Course, Curriculum, CurriculumCourse, DegreeLevel, Enrollment

from .models import ProfessorProfile, User, UserRole


class AccountApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_student_registration(self):
        curriculum = Curriculum.objects.create(
            code="REG-BSC",
            name="Registration Curriculum",
            degree_level=DegreeLevel.BACHELOR,
            duration=4,
        )
        professor = User.objects.create_user(
            email="professor@example.com",
            password="StrongPassword123!",
            role=UserRole.PROFESSOR,
        )
        course = Course.objects.create(
            code="REG101",
            name="Registration Course",
            espb=6,
            professor=ProfessorProfile.objects.create(user=professor, employee_no="REG-P01"),
        )
        CurriculumCourse.objects.create(curriculum=curriculum, course=course, semester=1)

        response = self.client.post(
            reverse("student-registration"),
            {
                "email": "student@example.com",
                "password": "StrongPassword123!",
                "first_name": "New",
                "last_name": "Student",
                "index_no": "REG-001",
                "curriculum_code": curriculum.code,
            },
            format="json",
        )

        user = User.objects.get(email="student@example.com")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.student_profile.wallet.balance, 0)
        self.assertTrue(Enrollment.objects.filter(student=user.student_profile, course=course).exists())

    def test_token_login(self):
        User.objects.create_user(
            email="student@example.com",
            password="StrongPassword123!",
            role=UserRole.STUDENT,
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "student@example.com", "password": "StrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_current_user_requires_authentication(self):
        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_creates_course(self):
        admin = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            role=UserRole.ADMIN,
        )
        professor_user = User.objects.create_user(
            email="professor@example.com",
            password="StrongPassword123!",
            role=UserRole.PROFESSOR,
        )
        professor = ProfessorProfile.objects.create(user=professor_user, employee_no="ADMIN-P01")
        curriculum = Curriculum.objects.create(
            code="ADMIN-BSC",
            name="Admin Curriculum",
            degree_level=DegreeLevel.BACHELOR,
            duration=4,
        )
        self.client.force_authenticate(user=admin)

        response = self.client.post(
            reverse("admin-courses"),
            {
                "code": "ADMIN101",
                "name": "Administration",
                "espb": 6,
                "professor_id": professor.pk,
                "curriculum_code": curriculum.code,
                "semester": 1,
                "is_mandatory": True,
            },
            format="json",
        )

        course = Course.objects.get(code="ADMIN101")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CurriculumCourse.objects.filter(curriculum=curriculum, course=course).exists())
