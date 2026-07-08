from django.urls import path

from .views import ProfessorProfileView, StudentProfileView

urlpatterns = [
    path("student-profile/", StudentProfileView.as_view(), name="student-profile"),
    path("professor-profile/", ProfessorProfileView.as_view(), name="professor-profile"),
]
