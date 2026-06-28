from django.contrib import admin

from .models import Course, Curriculum, CurriculumCourse, Enrollment

# Register your models here.

admin.site.register(Course)
admin.site.register(Curriculum)
admin.site.register(CurriculumCourse)
admin.site.register(Enrollment)
