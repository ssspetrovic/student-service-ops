from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from academics.models import Curriculum, Enrollment
from finance.models import Wallet

from .models import ProfessorProfile, StudentProfile, User, UserRole


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role"]


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

    @transaction.atomic
    def create(self, validated_data):
        curriculum = validated_data.pop("curriculum_code")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=UserRole.STUDENT,
        )
        profile = StudentProfile.objects.create(
            user=user,
            index_no=validated_data["index_no"],
            current_year_of_study=1,
            curriculum=curriculum,
        )
        first_semester_courses = curriculum.curriculum_courses.filter(
            semester=1,
            is_mandatory=True,
        ).order_by("-school_year")
        latest_course = first_semester_courses.first()

        if latest_course:
            for curriculum_course in first_semester_courses.filter(
                school_year=latest_course.school_year
            ):
                Enrollment.objects.create(
                    student=profile,
                    course=curriculum_course.course,
                    school_year=curriculum_course.school_year,
                    semester=curriculum_course.semester,
                )
        Wallet.objects.create(student=profile)
        return profile
