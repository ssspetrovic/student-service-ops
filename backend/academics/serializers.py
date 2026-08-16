from rest_framework import serializers

from .models import Course, Curriculum, CurriculumCourse, Enrollment


class CourseSerializer(serializers.ModelSerializer):
    professor_email = serializers.CharField(source="professor.user.email")
    professor_employee_no = serializers.CharField(source="professor.employee_no")

    class Meta:
        model = Course
        fields = ["code", "name", "espb", "professor_email", "professor_employee_no"]


class ProfessorCourseSerializer(CourseSerializer):
    semesters = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = [*CourseSerializer.Meta.fields, "semesters"]

    def get_semesters(self, course):
        return sorted({item.semester for item in course.curriculum_courses.all()})


class CurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ["code", "name", "degree_level", "duration"]


class StudentCurriculumCourseSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="course.code")
    name = serializers.CharField(source="course.name")
    espb = serializers.IntegerField(source="course.espb")
    professor_email = serializers.CharField(source="course.professor.user.email")

    class Meta:
        model = CurriculumCourse
        fields = [
            "code",
            "name",
            "espb",
            "professor_email",
            "semester",
            "is_mandatory",
        ]


class StudentCurriculumSerializer(serializers.ModelSerializer):
    courses = StudentCurriculumCourseSerializer(source="curriculum_courses", many=True)

    class Meta:
        model = Curriculum
        fields = ["code", "name", "degree_level", "duration", "courses"]


class CurriculumCourseSerializer(serializers.ModelSerializer):
    curriculum_code = serializers.CharField(source="curriculum.code")
    curriculum_name = serializers.CharField(source="curriculum.name")
    course_code = serializers.CharField(source="course.code")
    course_name = serializers.CharField(source="course.name")

    class Meta:
        model = CurriculumCourse
        fields = [
            "curriculum_code",
            "curriculum_name",
            "course_code",
            "course_name",
            "semester",
            "is_mandatory",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.code")
    course_name = serializers.CharField(source="course.name")
    course_espb = serializers.IntegerField(source="course.espb")
    student_index_no = serializers.CharField(source="student.index_no")

    class Meta:
        model = Enrollment
        fields = [
            "course_code",
            "course_name",
            "course_espb",
            "student_index_no",
            "school_year",
            "semester",
            "status",
            "enrolled_at",
        ]
