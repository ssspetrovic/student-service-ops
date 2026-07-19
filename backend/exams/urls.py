from django.urls import path

from .views import (
    CurrentStudentExamRegistrationListView,
    ExamListView,
    ExamRegistrationCancelView,
    ExamRegistrationGradeView,
    ExamRegistrationView,
    ProfessorExamRegistrationListView,
)

urlpatterns = [
    path("", ExamListView.as_view(), name="exams"),
    path(
        "registrations/",
        CurrentStudentExamRegistrationListView.as_view(),
        name="current-student-exam-registrations",
    ),
    path(
        "<int:exam_id>/registrations/",
        ProfessorExamRegistrationListView.as_view(),
        name="professor-exam-registrations",
    ),
    path("<int:exam_id>/register/", ExamRegistrationView.as_view(), name="exam-registration"),
    path(
        "registrations/<int:registration_id>/cancel/",
        ExamRegistrationCancelView.as_view(),
        name="exam-registration-cancel",
    ),
    path(
        "registrations/<int:registration_id>/grade/",
        ExamRegistrationGradeView.as_view(),
        name="exam-registration-grade",
    ),
]
