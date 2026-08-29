from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.generics import ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import Course, Curriculum, CurriculumCourse

from .models import ProfessorProfile, StudentProfile, User, UserRole
from .permissions import IsAdmin
from .services import provision_student_profile, update_student_profile


class AdminUserSerializer(serializers.ModelSerializer):
    index_no = serializers.CharField(source="student_profile.index_no", allow_null=True)
    current_year_of_study = serializers.IntegerField(
        source="student_profile.current_year_of_study", allow_null=True
    )
    curriculum_code = serializers.CharField(
        source="student_profile.curriculum.code", allow_null=True
    )
    employee_no = serializers.CharField(source="professor_profile.employee_no", allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "index_no",
            "current_year_of_study",
            "curriculum_code",
            "employee_no",
        ]


class AdminUserWriteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(choices=[UserRole.STUDENT, UserRole.PROFESSOR], required=False)
    index_no = serializers.CharField(max_length=30, required=False)
    curriculum_code = serializers.SlugRelatedField(
        slug_field="code", queryset=Curriculum.objects.all(), required=False
    )
    current_year_of_study = serializers.IntegerField(min_value=1, max_value=8, required=False)
    employee_no = serializers.CharField(max_length=20, required=False)

    def validate_email(self, value):
        value = User.objects.normalize_email(value)
        queryset = User.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_index_no(self, value):
        queryset = StudentProfile.objects.filter(index_no=value)
        if self.instance:
            queryset = queryset.exclude(user=self.instance)
        if queryset.exists():
            raise serializers.ValidationError("A student with this index number already exists.")
        return value

    def validate_employee_no(self, value):
        queryset = ProfessorProfile.objects.filter(employee_no=value)
        if self.instance:
            queryset = queryset.exclude(user=self.instance)
        if queryset.exists():
            raise serializers.ValidationError(
                "A professor with this employee number already exists."
            )
        return value

    def validate(self, attrs):
        if self.instance:
            self.validate_update(attrs)
            role = self.instance.role
        else:
            self.validate_create(attrs)
            role = attrs["role"]

        self.validate_profile_fields(attrs, role)
        return attrs

    def validate_create(self, attrs):
        for field in ("email", "password", "first_name", "last_name", "role"):
            if field not in attrs:
                raise serializers.ValidationError({field: "This field is required."})

        user = User(
            email=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        validate_password(attrs["password"], user=user)

    def validate_update(self, attrs):
        if self.instance.role == UserRole.ADMIN:
            raise serializers.ValidationError(
                "Administrator accounts are managed through Django admin."
            )

        if "role" in attrs:
            raise serializers.ValidationError({"role": "This field cannot be changed."})

        if "password" in attrs:
            raise serializers.ValidationError({"password": "This field cannot be changed."})

    def validate_profile_fields(self, attrs, role):
        if role == UserRole.STUDENT:
            if not self.instance:
                for field in ("index_no", "curriculum_code", "current_year_of_study"):
                    if field not in attrs:
                        raise serializers.ValidationError(
                            {field: "This field is required for students."}
                        )
            if "employee_no" in attrs:
                raise serializers.ValidationError(
                    {"employee_no": "Only professors have an employee number."}
                )
            return

        if role == UserRole.PROFESSOR:
            if not self.instance and "employee_no" not in attrs:
                raise serializers.ValidationError(
                    {"employee_no": "This field is required for professors."}
                )
            for field in ("index_no", "curriculum_code", "current_year_of_study"):
                if field in attrs:
                    raise serializers.ValidationError(
                        "Student profile fields are not valid for professors."
                    )

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data["role"]
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=role,
        )

        if role == UserRole.STUDENT:
            provision_student_profile(
                user=user,
                index_no=validated_data["index_no"],
                curriculum=validated_data["curriculum_code"],
                current_year_of_study=validated_data["current_year_of_study"],
            )
        else:
            ProfessorProfile.objects.create(
                user=user,
                employee_no=validated_data["employee_no"],
            )

        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        if instance.role == UserRole.STUDENT:
            profile_fields = ("index_no", "curriculum_code", "current_year_of_study")
            if any(field in validated_data for field in profile_fields):
                profile = getattr(instance, "student_profile", None)
                if profile is None:
                    raise serializers.ValidationError({"profile": "Student profile is missing."})
            if any(field in validated_data for field in profile_fields):
                update_student_profile(
                    profile,
                    index_no=validated_data.get("index_no"),
                    curriculum=validated_data.get("curriculum_code"),
                    current_year_of_study=validated_data.get("current_year_of_study"),
                )
        else:
            profile = getattr(instance, "professor_profile", None)
            if "employee_no" in validated_data:
                if profile is None:
                    raise serializers.ValidationError({"profile": "Professor profile is missing."})
                profile.employee_no = validated_data["employee_no"]
                profile.save()

        if "email" in validated_data:
            instance.email = validated_data["email"]
        if "first_name" in validated_data:
            instance.first_name = validated_data["first_name"]
        if "last_name" in validated_data:
            instance.last_name = validated_data["last_name"]
        instance.save()
        return instance


