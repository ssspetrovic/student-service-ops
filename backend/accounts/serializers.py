from rest_framework import serializers

from .models import StudentProfile, ProfessorProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    role = serializers.CharField(source="user.role")

    class Meta:
        model = StudentProfile
        fields = ["email", "role", "index_no", "current_year_of_study"]


class ProfessorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    role = serializers.CharField(source="user.role")

    class Meta:
        model = ProfessorProfile
        fields = ["email", "role", "employee_no"]
