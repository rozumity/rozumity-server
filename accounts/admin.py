from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import (
    User, ClientProfile, ExpertProfile, StaffProfile, 
    TherapyContract, SubscriptionPlan
)
from rest_framework_simplejwt.tokens import RefreshToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    class CustomUserCreationForm(forms.ModelForm):
        email = forms.EmailField(label='E-Mail')
        password = forms.CharField(label='Password', widget=forms.PasswordInput)
        is_client = forms.BooleanField(label='Is Client', required=False)
        is_staff = forms.BooleanField(label='Is Staff', required=False)
        is_expert = forms.BooleanField(label='Is Expert', required=False)
        is_superuser = forms.BooleanField(label='Is Superuser', required=False)
        
        class Meta:
            model = get_user_model()
            fields = ('email', 'password', 'is_client', 'is_expert', 'is_superuser')

        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password"])
            if commit:
                user.save()

            return user

    def jwt_tokens(self, obj):
        refresh = RefreshToken.for_user(obj)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return (  
            f"Access: {str('\n'.join(
                access_token[i:i+100] for i 
                in range(0, len(access_token), 100
            )))}\n\n"
            f"Refresh: {str('\n'.join(
                refresh_token[i:i+100] for i 
                in range(0, len(refresh_token), 100
            )))}"
        )

    jwt_tokens.short_description = "JWT Tokens"
    add_form = CustomUserCreationForm

    list_display = ('email', 'date_joined', 'is_client', 'is_expert', 'is_staff', 'is_active')
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
    search_fields = ('email',)


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
