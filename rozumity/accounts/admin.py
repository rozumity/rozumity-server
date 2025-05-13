from django.contrib import admin

from .models import (
    User, ClientProfile, ExpertProfile, StaffProfile, University, 
    Speciality, TherapyContract, SubscriptionPlan, Diary
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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


@admin.register(TherapyContract)
class TherapyContractAdmin(admin.ModelAdmin):
    pass


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    pass


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    pass
