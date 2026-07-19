from datetime import timedelta

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import ProfessorProfile, StudentProfile
from accounts.permissions import IsProfessor, IsStudent
from academics.models import Course, EnrollmentStatus
from finance.models import Wallet


from .models import Exam, ExamRegistration, ExamRegistrationStatus
from .services import (
    AlreadyRegisteredError,
    ExamGradingError,
    ExamNotFinishedError,
    ExamRegistrationCancellationClosedError,
    ExamRegistrationError,
    ExamRegistrationNotGradableError,
    ExamRegistrationNotActiveError,
    ExamRegistrationOwnershipError,
    ExamRegistrationPaymentError,
    ExamRegistrationRefundError,
    RegistrationPeriodClosedError,
    StudentNotEnrolledError,
    CANCELLATION_CLOSES_BEFORE_HOURS,
    REGISTRATION_CLOSES_BEFORE_DAYS,
    REGISTRATION_OPENS_BEFORE_DAYS,
    cancel_exam_registration,
    grade_exam_registration,
    register_student_for_exam,
)
from .serializers import (
    AvailableExamSerializer,
    ExamCreateSerializer,
    ExamRegistrationGradeSerializer,
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

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsProfessor()]
        return super().get_permissions()

    def post(self, request):
        professor = get_object_or_404(ProfessorProfile, user=request.user)
        serializer = ExamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(
            Course,
            code=serializer.validated_data["course_code"],
            professor=professor,
        )
        exam = Exam.objects.create(
            course=course,
            professor=professor,
            date=serializer.validated_data["date"],
            room=serializer.validated_data["room"],
        )

        return Response(ExamSerializer(exam).data, status=status.HTTP_201_CREATED)


class CurrentStudentExamRegistrationListView(ListAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return (
            ExamRegistration.objects.select_related("student", "exam__course")
            .filter(student__user=self.request.user)
            .order_by("-exam__date", "-pk")
        )


class CurrentStudentExamResultView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        results = (
            ExamRegistration.objects.select_related("student", "exam__course")
            .filter(
                student__user=request.user,
                status=ExamRegistrationStatus.GRADED,
                grade__isnull=False,
            )
            .order_by("-exam__date", "-pk")
        )
        average_grade = results.filter(grade__gte=6).aggregate(value=Avg("grade"))["value"]
        return Response(
            {
                "results": ExamRegistrationSerializer(results, many=True).data,
                "average": f"{average_grade:.2f}" if average_grade is not None else None,
            }
        )


class AvailableExamListView(ListAPIView):
    serializer_class = AvailableExamSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        student = get_object_or_404(StudentProfile, user=self.request.user)
        now = timezone.now()
        return (
            Exam.objects.select_related("course", "professor__user")
            .filter(
                course__enrollments__student=student,
                course__enrollments__status=EnrollmentStatus.ACTIVE,
                date__lte=now + timedelta(days=REGISTRATION_OPENS_BEFORE_DAYS),
                date__gt=now + timedelta(days=REGISTRATION_CLOSES_BEFORE_DAYS),
            )
            .exclude(registrations__student=student)
            .distinct()
            .order_by("date", "course__code")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        wallet = get_object_or_404(
            Wallet,
            student__user=self.request.user,
        )
        context["wallet_balance"] = wallet.balance
        return context


class CancellableExamRegistrationListView(ListAPIView):
    serializer_class = ExamRegistrationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return (
            ExamRegistration.objects.select_related("student", "exam__course")
            .filter(
                student__user=self.request.user,
                status=ExamRegistrationStatus.ACTIVE,
                exam__date__gt=timezone.now()
                + timedelta(hours=CANCELLATION_CLOSES_BEFORE_HOURS),
            )
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


class ExamRegistrationGradeView(APIView):
    permission_classes = [IsProfessor]

    def patch(self, request, registration_id):
        professor = get_object_or_404(ProfessorProfile, user=request.user)
        registration = get_object_or_404(
            ExamRegistration,
            pk=registration_id,
            exam__professor=professor,
        )
        grade_serializer = ExamRegistrationGradeSerializer(data=request.data)
        grade_serializer.is_valid(raise_exception=True)

        try:
            registration = grade_exam_registration(
                professor=professor,
                registration=registration,
                grade=grade_serializer.validated_data["grade"],
            )
        except ExamGradingError as error:
            return Response(
                {"detail": get_grading_error_detail(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProfessorExamRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


def get_grading_error_detail(error: ExamGradingError) -> str:
    if isinstance(error, ExamNotFinishedError):
        return "The exam has not finished yet."
    if isinstance(error, ExamRegistrationNotGradableError):
        return "Canceled registrations cannot be graded."
    return "Exam grading failed."
