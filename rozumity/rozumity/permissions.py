
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


class IsUserEditPermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated, 
            request.method in ["PATCH", "PUT"]
        ))


class IsUserWritePermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated, 
            request.method == "POST"
        ))


class IsStaffReadPermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.user.is_staff,
            request.method == 'GET'
        ))


class AuthReadStaffWritePermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method == 'GET' or request.user.is_staff
        ))
