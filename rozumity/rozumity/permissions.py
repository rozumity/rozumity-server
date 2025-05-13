
from rest_framework.permissions import BasePermission


class StaffReadWritePermission(BasePermission):
    async def has_permission(self, request, view):
        return request.user and request.user.is_staff


class AuthReadStaffWritePermission(BasePermission):
    async def has_permission(self, request, view):
        return all((
            request.user.is_authenticated,
            request.method == 'GET' or request.user.is_staff
        ))
