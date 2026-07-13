from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsStudent


from .models import Exam, ExamRegistration
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
