from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from academics.models import Curriculum

from .models import ProfessorProfile, StudentProfile, User, UserRole


class ManagedUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    role = forms.ChoiceField(
        choices=[
            (UserRole.STUDENT, UserRole.STUDENT.label),
            (UserRole.PROFESSOR, UserRole.PROFESSOR.label),
        ]
    )
    index_no = forms.CharField(required=False)
    current_year_of_study = forms.IntegerField(required=False, min_value=1, max_value=8)
    curriculum = forms.ModelChoiceField(queryset=Curriculum.objects.all(), required=False)
    employee_no = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "role")

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        if role == UserRole.STUDENT:
            for name in ("index_no", "current_year_of_study", "curriculum"):
                if not cleaned_data.get(name):
                    self.add_error(name, "This field is required for students.")
            index_no = cleaned_data.get("index_no")
            if index_no and StudentProfile.objects.filter(index_no=index_no).exists():
                self.add_error("index_no", "A student with this index number already exists.")
        elif role == UserRole.PROFESSOR and not cleaned_data.get("employee_no"):
            self.add_error("employee_no", "This field is required for professors.")
        elif role == UserRole.PROFESSOR and ProfessorProfile.objects.filter(
            employee_no=cleaned_data["employee_no"]
        ).exists():
            self.add_error("employee_no", "A professor with this employee number already exists.")
        return cleaned_data


class ManagedUserChangeForm(UserChangeForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"

    def clean_role(self):
        role = self.cleaned_data["role"]
        if self.instance.pk and role != self.instance.role:
            raise forms.ValidationError("A user's role cannot be changed after creation.")
        return role
