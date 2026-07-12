from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsStudent

from .models import Course, Curriculum, Enrollment
from .serializers import (
    CourseSerializer,
    CurriculumSerializer,
    EnrollmentSerializer,
)


# Create your views here.
class CourseListView(ListAPIView):
    queryset = Course.objects.select_related("professor__user").order_by("code")
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


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
