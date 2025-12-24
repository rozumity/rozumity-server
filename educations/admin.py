from django.contrib import admin

from .models import (
    University, Speciality, Education
)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    pass


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    pass


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    pass