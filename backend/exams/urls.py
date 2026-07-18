from django.urls import path

from .views import CurrentStudentExamRegistrationListView, ExamListView, ExamRegistrationView

urlpatterns = [
    path("", ExamListView.as_view(), name="exams"),
    path(
        "registrations/",
        CurrentStudentExamRegistrationListView.as_view(),
        name="current-student-exam-registrations",
    ),
    path("<int:exam_id>/register/", ExamRegistrationView.as_view(), name="exam-registration"),
]
