from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import ProfessorProfile, StudentProfile
from accounts.permissions import IsProfessor, IsStudent


from .models import Exam, ExamRegistration
from .services import (
    AlreadyRegisteredError,
    ExamRegistrationCancellationClosedError,
    ExamRegistrationError,
    ExamRegistrationNotActiveError,
    ExamRegistrationOwnershipError,
    ExamRegistrationPaymentError,
    ExamRegistrationRefundError,
    RegistrationPeriodClosedError,
    StudentNotEnrolledError,
    cancel_exam_registration,
    register_student_for_exam,
)
from .serializers import (
    ExamRegistrationSerializer,
    ExamSerializer,
    ProfessorExamRegistrationSerializer,
)


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


class ProfessorExamRegistrationListView(ListAPIView):
    serializer_class = ProfessorExamRegistrationSerializer
    permission_classes = [IsProfessor]

    def get_queryset(self):
        professor = get_object_or_404(ProfessorProfile, user=self.request.user)
        exam = get_object_or_404(
            Exam,
            pk=self.kwargs["exam_id"],
            professor=professor,
        )

        return (
            ExamRegistration.objects.select_related("student__user", "exam__course")
            .filter(exam=exam)
            .order_by("student__index_no")
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
                {"detail": get_registration_error_detail(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ExamRegistrationSerializer(registration)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ExamRegistrationCancelView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, registration_id):
        student = get_object_or_404(StudentProfile, user=request.user)
        registration = get_object_or_404(
            ExamRegistration,
            pk=registration_id,
            student=student,
        )

        try:
            registration = cancel_exam_registration(
                student=student,
                registration=registration,
            )
        except ExamRegistrationError as e:
            return Response(
                {"detail": get_registration_error_detail(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ExamRegistrationSerializer(registration)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


def get_registration_error_detail(error: ExamRegistrationError) -> str:
    if isinstance(error, StudentNotEnrolledError):
        return "Student is not enrolled in this course."
    if isinstance(error, RegistrationPeriodClosedError):
        return "Registration period is not active."
    if isinstance(error, AlreadyRegisteredError):
        return "Student is already registered for this exam."
    if isinstance(error, ExamRegistrationPaymentError):
        return "Student does not have enough funds to register for this exam."
    if isinstance(error, ExamRegistrationCancellationClosedError):
        return "Registration can no longer be canceled."
    if isinstance(error, ExamRegistrationNotActiveError):
        return "Only active registrations can be canceled."
    if isinstance(error, ExamRegistrationOwnershipError):
        return "Registration does not belong to this student."
    if isinstance(error, ExamRegistrationRefundError):
        return "The original exam registration payment could not be found."
    return "Exam registration failed."
