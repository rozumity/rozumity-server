import rules
from asgiref.sync import sync_to_async
from rest_framework.permissions import (
    BasePermission, IsAdminUser, IsAuthenticated, 
    IsAuthenticatedOrReadOnly
)


class IsAdminUserAsync(IsAdminUser):
    async def has_permission(self, request, view):
        return await sync_to_async(super().has_permission)(request, view)


class IsAuthenticatedAsync(IsAuthenticated):
    async def has_permission(self, request, view):
        return await sync_to_async(super().has_permission)(request, view)


class IsAuthenticatedOrReadOnlyAsync(IsAuthenticatedOrReadOnly):
    async def has_permission(self, request, view):
        return await sync_to_async(super().has_permission)(request, view)


class IsClient(BasePermission):
    async def has_permission(self, request, view):
        return rules.has_perm('is_client', request.user)


class IsExpert(BasePermission):
    async def has_permission(self, request, view):
        return rules.has_perm('is_expert', request.user)


class IsOwner(BasePermission):
    async def has_object_permission(self, request, view, obj):
        return rules.has_perm('is_owner', request.user, obj)
