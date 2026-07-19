from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from academics.models import Curriculum

from .models import ProfessorProfile, StudentProfile, User
from .services import create_student_account


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    role = serializers.CharField(source="user.role")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    curriculum_code = serializers.CharField(source="curriculum.code")
    curriculum_name = serializers.CharField(source="curriculum.name")

    class Meta:
        model = StudentProfile
        fields = [
            "email",
            "role",
            "first_name",
            "last_name",
            "index_no",
            "current_year_of_study",
            "curriculum_code",
            "curriculum_name",
        ]


class ProfessorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    role = serializers.CharField(source="user.role")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = ProfessorProfile
        fields = ["email", "role", "first_name", "last_name", "employee_no"]


class StudentRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_blank=False)
    index_no = serializers.CharField(max_length=30)
    current_year_of_study = serializers.IntegerField(min_value=1, max_value=8)
    curriculum_code = serializers.SlugRelatedField(
        slug_field="code",
        queryset=Curriculum.objects.all(),
    )

    def validate_email(self, value):
        value = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_index_no(self, value):
        if StudentProfile.objects.filter(index_no=value).exists():
            raise serializers.ValidationError("A student with this index number already exists.")
        return value

    def validate(self, attrs):
        user = User(
            email=attrs["email"],
            username=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        validate_password(attrs["password"], user=user)
        return attrs

    def create(self, validated_data):
        curriculum = validated_data.pop("curriculum_code")
        return create_student_account(curriculum=curriculum, **validated_data)
