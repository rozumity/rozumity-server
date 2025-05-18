from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission

from .models import (
    User, ClientProfile, ExpertProfile, StaffProfile, 
    TherapyContract, SubscriptionPlan
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'date_joined', 'is_client', 'is_expert', 'is_staff', 'is_active')
    list_filter = ('email', 'date_joined', 'is_client', 'is_expert', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('date_of_birth',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('date_of_birth',)}),
    )
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_client', 'is_expert', 'is_staff')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(Permission)
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename')
    search_fields = ('name', 'codename')
    list_filter = ('content_type',)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(TherapyContract)
class TherapyContractAdmin(admin.ModelAdmin):
    pass


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    pass
