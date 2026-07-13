from django.urls import path

from .views import ExamListView, CurrentStudentExamRegistrationListView

urlpatterns = [
    path("", ExamListView.as_view(), name="exams"),
    path("registrations/", CurrentStudentExamRegistrationListView.as_view(), name="current-student-exam-registrations"),
]
