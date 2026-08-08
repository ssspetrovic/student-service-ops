from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import ProfessorProfile, User, UserRole
from accounts.test_helpers import create_student_profile

from .models import Course, Curriculum, CurriculumCourse, DegreeLevel


class CurrentStudentCurriculumApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor_user = User.objects.create_user(
            email="professor@example.com",
            password="professor123",
            role=UserRole.PROFESSOR,
        )
        self.professor = ProfessorProfile.objects.create(
            user=self.professor_user,
            employee_no="PROF-001",
        )
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="student123",
            role=UserRole.STUDENT,
        )
        self.curriculum = Curriculum.objects.create(
            code="IE-BSC",
            name="Information Engineering",
            degree_level=DegreeLevel.BACHELOR,
            duration=4,
        )
        create_student_profile(
            user=self.student_user,
            index_no="STUDENT-001",
            curriculum=self.curriculum,
        )
        course = Course.objects.create(
            code="TEST01",
            name="Test Course",
            espb=5,
            professor=self.professor,
        )
        CurriculumCourse.objects.create(
            curriculum=self.curriculum,
            course=course,
            semester=1,
            school_year="2020/2021",
        )

    def test_student_receives_assigned_curriculum(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.get(reverse("current-student-curriculum"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "code": "IE-BSC",
                "name": "Information Engineering",
                "degree_level": DegreeLevel.BACHELOR,
                "duration": 4,
                "courses": [
                    {
                        "code": "TEST01",
                        "name": "Test Course",
                        "espb": 5,
                        "professor_email": "professor@example.com",
                        "semester": 1,
                        "is_mandatory": True,
                        "school_year": "2020/2021",
                    },
                ],
            },
        )

    def test_non_students_are_rejected(self):
        admin_user = User.objects.create_user(
            email="admin@example.com",
            password="admin123",
            role=UserRole.ADMIN,
        )
        url = reverse("current-student-curriculum")
        for user, expected_status in (
            (None, status.HTTP_401_UNAUTHORIZED),
            (self.professor_user, status.HTTP_403_FORBIDDEN),
            (admin_user, status.HTTP_403_FORBIDDEN),
        ):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.get(url).status_code, expected_status)
