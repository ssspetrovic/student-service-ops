from django.db import transaction

from finance.models import Wallet

from .models import StudentProfile, User, UserRole


@transaction.atomic
def create_student_account(
    *, email, password, first_name, last_name, index_no, current_year_of_study, curriculum
):
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.STUDENT,
    )
    profile = StudentProfile.objects.create(
        user=user,
        index_no=index_no,
        current_year_of_study=current_year_of_study,
        curriculum=curriculum,
    )
    Wallet.objects.create(student=profile)
    return profile
