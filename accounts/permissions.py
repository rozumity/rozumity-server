
from rest_framework import permissions

from accounts.models import TherapyContract
from accounts.utils import get_profile


class IsExpert(permissions.BasePermission):
    async def has_permission(self, request, view):
        if request.user.is_authenticated:
            profile = await get_profile(request)
            return "expert" in profile.__class__.__name__.lower()
        return False


class IsClient(permissions.BasePermission):
    async def has_permission(self, request, view):
        if request.user.is_authenticated:
            profile = await get_profile(request)
            return "client" in profile.__class__.__name__.lower()
        return False


class IsContractSigner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.email in (obj.client.pk, obj.expert_id)


class IsProfileOwnerWriteAuthRead(permissions.BasePermission):
    async def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == "GET":
            return True
        elif request.user.is_authenticated:
            return request.user.email == view.kwargs.get('pk')
        return False


class HasDiaryPermission(permissions.BasePermission):
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
