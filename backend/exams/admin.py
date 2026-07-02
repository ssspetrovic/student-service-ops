from django.contrib import admin

from .models import Exam, ExamRegistration

# Register your models here.
admin.site.register(Exam)
admin.site.register(ExamRegistration)
