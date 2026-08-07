from django.urls import path

from .views import CurrentUserView, ProfessorProfileView, StudentProfileView

urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("student-profile/", StudentProfileView.as_view(), name="student-profile"),
    path("professor-profile/", ProfessorProfileView.as_view(), name="professor-profile"),
]
