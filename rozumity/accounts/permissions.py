
from rest_framework import permissions
from accounts.models import TherapyContract


class HasDiaryPermission(permissions.BasePermission):
    async def has_permission(self, request, view):
        email = request.user.email
        has_diary_perm = False
        async for contract in TherapyContract.objects.filter(client_email=email).filter(expert_email=email):
            if await contract.has_diary:
                has_diary_perm = True
                break
        return has_diary_perm


class HasAIPermission(permissions.BasePermission):
    async def has_permission(self, request, view):
        email = request.user.email
        has_ai_perm = False
        async for contract in TherapyContract.objects.filter(client_email=email).filter(expert_email=email):
            if await contract.has_ai:
                has_ai_perm = True
                break
        return has_ai_perm


class HasScreeningPermission(permissions.BasePermission):
    async def has_permission(self, request, view):
        email = request.user.email
        has_screening_perm = False
        async for contract in TherapyContract.objects.filter(client_email=email).filter(expert_email=email):
            if await contract.has_screening:
                has_screening_perm = True
                break
        return has_screening_perm


class HasDyagnosisPermission(permissions.BasePermission):
    async def has_permission(self, request, view):
        email = request.user.email
        has_dyagnosis_perm = False
        async for contract in TherapyContract.objects.filter(expert_email=email):
            if await contract.has_dyagnosis:
                has_dyagnosis_perm = True
                break
        return has_dyagnosis_perm
