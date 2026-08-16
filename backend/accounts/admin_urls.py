from django.urls import path

from .admin_api import (
    AdminCourseListView,
    AdminCourseUpdateView,
    AdminCurriculumListCreateView,
    AdminProfessorListView,
    AdminUserDeactivateView,
    AdminUserListCreateView,
    AdminUserUpdateView,
)

urlpatterns = [
    path("users/", AdminUserListCreateView.as_view(), name="admin-users"),
    path("users/<int:pk>/", AdminUserUpdateView.as_view(), name="admin-user"),
    path("users/<int:pk>/deactivate/", AdminUserDeactivateView.as_view(), name="admin-user-deactivate"),
    path("programs/", AdminCurriculumListCreateView.as_view(), name="admin-programs"),
    path("professors/", AdminProfessorListView.as_view(), name="admin-professors"),
    path("courses/", AdminCourseListView.as_view(), name="admin-courses"),
    path("courses/<int:pk>/", AdminCourseUpdateView.as_view(), name="admin-course"),
]
