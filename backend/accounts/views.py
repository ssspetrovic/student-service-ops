from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView


from .models import ProfessorProfile, StudentProfile
from .permissions import IsProfessor, IsStudent
from .serializers import ProfessorProfileSerializer, StudentProfileSerializer


# Create your views here.
class StudentProfileView(RetrieveAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return get_object_or_404(StudentProfile, user=self.request.user)


class ProfessorProfileView(RetrieveAPIView):
    serializer_class = ProfessorProfileSerializer
    permission_classes = [IsProfessor]

    def get_object(self):
        return get_object_or_404(ProfessorProfile, user=self.request.user)
