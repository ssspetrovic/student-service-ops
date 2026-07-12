from django.urls import path

from .views import CourseListView, CurriculumListView, CurrentStudentEnrollmentListView

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="courses"),
    path("curricula/", CurriculumListView.as_view(), name="curricula"),
    path(
        "enrollments/",
        CurrentStudentEnrollmentListView.as_view(),
        name="current-student-enrollments",
    ),
]