class AdminUserListCreateView(ListCreateAPIView):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.select_related(
            "student_profile__curriculum", "professor_profile"
        ).order_by("last_name", "first_name", "email")

    def get_serializer_class(self):
        return AdminUserSerializer if self.request.method == "GET" else AdminUserWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(AdminUserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserUpdateView(UpdateAPIView):
    queryset = User.objects.select_related("student_profile__curriculum", "professor_profile")
    serializer_class = AdminUserWriteSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return Response(AdminUserSerializer(self.get_object()).data, status=response.status_code)


class AdminUserDeactivateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.role == UserRole.ADMIN:
            return Response(
                {"detail": "Administrator accounts are managed through Django admin."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.is_active:
            return Response(
                {"detail": "Only active users can be deactivated."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.role == UserRole.PROFESSOR:
            professor = getattr(user, "professor_profile", None)
            if professor and (
                professor.courses.exists()
                or professor.exams.filter(
                    Q(date__gte=timezone.now()) | Q(registrations__status="active")
                ).exists()
            ):
                return Response(
                    {
                        "detail": (
                            "Reassign this professor's courses and pending exams deactivating the account."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(AdminUserSerializer(user).data)


class AdminCurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ["id", "code", "name", "degree_level", "duration"]


class AdminCurriculumListCreateView(ListCreateAPIView):
    queryset = Curriculum.objects.order_by("code")
    serializer_class = AdminCurriculumSerializer
    permission_classes = [IsAdmin]


class AdminProfessorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user_id")
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = ProfessorProfile
        fields = ["id", "email", "first_name", "last_name", "employee_no"]


class AdminProfessorListView(ListAPIView):
    queryset = (
        ProfessorProfile.objects.filter(user__is_active=True)
        .select_related("user")
        .order_by("user__last_name", "user__first_name")
    )
    serializer_class = AdminProfessorSerializer
    permission_classes = [IsAdmin]


class AdminCourseSerializer(serializers.ModelSerializer):
    professor_id = serializers.IntegerField(source="professor.user_id")
    professor_name = serializers.CharField(source="professor.user.get_full_name")
    professor_email = serializers.EmailField(source="professor.user.email")

    class Meta:
        model = Course
        fields = ["id", "code", "name", "espb", "professor_id", "professor_name", "professor_email"]


class AdminCourseUpdateSerializer(serializers.Serializer):
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfessorProfile.objects.filter(user__is_active=True), source="professor"
    )

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.professor = validated_data["professor"]
        instance.save(update_fields=["professor"])
        instance.exams.filter(
            Q(date__gte=timezone.now()) | Q(registrations__status="active")
        ).update(professor=instance.professor)
        return instance


class AdminCourseCreateSerializer(serializers.ModelSerializer):
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfessorProfile.objects.filter(user__is_active=True), source="professor"
    )
    curriculum_code = serializers.SlugRelatedField(
        slug_field="code", queryset=Curriculum.objects.all(), source="curriculum"
    )
    semester = serializers.IntegerField(min_value=1, max_value=12)
    is_mandatory = serializers.BooleanField(default=True)

    class Meta:
        model = Course
        fields = [
            "code",
            "name",
            "espb",
            "professor_id",
            "curriculum_code",
            "semester",
            "is_mandatory",
        ]

    @transaction.atomic
    def create(self, validated_data):
        curriculum = validated_data.pop("curriculum")
        semester = validated_data.pop("semester")
        is_mandatory = validated_data.pop("is_mandatory")
        course = Course.objects.create(**validated_data)
        CurriculumCourse.objects.create(
            curriculum=curriculum,
            course=course,
            semester=semester,
            is_mandatory=is_mandatory,
        )
        return course


class AdminCourseListView(ListCreateAPIView):
    queryset = Course.objects.select_related("professor__user").order_by("code")
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        return (
            AdminCourseSerializer if self.request.method == "GET" else AdminCourseCreateSerializer
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response(AdminCourseSerializer(course).data, status=status.HTTP_201_CREATED)


class AdminCourseUpdateView(UpdateAPIView):
    queryset = Course.objects.select_related("professor__user")
    serializer_class = AdminCourseUpdateSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return Response(AdminCourseSerializer(self.get_object()).data, status=response.status_code)
