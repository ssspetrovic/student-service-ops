from django.urls import path

from .views import (
    CourseListView,
    CurriculumListView,
    CurrentProfessorCourseListView,
    CurrentStudentCurriculumView,
    CurrentStudentEnrollmentListView,
)

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="courses"),
    path("my-courses/", CurrentProfessorCourseListView.as_view(), name="current-professor-courses"),
    path("curricula/", CurriculumListView.as_view(), name="curricula"),
    path(
        "enrollments/",
        CurrentStudentEnrollmentListView.as_view(),
        name="current-student-enrollments",
    ),
    path(
        "my-curriculum/",
        CurrentStudentCurriculumView.as_view(),
        name="current-student-curriculum",
    ),
]
