from rest_framework import serializers

from .models import Exam, ExamRegistration


class ExamSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.code")
    course_name = serializers.CharField(source="course.name")
    professor_email = serializers.CharField(source="professor.user.email")
    professor_employee_no = serializers.CharField(source="professor.employee_no")

    class Meta:
        model = Exam
        fields = [
            "id",  # for targeting with register requests
            "date",
            "room",
            "course_code",
            "course_name",
            "professor_employee_no",
            "professor_email",
        ]


class ExamCreateSerializer(serializers.Serializer):
    course_code = serializers.CharField(max_length=20)
    date = serializers.DateTimeField()
    room = serializers.CharField(max_length=50, allow_blank=True, default="")


class ExamRegistrationSerializer(serializers.ModelSerializer):
    student_index_no = serializers.CharField(source="student.index_no")
    exam_id = serializers.IntegerField(source="exam.id")
    exam_course_code = serializers.CharField(source="exam.course.code")
    exam_course_name = serializers.CharField(source="exam.course.name")
    exam_date = serializers.DateTimeField(source="exam.date")
    exam_room = serializers.CharField(source="exam.room")

    class Meta:
        model = ExamRegistration
        fields = [
            "id",
            "student_index_no",
            "exam_id",
            "exam_course_code",
            "exam_course_name",
            "exam_date",
            "exam_room",
            "grade",
            "status",
            "registered_at",
        ]


class ProfessorExamRegistrationSerializer(ExamRegistrationSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta(ExamRegistrationSerializer.Meta):
        fields = [*ExamRegistrationSerializer.Meta.fields, "student_name"]

    def get_student_name(self, registration):
        return registration.student.user.get_full_name()


class ExamRegistrationGradeSerializer(serializers.Serializer):
    grade = serializers.IntegerField(min_value=5, max_value=10)
