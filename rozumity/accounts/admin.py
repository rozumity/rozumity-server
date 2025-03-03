from django.contrib import admin

from .models import User, ClientProfile, ExpertProfile, StaffProfile, University, Speciality


@admin.register(User)
class UniversityAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(StaffProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    pass

@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    pass
