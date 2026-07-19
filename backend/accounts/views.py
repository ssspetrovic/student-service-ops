from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProfessorProfile, StudentProfile
from .permissions import IsProfessor, IsStudent
from .serializers import (
    ProfessorProfileSerializer,
    StudentProfileSerializer,
    StudentRegistrationSerializer,
)


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


class StudentRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_serializer = StudentRegistrationSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        profile = request_serializer.save()
        return Response(
            StudentProfileSerializer(profile).data,
            status=status.HTTP_201_CREATED,
        )
