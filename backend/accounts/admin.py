from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from finance.models import Wallet

from .forms import ManagedUserChangeForm, ManagedUserCreationForm
from .models import ProfessorProfile, StudentProfile, User, UserRole


# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    add_form = ManagedUserCreationForm
    form = ManagedUserChangeForm
    list_display = ("email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                    "index_no",
                    "current_year_of_study",
                    "curriculum",
                    "employee_no",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.username = obj.email
        super().save_model(request, obj, form, change)
        if not change and obj.role == UserRole.STUDENT:
            profile = StudentProfile.objects.create(
                user=obj,
                index_no=form.cleaned_data["index_no"],
                current_year_of_study=form.cleaned_data["current_year_of_study"],
                curriculum=form.cleaned_data["curriculum"],
            )
            Wallet.objects.create(student=profile)
        elif not change and obj.role == UserRole.PROFESSOR:
            ProfessorProfile.objects.create(
                user=obj,
                employee_no=form.cleaned_data["employee_no"],
            )


admin.site.register(StudentProfile)
admin.site.register(ProfessorProfile)
