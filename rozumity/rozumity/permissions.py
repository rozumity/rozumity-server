
from rest_framework.permissions import BasePermission


class IsStaffPermission(BasePermission):
    async def has_permission(self, request, view):
        return request.user.is_staff


class IsUserReadPermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated, 
            request.method == 'GET'
        ))


class IsUserWritePermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated, 
            request.method == "POST"
        ))


class AuthReadStaffWritePermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method == 'GET' or request.user.is_staff
        ))
