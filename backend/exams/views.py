from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import StudentProfile
from accounts.permissions import IsStudent


from .models import Exam, ExamRegistration
from .services import ExamRegistrationError, register_student_for_exam
from .serializers import ExamSerializer, ExamRegistrationSerializer


# Create your views here.
class ExamListView(ListAPIView):
    queryset = Exam.objects.select_related("course", "professor__user").order_by(
        "date", "course__code"
    )
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class CurrentStudentExamRegistrationListView(ListAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [IsStudent]

    # get queryset for binding the registration to the user sending the requestd
    def get_queryset(self):
        return (
            ExamRegistration.objects.select_related("student", "exam__course")
            .filter(student__user=self.request.user)
            .order_by("exam__date", "exam__course__code")
        )


class ExamRegistrationView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, exam_id):
        student = get_object_or_404(StudentProfile, user=request.user)
        exam = get_object_or_404(Exam, id=exam_id)

        try:
            registration = register_student_for_exam(student=student, exam=exam)
        except ExamRegistrationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ExamRegistrationSerializer(registration)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
