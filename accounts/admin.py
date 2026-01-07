from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import *
from accounts.forms import CustomUserCreationForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def jwt_tokens(self, obj):
        refresh = RefreshToken.for_user(obj)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return (f"Access: \n{access_token}\n\n" f"Refresh: \n{refresh_token}")

    jwt_tokens.short_description = "JWT Tokens"

    add_form = CustomUserCreationForm

    list_display = ('id', 'email', 'date_joined', 'is_client', 'is_expert', 'is_staff', 'is_active')
    list_filter = ('date_joined', 'is_client', 'is_expert', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'jwt_tokens', 'is_client', 'is_expert', 'is_staff')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password', 'is_client', 'is_expert', 'is_staff')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    ordering = ('email',)
    readonly_fields = ('jwt_tokens',)
    search_fields = ('email', 'id')


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'country', 'gender')
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ('country', 'gender')


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'country', 'gender')
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ('country', 'gender')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'country', 'gender')
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ('country', 'gender')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    pass


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    pass


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    pass


@admin.register(TherapyContract)
class TherapyContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'expert', 'client_plan', 'expert_plan', 'contract_start_date')
    search_fields = ('client__user__email', 'expert__user__email')
    list_filter = ('client_plan', 'expert_plan')


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner_type', 'price',)
    search_fields = ('title',)
    list_filter = ('owner_type',)
