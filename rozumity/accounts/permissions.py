
from rest_framework import permissions
from rozumity.permissions import AuthReadStaffWritePermission
from accounts.models import TherapyContract


class HasDiaryPermission(AuthReadStaffWritePermission):
    async def has_permission(self, request, view):
        has_diary_perm = False
        user = request.user
        if user.is_anonymous:
            return
        email = user.email
        async for contract in TherapyContract.objects.filter(client_email=email).filter(expert_email=email):
            if await contract.has_diary:
                has_diary_perm = True
                break
        return has_diary_perm


class HasAIPermission(permissions.BasePermission):
    async def has_permission(self, request, view):
        has_ai_perm = False
        user = request.user
        if user.is_anonymous:
            return
        email = user.email
        async for contract in TherapyContract.objects.filter(client_email=email).filter(expert_email=email):
            if await contract.has_ai:
                has_ai_perm = True
                break
        return has_ai_perm


class HasScreeningPermission(permissions.BasePermission):
    async def has_permission(self, request, view):
        has_screening_perm = False
        user = request.user
        if user.is_anonymous:
            return
        email = user.email
        async for contract in TherapyContract.objects.filter(client_email=email).filter(expert_email=email):
            if await contract.has_screening:
                has_screening_perm = True
                break
        return has_screening_perm


class HasDyagnosisPermission(permissions.BasePermission):
    async def has_permission(self, request, view):
        has_dyagnosis_perm = False
        user = request.user
        if user.is_anonymous:
            return
        email = user.email
        async for contract in TherapyContract.objects.filter(client_email=email).filter(expert_email=email):
            if await contract.has_dyagnosis:
                has_dyagnosis_perm = True
                break
        return has_dyagnosis_perm


class IsContractSigner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.email in (obj.client_email, obj.expert_email)
