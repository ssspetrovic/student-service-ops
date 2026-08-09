from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.models import ProfessorProfile
from accounts.permissions import IsProfessor, IsStudent

from .models import Course, Curriculum, CurriculumCourse, Enrollment
from .serializers import (
    CourseSerializer,
    CurriculumSerializer,
    EnrollmentSerializer,
    StudentCurriculumSerializer,
)


# Create your views here.
class CourseListView(ListAPIView):
    queryset = Course.objects.select_related("professor__user").order_by("code")
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class CurrentProfessorCourseListView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsProfessor]

    def get_queryset(self):
        professor = get_object_or_404(ProfessorProfile, user=self.request.user)
        return Course.objects.select_related("professor__user").filter(
            professor=professor
        ).order_by("code")


class CurriculumListView(ListAPIView):
    queryset = Curriculum.objects.order_by("code")
    serializer_class = CurriculumSerializer
    permission_classes = [IsAuthenticated]


class CurrentStudentEnrollmentListView(ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return (
            Enrollment.objects.select_related("course", "student")
            .filter(student__user=self.request.user)
            .order_by("school_year", "semester", "course__code")
        )


class CurrentStudentCurriculumView(RetrieveAPIView):
    serializer_class = StudentCurriculumSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        curriculum_courses = CurriculumCourse.objects.select_related(
            "course__professor__user"
        ).order_by("semester", "course__code")
        return get_object_or_404(
            Curriculum.objects.prefetch_related(
                Prefetch("curriculum_courses", queryset=curriculum_courses)
            ),
            students__user=self.request.user,
        )
